# DGT (Dirección General de Tráfico) — Auditoría atómica de inteligencia de automoción

> **Slug:** `dgt` · **Subdominio (categoría cardeep):** `official-data`
> **Web auditada:** https://www.dgt.es/menusecundario/dgt-en-cifras/ (+ sede.dgt.gob.es, sedeapl.dgt.gob.es, nap.dgt.es, datos.gob.es)
> **Auditado:** 2026-06-30 · **Confianza global:** ALTA en identidad, catálogo de servicios y campos atómicos (extraídos de fuentes oficiales first-party: diseño de registro MATRABA en PDF, página de ayuda del Informe, fichas de microdatos, sede electrónica). MEDIA en algunos importes de tasa más allá de la 4.1 y en el detalle campo-a-campo del cuadro de mando del parque (descripción first-party, granularidad parcialmente inferida).
> **Convención:** cada afirmación va marcada `[VERIFICADO]` (leído en fuente oficial) o `[ASUMIDO]` (inferencia declarada). Nunca se presenta un asumido como verificado.

> **Nota de naturaleza (CRÍTICA):** DGT **NO es una empresa** ni un tasador comercial. Es el **organismo público autónomo del Estado español** que **opera el Registro de Vehículos** — la **fuente de verdad legal y autoritativa** de todo vehículo matriculado en España (titular, datos técnicos, cargas, ITV, bajas, transacciones). Para cardeep es la capa **`official-data`**: el suelo registral contra el que se validan matrícula, bastidor, ficha técnica, titularidad y eventos de compraventa. No tiene concepto de "punto de venta", concesionario, anuncio, precio ni huella digital — eso es justamente lo que cardeep aporta y DGT no. `[VERIFICADO]`

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre | **Dirección General de Tráfico (DGT)** | `[VERIFICADO]` |
| Naturaleza jurídica | **Organismo autónomo** del Gobierno de España | `[VERIFICADO]` Wikipedia + interior.gob.es |
| Adscripción | **Ministerio del Interior** (Subsecretaría del Interior) | `[VERIFICADO]` interior.gob.es |
| Creación | **Ley 47/1959, de 30 de julio** (nace como **Jefatura Central de Tráfico**, entonces Ministerio de la Gobernación) | `[VERIFICADO]` historia DGT + Wikipedia |
| Cargo de Director General | creado en **1967** (sustituye al Jefe Central de Tráfico); 14 directores hasta hoy | `[VERIFICADO]` |
| Director General actual | **Pere Navarro Olivella** (desde 2018) | `[VERIFICADO]` |
| HQ (Secretaría General) | **C/ Josefa Valcárcel, 44 — 28027 Madrid** | `[VERIFICADO]` cabecera del PDF oficial MATRABA |
| Webs | `dgt.es` (portal) · `sede.dgt.gob.es` (sede electrónica/trámites) · `sedeapl.dgt.gob.es` (portal estadístico/aplicaciones) · `nap.dgt.es` (Punto de Acceso Nacional) · `revista.dgt.es` | `[VERIFICADO]` |
| App | **miDGT** (app de **consulta**, NO de trámites: muestra permiso, puntos, vehículos, distintivo; no permite transferir) | `[VERIFICADO]` sede + gestoriamorey |
| Teléfono | **060** (atención) | `[VERIFICADO]` |
| Función nuclear (para cardeep) | **Titular y operador del Registro de Vehículos** de España: matriculación, transferencias, bajas, cargas, datos técnicos, ITV, distintivo ambiental | `[VERIFICADO]` |

**Cliente/usuario objetivo (verificado):** **ciudadanos** (consulta de su vehículo, distintivo, informes), **empresas del sector del automóvil y otros actores externos** (gestorías, concesionarios, aseguradoras, desguaces, plataformas de VO, fintech) vía **Informe Telemático en lote**, **otras Administraciones Públicas** (ayuntamientos, CCAA, diputaciones) vía **PID / MOVE / PADRÓN / ZBE / ARCI**, e **investigadores/reutilizadores** vía datos abiertos. `[VERIFICADO]`

---

## 2. Cobertura

- **País:** **España exclusivamente.** Es el registro nacional; no hay cobertura paneuropea. `[VERIFICADO]`
- **Scope vehículo:** **TODO el parque matriculado** — turismos, motocicletas, ciclomotores, camiones, furgonetas, autobuses, remolques/semirremolques, vehículos especiales, agrícolas, vehículos históricos. `[VERIFICADO]` (tablas COD_CLASE_MAT y COD_TIPO del MATRABA).
- **Nuevo + usado:** sí — el campo `IND_NUEVO_USADO` marca si el vehículo era **nuevo (N)** o **usado (U)** al momento de la matriculación; además se registra **toda transferencia** (compraventa de VO) y toda baja. `[VERIFICADO]`
- **Granularidad geográfica:** **nacional → autonómico (CCAA) → provincial → municipal** (código INE de municipio, código postal). `[VERIFICADO]` (cuadro de mando parque + campos `COD_MUNICIPIO_INE_VEH`, `CODIGO_POSTAL`, `COD_PROVINCIA_VEH`).
- **Profundidad temporal:** series históricas largas (Anuarios desde al menos 2019 en línea; microdatos diarios/mensuales/anuales; evolución histórica en los cuadros de mando). `[VERIFICADO]`
- **Propulsiones cubiertas (`COD_PROPULSION`):** Gasolina, Diésel, Eléctrico, Otros, Butano, Solar, GLP, GNC, GNL, Hidrógeno, Biometano, Etanol, Biodiésel. `[VERIFICADO]`
- **Categorías de vehículo eléctrico (`CATEGORIA_VEHICULO_ELECTRICO`):** **PHEV** (enchufable), **REEV** (autonomía extendida), **HEV** (híbrido), **BEV** (batería). `[VERIFICADO]`

---

## 3. Productos + campos atómicos

> DGT no vende "productos" comerciales; expone **servicios públicos** y **datasets**. Se documentan como productos a efectos de la auditoría. Los nombres de campo se conservan en el original (son nombres de dato oficiales).

### P1 — Informe de un Vehículo · *el "Carfax oficial" de España (per-vehículo)*
Informe oficial del Registro de Vehículos solicitable por matrícula/bastidor. **7 variantes.** `[VERIFICADO]` sede + dgt.es.
| Variante | Tasa | Contenido |
|---|---|---|
| **Reducido** | **Gratis** | Fecha de 1.ª matriculación en España + impedimentos a transferencia/circulación (incidencias). |
| **Completo** | **8,67 € (Tasa 4.1)** | Todo (ver campos abajo). |
| **Datos Técnicos** | 8,67 € | Identificación + ficha técnica + historial ITV + Euro NCAP. |
| **Cargas** | 8,67 € | Identificación + cargas/limitaciones de disposición. |
| **Vehículos a Mi Nombre** | 8,67 € | Vehículos en vigor a nombre del solicitante (solo titular/autorizado). |
| **Vehículos Sin Matricular** | **Gratis** | Certifica si un vehículo sin matricular consta en el registro. |
| **Titularidad de Vehículos** | 8,67 € | Confirma titularidad en rango de fechas (hasta 10 vehículos). |

**Campos atómicos del Informe Completo** (verbatim de la página de ayuda oficial): `[VERIFICADO]`
- **Datos del titular:** Filiación o razón social · identificación de cotitulares · indicador `Renting: SI`.
- **Identificación del vehículo:** Bastidor (VIN) · Marca · Modelo · Fecha de matriculación · Servicio de Renting · Municipio IVTM (domicilio fiscal).
- **Seguro Obligatorio:** Estado de aseguramiento · Nombre de compañía aseguradora.
- **Inspección Técnica (ITV):** Fecha de realización · Estación ITV · Defectos detectados · Plazos de caducidad ITV · Kilometraje (cuando la estación lo remitió) · Estado (`ITV favorable` / `desfavorable` / `caducada` / `negativa`).
- **Historial de bajas:** Motivo de baja · Período de baja · Situación actual (temporal/definitiva).
- **Historial de lecturas del cuentakilómetros:** Fecha de lectura · Origen (ITV / declaración voluntaria / talleres) · valor de kilometraje.
- **Indicador de vehículo con denegatoria** (incidencia denegatoria).
- **Cargas o gravámenes:** Embargo · Reserva de Dominio · Renting · Precinto · Leasing · Hipoteca Mobiliaria.
- **Información técnica:** Potencia · Combustible · Dimensiones · Masas máximas · Plazas.
- **Historial de titulares:** Número total de titulares · Fechas de titularidad · Tipo (persona física/jurídica).
- **Información medioambiental:** Combustible · Consumo (Wh/Km) · Categoría vehículo eléctrico · Autonomía eléctrica (Km).
- **Seguridad del vehículo:** Euro NCAP (rating estrellas).
- **Otros (citados en descripción del servicio):** Llamadas a revisión pendientes (recalls) · Mantenimiento (registro electrónico de talleres).
- **Nº de campos atómicos:** ~35.

### P2 — Informe Telemático de Vehículos (INTV) / Informes en lote · *acceso B2B programático*
Mismo catálogo de 7 informes, pero vía **Web Service** para "empresas del sector del automóvil y otros actores externos", con **consultas en lote automatizadas integradas en sus sistemas**. `[VERIFICADO]`
- **Acceso:** Web Service (Internet) con **certificado de clave pública** del dominio TRAFICO o SEDE; alta previa en el sistema. `[VERIFICADO]`
- **Salida:** **PDF** con el mismo formato que el informe del ciudadano. `[VERIFICADO]`
- **Requisito:** identificación del solicitante + declaración de **interés legítimo**. `[VERIFICADO]`
- **Tasa:** **4.1 = 8,67 €** por informe de pago, **prepago** (nº de tasa de 12 dígitos). Reducido gratis. `[VERIFICADO]`
- **Campos:** idénticos a P1 según variante.

### P3 — DGT en cifras · *portal estadístico público (agregado)*
Portal único de estadística (sustituye al antiguo portal estadístico cesado el 1-jul-2024). Temas: `[VERIFICADO]`
- **Vehículos:** {**Parque**, **Matriculaciones**, **Cambios de titularidad**, **Bajas**, **Distintivo ambiental**, **Movimientos**}.
- **Conductores:** permisos en vigor, censo de conductores (por CCAA/provincia/municipio, clase de permiso, antigüedad, sexo, edad), pruebas de aptitud.
- **Accidentes (siniestralidad):** datos diarios provisionales + anuales definitivos (accidentes con víctimas, fallecidos a 30 días, heridos hospitalizados/no hospitalizados), series históricas + microdatos.
- **Denuncias e ingresos (multas):** nº de denuncias, infracciones por exceso de velocidad, recaudación.
- **Información municipal:** **fichas informativas** por municipio (seguridad vial, conductores, parque, actividad sancionadora) por estratos de población/territorio.
- **Formatos:** **cuadros de mando interactivos** (dashboards), **Excel**, **PDF**, **HTML**, **TXT**, microdatos, y volcado al **Portal de Datos Abiertos del Gobierno** (datos.gob.es). `[VERIFICADO]`
- **Publicación insignia:** **Anuario Estadístico General** (anual; tablas de vehículos {matriculación, cambios de titularidad, procedencia, carburante, potencia, agrupaciones de carga, bajas por antigüedad/categoría, parque por tipo/población/carburante/provincia/antigüedad}, conductores y denuncias). `[VERIFICADO]`

### P4 — Microdatos MATRABA (Matriculaciones · Transferencias · Bajas) · *censo masivo per-vehículo* — **EL MÁS RICO EN CAMPOS**
Ficheros de censo del Registro de Vehículos en **ancho fijo (.txt en ZIP)**, **69 campos / 985 posiciones**, frecuencia **diaria y mensual** (matriculaciones) y censos análogos de transferencias y bajas (el mismo diseño cubre "matriculación, baja o transferencia"). `[VERIFICADO]` — diseño de registro PDF oficial `MATRICULACIONES_MATRABA.pdf`.

**Los 69 campos (verbatim del diseño de registro):** `[VERIFICADO]`
1. `FEC_MATRICULA` (fecha de matriculación) · 2. `COD_CLASE_MAT` (clase matrícula: ordinaria/turística/remolque/diplomática/reservada/especial/ciclomotor/transporte temporal/histórica) · 3. `FEC_TRAMITACION` · 4. `MARCA_ITV` · 5. `MODELO_ITV` · 6. `COD_PROCEDENCIA_ITV` (fabricación nacional/importación no UE/subasta/importación UE) · 7. `BASTIDOR_ITV` (8 primeros caracteres + `*` desde feb-2025) · 8. `COD_TIPO` (tipo de vehículo: camión, plataforma, caja… catálogo amplio) · 9. `COD_PROPULSION_ITV` (gasolina/diésel/eléctrico/GLP/GNC/GNL/H₂/biometano/etanol/biodiésel…) · 10. `CILINDRADA_ITV` · 11. `POTENCIA_ITV` (potencia fiscal en CVF) · 12. `TARA` · 13. `PESO_MAX` · 14. `NUM_PLAZAS` · 15. `IND_PRECINTO` (precintado SI/blanco) · 16. `IND_EMBARGO` (embargado SI/blanco) · 17. `NUM_TRANSMISIONES` · 18. `NUM_TITULARES` · 19. `LOCALIDAD_VEHICULO` · 20. `COD_PROVINCIA_VEH` (provincia de domicilio) · 21. `COD_PROVINCIA_MAT` (provincia de matriculación) · 22. `CLAVE_TRAMITE` · 23. `FEC_TRAMITE` · 24. `CODIGO_POSTAL` · 25. `FEC_PRIM_MATRICULACION` (1.ª matriculación) · 26. `IND_NUEVO_USADO` (N/U) · 27. `PERSONA_FISICA_JURIDICA` (D física / X jurídica) · 28. `CODIGO_ITV` · 29. `SERVICIO` (particular/público/taxi/alquiler c-s conductor/escuela/agrícola/obras/escolar/mercancías peligrosas) · 30. `COD_MUNICIPIO_INE_VEH` · 31. `MUNICIPIO` · 32. `KW_ITV` (potencia neta máx. en kW) · 33. `NUM_PLAZAS_MAX` · 34. `CO2_ITV` (emisiones CO₂) · 35. `RENTING` (S/N) · 36. `COD_TUTELA` (titular menor/tutela judicial) · 37. `COD_POSESION` (V venta / S subasta — herencias/compraventas) · 38. `IND_BAJA_DEF` (motivo baja definitiva: desguace/agotamiento/antigüedad/renovación/exportación/oficio abandono/oficio seguridad/tratamiento residual…) · 39. `IND_BAJA_TEMP` · 40. `IND_SUSTRACCION` (robado S/N) · 41. `BAJA_TELEMATICA` ("En desguace") · 42. `TIPO_ITV` · 43. `VARIANTE_ITV` · 44. `VERSION_ITV` · 45. `FABRICANTE_ITV` · 46. `MASA_ORDEN_MARCHA_ITV` · 47. `MASA_MAXIMA_TECNICA_ADMISIBLE_ITV` (MMTA) · 48. `CATEGORIA_HOMOLOGACION_EUROPEA_ITV` (M1/N1/L…) · 49. `CARROCERIA` · 50. `PLAZAS_PIE` · 51. `NIVEL_EMISIONES_EURO_ITV` (Euro 1-6…) · 52. `CONSUMO_WH/KM_ITV` (consumo energía eléctrica) · 53. `CLASIFICACION_REGLAMENTO_VEHICULOS_ITV` (Anexo II RD 2822) · 54. `CATEGORIA_VEHICULO_ELECTRICO` (PHEV/REEV/HEV/BEV) · 55. `AUTONOMIA_VEHICULO_ELECTRICO` · 56. `MARCA_VEHICULO_BASE` · 57. `FABRICANTE_VEHICULO_BASE` · 58. `TIPO_VEHICULO_BASE` · 59. `VARIANTE_VEHICULO_BASE` · 60. `VERSION_VEHICULO_BASE` · 61. `DISTANCIA_EJES_12_ITV` · 62. `VIA_ANTERIOR_ITV` (mm) · 63. `VIA_POSTERIOR_ITV` (mm) · 64. `TIPO_ALIMENTACION_ITV` (M mono / B bi / F flexicombustible) · 65. `CONTRASEÑA_HOMOLOGACION_ITV` · 66. `ECO_INNOVACION_ITV` · 67. `REDUCCION_ECO_ITV` · 68. `CODIGO_ECO_ITV` · 69. `FEC_PROCESO`.

> **Restricción crítica (feb-2025):** los ficheros MATRABA **ya no incluyen el bastidor completo** (`BASTIDOR_ITV` = 8 chars + `*`). El bastidor/VIN completo exige **solicitud con acreditación de interés legítimo** mediante formulario. `[VERIFICADO]`

### P5 — Microdatos del Parque de vehículos · *foto del parque circulante*
Ficheros ZIP del **parque activo** con frecuencia **mensual** (provisional; iniciado mar-2025) y **anual**. Diseño propio (`Interfaz-de-Salida-Fichero-Parque-Mensual.pdf` / `…-Anual.pdf`). `[VERIFICADO]`
- **Variables (descritas en la ficha):** tipo de vehículo · combustible/propulsión · potencia · año de matriculación · agrupación de plazas · cilindrada · provincia · **distintivo ambiental** · **categoría eléctrica** · titularidad. `[VERIFICADO descripción]` / `[ASUMIDO equivalencia campo-a-campo con MATRABA]`.

### P6 — Panel de datos del parque de vehículos · *cuadro de mando interactivo*
Dashboard interactivo del parque activo. Indicadores filtrables: **tipo de vehículo · propulsión/combustible · cilindrada · distintivo ambiental · antigüedad · categoría eléctrica · titularidad**, con desglose **nacional/autonómico/provincial/municipal** y **evolución histórica**. `[VERIFICADO]`

### P7 — Consulta del Distintivo Ambiental · *clasificación per-matrícula (gratis)*
Consulta por matrícula del distintivo medioambiental. Clasifica el **~50% más eficiente** del parque. Categorías: `[VERIFICADO]`
- **0 Emisiones** (BEV, REEV, PHEV con ≥40 km autonomía, pila de combustible) · **ECO** (híbridos, gas, o ambos) · **C** (gasolina/diésel con última normativa de emisiones) · **B** (gasolina/diésel normativa anterior) · (sin distintivo el resto).
- Salida: etiqueta correspondiente + colocación (ángulo inferior derecho del parabrisas). `[VERIFICADO]`

### P8 — Ficheros para Administraciones (MOVE · PADRÓN · ZBE · ARCI) · *descarga institucional*
`[VERIFICADO]`
- **MOVE (Movimientos):** matriculaciones, ciclomotores, rematriculaciones, matriculaciones temporales, prórrogas, **bajas**, **transferencias/cambios de titularidad**. Frecuencia **mensual**. Para ayuntamientos/diputaciones.
- **PADRÓN:** **censo completo de vehículos** de un municipio/diputación a una fecha. Frecuencia **semestral** (marzo y septiembre).
- **ZBE (Zonas de Bajas Emisiones):** listado **diario** con la **matrícula de TODOS los vehículos de España con derecho a distintivo ambiental** + su **clasificación** + datos de **domicilio**. Solo para municipios con ZBE en ordenanza, vía interfaz **DGT 3.0**.
- **ARCI:** guía codificada de infracciones (documento descargable).

### P9 — PID (Plataforma de Intermediación de Datos) · *verificación entre administraciones*
DGT cede información de **vehículos, conductores y sanciones** a otras Administraciones vía PID (no expone datos al público; es interoperabilidad administrativa). `[VERIFICADO]`

### P10 — DGT 3.0 · *plataforma de vehículo conectado / movilidad*
Plataforma de información de tráfico/movilidad en tiempo real. **API REST + colas MQTT** como métodos estándar de compartición/consumo. `[VERIFICADO]` Es infraestructura de seguridad vial conectada, no datos de mercado de VO.

### P11 — NAP (Punto de Acceso Nacional de Tráfico y Movilidad) · *datos abiertos de tráfico en tiempo real*
`nap.dgt.es` (Directiva 2010/40/UE). Datasets en **DATEX2 v3.7 / JSON / ROSATTE XML**: Incidencias, Cámaras, Paneles (tiempo real + localizaciones), **Radares fijos**, Tramos de elevado riesgo motos, Tramos INVIVE, TEFIVA (fauna), **Zonas de Bajas Emisiones (ZBE)**, Límites de velocidad, Conos conectados, posiciones de vehículos lentos, Mapa de Tráfico, Mapa de Movilidad. `[VERIFICADO]`
> Relevancia cardeep: **baja** (es tráfico/infraestructura, no vehículo/punto de venta), salvo el dataset **ZBE** que conecta con la capa medioambiental del parque.

---

## 4. Metodología y fuentes de datos

- **DGT ES la fuente primaria.** No agrega ni compra: **opera el Registro de Vehículos** por mandato legal (Ley 47/1959 y normativa de tráfico). Es la verdad registral. `[VERIFICADO]`
- **Alimentación del dato:**
  - Matriculación/transferencia/baja: grabadas en el propio registro (trámites en sede/oficinas/gestores). `[VERIFICADO]`
  - Datos técnicos (`*_ITV`, base): de la **tarjeta ITV / homologación** del vehículo. `[VERIFICADO por nomenclatura de campos]`
  - **ITV** (inspecciones, defectos, kilometraje): remitidos por las **estaciones ITV**. `[VERIFICADO]`
  - **Kilometraje:** ITV + **declaración voluntaria** + **talleres** (registro electrónico de mantenimiento). `[VERIFICADO]`
  - **Cargas/gravámenes:** embargo, reserva de dominio, precinto, leasing, hipoteca mobiliaria — anotadas en el registro por autoridades/financieras. `[VERIFICADO]`
  - **Seguro Obligatorio:** estado y compañía (interoperabilidad con el fichero de seguros). `[VERIFICADO existencia del dato]`
  - **Euro NCAP:** rating de Euro NCAP. `[VERIFICADO existencia]`
  - **Recalls (llamadas a revisión):** de los fabricantes. `[VERIFICADO existencia]`
  - **Distintivo ambiental:** calculado de los datos técnicos según clasificación (RD 2822/Anexo II + criterios de emisiones). `[VERIFICADO]`
- **Actualización:** matriculaciones **diaria** y mensual; parque **mensual** (provisional) y **anual**; ZBE **diaria**; MOVE **mensual**; PADRÓN **semestral**; informes per-vehículo **en tiempo real** bajo consulta. `[VERIFICADO]`
- **Privacidad:** datos personales del titular bajo RGPD — accesibles solo a partes con interés legítimo; bastidor restringido en microdatos desde feb-2025. `[VERIFICADO]`

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Sede electrónica** | `sede.dgt.gob.es` — informes per-vehículo, distintivo, transferencias; identificación **Cl@ve / certificado / DNIe** | `[VERIFICADO]` |
| **App miDGT** | consulta (permiso, puntos, vehículos, distintivo, informe reducido); **no trámites** | `[VERIFICADO]` |
| **PDF** | todos los informes per-vehículo se descargan en PDF | `[VERIFICADO]` |
| **Teléfono / presencial** | 060 / oficinas de Tráfico (cita previa) | `[VERIFICADO]` |
| **Web Service (INTV)** | informes en lote para empresas, integración en sistemas, certificado de clave pública | `[VERIFICADO]` |
| **Microdatos** | ZIP con `.txt` ancho fijo (MATRABA, parque) — descarga libre en DGT en cifras | `[VERIFICADO]` |
| **Cuadros de mando** | dashboards interactivos (parque, siniestralidad) | `[VERIFICADO]` |
| **Excel / HTML / TXT / PDF** | tablas estadísticas y anuarios | `[VERIFICADO]` |
| **Datos abiertos** | volcado a `datos.gob.es` (licencia `datos.gob.es/avisolegal`) | `[VERIFICADO]` |
| **Descarga institucional** | MOVE / PADRÓN / ZBE / ARCI (alta + permisos por oficina de Tráfico) | `[VERIFICADO]` |
| **PID** | interoperabilidad administración-administración | `[VERIFICADO]` |
| **DGT 3.0 / NAP** | API REST + MQTT / DATEX2 v3.7 / JSON / ROSATTE | `[VERIFICADO]` |

---

## 6. Precio (modelo)

- **No es modelo comercial: son TASAS públicas.** `[VERIFICADO]`
- **Tasa 4.1 = 8,67 €** por informe de pago (Completo, Datos Técnicos, Cargas, Vehículos a Mi Nombre, Titularidad). Prepago, nº de tasa de 12 dígitos. `[VERIFICADO]`
- **Gratuitos:** Informe **Reducido** y **Vehículos Sin Matricular**; consulta de **distintivo ambiental**; **microdatos** y estadística (datos abiertos). `[VERIFICADO]`
- **Administraciones / interoperabilidad (PID, MOVE, PADRÓN, ZBE):** sin coste comercial; requieren **alta + convenio/permisos**. `[VERIFICADO]`
- **Otras tasas de tráfico** (transferencia, matriculación, duplicados…) existen en el catálogo de tasas, pero quedan fuera del alcance "datos". `[VERIFICADO existencia]` / `[NO VERIFICADO importes concretos]`.
- **Conclusión:** acceso barato/gratuito al dato unitario y al agregado, pero **gobernado por tasa + interés legítimo + certificado**, no por suscripción SaaS.

---

## 7. Placement — DÓNDE se coloca cada dato (patrón a copiar/diferenciar por cardeep)

| Dato/métrica | Ubicación en UI/canal DGT | Estado |
|---|---|---|
| Historial per-vehículo (titulares, cargas, ITV, km, bajas, recalls, Euro NCAP) | **Informe de Vehículo** (PDF, secciones: Datos del titular · Identificación · Seguro · ITV · Bajas · Cuentakilómetros · Cargas · Técnica · Titulares · Medioambiental · Seguridad) | `[VERIFICADO]` |
| Impedimentos/incidencias rápidas + 1.ª matrícula | **Informe Reducido** (gratis, caja de matrícula en sede/miDGT) | `[VERIFICADO]` |
| Cargas/gravámenes aislados | **Informe de Cargas** (sección dedicada) | `[VERIFICADO]` |
| Distintivo ambiental | **Caja de consulta por matrícula** → etiqueta 0/ECO/C/B (sede + miDGT) | `[VERIFICADO]` |
| Parque agregado (tipo/combustible/distintivo/antigüedad/categoría eléctrica/titularidad × geo) | **Panel de datos del parque** (cuadro de mando interactivo, drill nacional→municipal) | `[VERIFICADO]` |
| Matriculaciones / transferencias / bajas unitarias | **Microdatos MATRABA** (ZIP/.txt ancho fijo, diario/mensual) | `[VERIFICADO]` |
| Censo municipal completo | **PADRÓN** (descarga semestral para administraciones) | `[VERIFICADO]` |
| Plate→distintivo→domicilio (todos los vehículos) | **Fichero ZBE** (diario, vía DGT 3.0, para municipios con ZBE) | `[VERIFICADO]` |
| Tablas/series y narrativa anual | **DGT en cifras** + **Anuario Estadístico General** (Excel/PDF/HTML) | `[VERIFICADO]` |
| Consulta programática per-vehículo | **INTV Web Service** (PDF idéntico al del ciudadano) | `[VERIFICADO]` |

**Patrón clave para cardeep:** (1) **separación nítida entre el plano per-vehículo** (Informe = ficha legal con secciones temáticas verticales: titular, cargas, ITV, km, técnica, medioambiental, seguridad) **y el plano agregado** (cuadro de mando del parque con drill geográfico + filtros por distintivo/combustible/antigüedad); (2) **caja de consulta por matrícula** como gancho universal (reducido gratis + distintivo), que cardeep puede replicar como "consulta tu coche"; (3) **microdato masivo en ancho fijo** como capa de descarga bulk; (4) cardeep **NO debe copiar** el modelo de acceso (tasa + interés legítimo + certificado) — su valor es justo lo contrario: abrir y enriquecer. **DGT aporta el esqueleto registral/técnico per-vehículo; cardeep aporta la capa comercial (punto de venta, anuncio, precio, huella digital) que DGT no tiene.**

---

## 8. Diferencial (lo que ofrece y nadie más puede)

1. **Fuente de verdad legal y autoritativa.** Es el **Registro de Vehículos**: ningún tasador, marketplace ni data house privado puede igualar la cobertura censal del 100% del parque español con validez jurídica. `[VERIFICADO]`
2. **Informe oficial de historial per-vehículo** (titulares con fechas, cargas/embargos/reserva de dominio/precinto/hipoteca, ITV con defectos y km, bajas, robo, recalls, Euro NCAP) — el "Carfax" **con valor legal**, no comercial. `[VERIFICADO]`
3. **Cargas y gravámenes** (embargo, reserva de dominio, leasing, hipoteca mobiliaria, precinto): información jurídicamente vinculante para una compraventa que **solo el registro tiene**. `[VERIFICADO]`
4. **Distintivo ambiental oficial** por matrícula, gratis — la autoridad que **define** la clasificación 0/ECO/C/B. `[VERIFICADO]`
5. **Censo masivo abierto** (MATRABA + parque, 69 campos, gratis) — el dataset registral más completo de España, reutilizable. `[VERIFICADO]`
6. **Censo de transacciones** (matriculación/transferencia/baja): cada **evento de compraventa** de VO queda registrado (`NUM_TRANSMISIONES`, `COD_POSESION`=venta/subasta, `IND_NUEVO_USADO`). `[VERIFICADO]`
7. **Fichero ZBE diario** que mapea **toda matrícula → distintivo → domicilio**. `[VERIFICADO]`
8. **Ficha técnica completa** desde homologación (categoría UE, Euro, masas, ejes, vías, alimentación, eco-innovación, vehículo base). `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece — y por qué cardeep existe)

1. **CERO concepto de "punto de venta"/concesionario/dealer.** No hay directorio de vendedores, ni web, ni `cdp_code`, ni huella digital. Es la ausencia que **define la razón de ser de cardeep**. `[VERIFICADO por ausencia total en todo el catálogo]`
2. **CERO valoración.** No hay valor residual %, retail/trade price, curva de depreciación, ajuste por km ni price-to-market. (Eso es GANVAM/Eurotax/Autovista.) `[VERIFICADO ausencia]`
3. **CERO inteligencia de mercado/liquidez.** No hay days-to-sell, market days supply, índice oferta/demanda, ni precio de anuncio. No es un marketplace ni un agregador de listings. `[VERIFICADO ausencia]`
4. **No hay precio de transacción real.** DGT registra el **evento** de transferencia, **no el importe** (el precio se declara a Hacienda vía ITP modelo 620/621, no a la DGT). `[VERIFICADO]`
5. **VIN/bastidor restringido** en microdatos desde feb-2025 (8 chars + `*`); el bastidor completo y los datos personales exigen **interés legítimo** + formulario. `[VERIFICADO]`
6. **Acceso burocrático, no SaaS.** Tasa 4.1 + certificado de clave pública + alta + convenio para administraciones; sin API pública self-serve de datos de vehículo, sin marketplace de datos. `[VERIFICADO]`
7. **Solo España.** Sin cobertura paneuropea. `[VERIFICADO]`
8. **Dato registral/administrativo, no comercial.** Refleja el estado legal del vehículo, no su atractivo de mercado ni su disponibilidad de venta. `[VERIFICADO]`
9. **Sin catálogo de equipamiento/trim comercial** tipo VIN-decoder de mercado (tiene ficha técnica de homologación, no opciones/packs comerciales). `[ASUMIDO fuerte]`

---

## 10. Fuentes (URLs)

**First-party DGT — portal y estadística**
- https://www.dgt.es/menusecundario/dgt-en-cifras/ (portal estadístico — temas, formatos, cuadros de mando)
- https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/?tema=vehiculos&pag=1&order=DESC (subcategorías vehículos: Parque/Matriculaciones/Cambios titularidad/Bajas/Distintivo/Movimientos)
- https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Microdatos-de-Matriculaciones-de-Vehiculos-diarios/ (MATRABA diario — ZIP, restricción bastidor feb-2025)
- https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Microdatos-de-parque-de-vehiculos-mensual/ (parque mensual — variables)
- https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Panel-de-datos-del-parque-de-vehiculos/ (cuadro de mando del parque — indicadores)
- **https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/matraba/MATRICULACIONES_MATRABA.pdf** (DISEÑO DE REGISTRO — **69 campos atómicos verbatim + tablas de código**, fuente del catálogo de campos)
- https://sedeapl.dgt.gob.es/IEST_INTER/pdfs/disenoRegistro/vehiculos/matriculaciones/MATRICULACIONES_MATRABA.pdf (espejo del diseño de registro)
- https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/parque-de-vehiculos/Interfaz-de-Salida-Fichero-Parque-Anual.pdf (diseño del fichero de parque anual)
- https://www.dgt.es/export/sites/web-DGT/.galleries/downloads/dgt-en-cifras/publicaciones/Anuario_Estadistico_General/Anuario-General-2025.pdf (Anuario Estadístico General — secciones vehículos/conductores/denuncias)

**First-party DGT — sede electrónica / servicios**
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/informe-de-un-vehiculo/ (7 variantes de informe + tasas + canales)
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/informe-de-un-vehiculo/ayuda-para-interpretar-el-informe-del-vehiculo/ (**campos atómicos del Informe Completo** — fuente)
- https://www.dgt.es/nuestros-servicios/tu-vehiculo/tus-vehiculos/informe-de-un-vehiculo/ (tipos de informe + tasa 4.1)
- https://sede.dgt.gob.es/es/vehiculos/tramites-para-empresas/informe-telematico-de-vehiculos/ (INTV Web Service — 8,67 €, certificado, interés legítimo, PDF)
- https://www.dgt.es/nuestros-servicios/para-colaboradores-y-empresas/otras-empresas-y-proveedores/informes-de-vehiculos-en-lote/ (informes en lote)
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/distintivo-ambiental/ (consulta distintivo 0/ECO/C/B)
- https://sede.dgt.gob.es/es/vehiculos/transferencias-de-vehiculos/ (transferencia/cambio de titularidad — evento de compraventa, plazo 30 días)
- https://www.dgt.es/nuestros-servicios/para-ayuntamientos-y-otras-administraciones/intermediacion-de-datos-y-descarga-de-ficheros/descarga-de-ficheros-move-padron-y-arci/ (MOVE/PADRÓN/ZBE/ARCI)
- https://sede.dgt.gob.es/es/otros-tramites/tramites-para-administraciones/plataforma-de-intermediacion-de-datos/ (PID)
- https://sede.dgt.gob.es/es/otros-tramites/compra-y-actualizacion-de-tasas/ + https://sedeclave.dgt.gob.es/WEB_Tasas7/jsp/tasas/catalogo.jspx (catálogo de tasas)

**First-party DGT — datos abiertos / movilidad**
- https://nap.dgt.es/dataset (Punto de Acceso Nacional — datasets DATEX2/JSON/ROSATTE)
- https://www.dgt.es/muevete-con-seguridad/tecnologia-e-innovacion-en-carretera/forma-parte-de-la-dgt-3.0/ (DGT 3.0 — API REST + MQTT)
- https://www.dgt.es/conoce-la-dgt/quienes-somos/historia/ (historia / Ley 47/1959)

**Terceros / verificación cruzada**
- https://es.wikipedia.org/wiki/Direcci%C3%B3n_General_de_Tr%C3%A1fico (naturaleza jurídica, creación 1959, adscripción Interior)
- https://www.interior.gob.es/.../direccion-general-de-trafico/ (organismo autónomo del Ministerio del Interior)
- https://datos.gob.es/es/catalogo/e00130502-microdatos-de-matriculaciones-de-vehiculos-diarios (ficha dataset: 69 campos / 985 posiciones / ancho fijo / licencia)
- https://datos.gob.es/en/blog/dgt-datasets-help-improve-traffic-and-road-safety (reutilización de datasets DGT)
- https://informevehiculo-dgt.es/solicitar/liquidacion-de-tasa-dgt-4-1/ + veritasgestion.com / motor.mapfre.es (tasa 4.1 = 8,67 €)

---

## 11. Resumen para schema

- **slug:** `dgt`
- **subdominio (cardeep):** `official-data`
- **naturaleza:** Organismo público autónomo (Ministerio del Interior) — **operador del Registro de Vehículos** de España. NO es empresa ni tasador.
- **productos:** 11 (Informe de Vehículo [7 variantes] · INTV/Informes en lote · DGT en cifras [+Anuario] · Microdatos MATRABA · Microdatos Parque · Panel del parque · Distintivo ambiental · Ficheros MOVE/PADRÓN/ZBE/ARCI · PID · DGT 3.0 · NAP).
- **diferencial central:** **fuente de verdad registral/legal** — historial per-vehículo oficial (titulares, **cargas/gravámenes**, ITV, km, recalls, Euro NCAP), censo masivo de parque y de transacciones (matriculación/transferencia/baja, 69 campos), distintivo ambiental oficial. Con validez jurídica que nadie privado puede replicar.
- **gap central para cardeep:** **CERO punto de venta / dealer / web / precio / valoración / liquidez de mercado.** DGT es el esqueleto registral-técnico per-vehículo; cardeep aporta la capa comercial y de huella digital que DGT no tiene. Además: VIN restringido (feb-2025), acceso por tasa+interés legítimo+certificado (no SaaS), solo España, sin precio de transacción real.
