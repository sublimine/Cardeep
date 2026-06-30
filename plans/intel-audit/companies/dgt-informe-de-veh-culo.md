# DGT — Informe de Vehículo — Auditoría atómica de inteligencia de automoción

> **Slug:** `dgt-informe-de-veh-culo` · **Subdominio (categoría cardeep):** `official-data`
> **Web:** https://www.dgt.es · **Sede electrónica:** https://sede.dgt.gob.es · **Datos:** https://www.dgt.es/menusecundario/dgt-en-cifras/
> **Auditado:** 2026-06-30 · **Confianza global:** ALTA en identidad/productos/campos/precio/entrega (todo en fuentes oficiales first-party) · ALTA en placement (sede + interpret pages + PDF de diseño de registro leído) · MEDIA en cifras de presupuesto/plantilla (vía Wikipedia, secundaria).
> **Convención:** cada afirmación va marcada `[VERIFICADO]` (leído en fuente) o `[ASUMIDO]` (inferencia declarada). Nunca se presenta un asumido como verificado. `[VERIFICADO ≥2]` = confirmado en dos o más fuentes.

> **NATURALEZA — leer primero.** DGT **NO es una empresa de datos privada**: es la **Dirección General de Tráfico**, organismo autónomo del **Ministerio del Interior** de España y **fuente de verdad registral** del vehículo en España (gestiona el **Registro de Vehículos**). El "producto de datos" auditado es el **Informe de un vehículo** (per-VIN/matrícula, 7 modalidades) más el **ecosistema de datos abiertos "DGT en cifras"** (microdatos de matriculaciones/transferencias/bajas + dashboards de parque + distintivo ambiental). Para cardeep, DGT es el **dato administrativo primario** del que beben GANVAM (INTEVES), DAT, aseguradoras, gestorías y todos los revendedores ("informevehiculo-dgt.es", coches.com 9,99€, etc.). No valora a mercado: **certifica estado administrativo, identidad técnica y trazabilidad oficial**. `[VERIFICADO]`

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre | **Dirección General de Tráfico (DGT)** — históricamente **Jefatura Central de Tráfico** | `[VERIFICADO ≥2]` dgt.es, Wikipedia |
| Naturaleza jurídica | **Organismo autónomo** (no sociedad mercantil) | `[VERIFICADO ≥2]` Wikipedia, interior.gob.es |
| Adscripción | **Ministerio del Interior** (Subsecretaría del Interior) | `[VERIFICADO ≥2]` |
| Creación | **Ley 47/1959, de 30 de julio**, sobre competencias en materia de tráfico | `[VERIFICADO ≥2]` dgt.es/historia, Wikipedia |
| HQ | **C/ Josefa Valcárcel, 44 — 28027 Madrid** | `[VERIFICADO ≥2]` Wikipedia + cabecera del PDF oficial de diseño de registro ("JOSEFA VALCÁRCEL, 44, 28027-MADRID") |
| Director General | **Pere Navarro Olivella** (desde 2018) | `[VERIFICADO]` Wikipedia |
| Plantilla | **12.244 empleados** (a 31-dic-2024) | `[VERIFICADO]` Wikipedia (secundaria) |
| Presupuesto | **≈979,9 M€** (2023) | `[VERIFICADO]` Wikipedia (secundaria) |
| Financiación | Multas (~374,3 M€ en 2019) + **tasas administrativas** (~686,2 M€ en 2019) → el Informe se cobra vía **tasa 4.1** | `[VERIFICADO]` Wikipedia + sede.dgt |
| Registros que gestiona | **Registro de Vehículos** + **Registro de Conductores e Infractores** | `[VERIFICADO ≥2]` Wikipedia, interior.gob.es |
| Código SIA del trámite | **202342** (Informe de un vehículo) | `[VERIFICADO]` sede.dgt |
| Marco normativo del dato | **Reglamento General de Vehículos** | `[VERIFICADO]` sede.dgt |

**Qué es (el producto):** servicio oficial que, a partir de **matrícula / nº de bastidor (VIN) / NIVE (nº ITV)**, emite un **informe PDF** del estado administrativo, técnico y de cargas de un vehículo matriculado en España, tomado **directamente del Registro de Vehículos**. Es el documento que el mercado usa como **due-diligence previa a una compraventa de VO** y como verificación de embargos/reserva de dominio/precinto. `[VERIFICADO ≥2]`

### Categorías de producto
1. **Informe de un vehículo (per-matrícula/VIN)** — 7 modalidades (núcleo de esta auditoría).
2. **Consulta gratuita del distintivo ambiental** (por matrícula, sin identificación).
3. **Consulta de datos de tus vehículos** (gratis, para el titular, en miDGT).
4. **DGT en cifras** — datos abiertos/estadística: microdatos (matriculaciones/transferencias/bajas), dashboards de parque, anuarios.
5. **Canales B2B/profesional:** Informe Telemático de Vehículos (INTV, web service), Informes de vehículos en lote.

### Cliente objetivo
**Particular** comprador/vendedor de VO · **gestorías y colaboradores** · **compraventas y concesionarios** · **empresas del sector** (renting, leasing, flotas) · **aseguradoras** · **peritos / abogados / tribunales** · **administraciones** · **desarrolladores/integradores** (INTV web service) · **revendedores** del informe (coches.com, portales "informe DGT"). `[VERIFICADO ≥2]`

---

## 2. Cobertura

| Dimensión | Detalle | Estado |
|---|---|---|
| País | **España exclusivamente** — autoridad registral nacional | `[VERIFICADO]` |
| Universo | **Todo el parque matriculado en España** (turismos, motos/ciclomotores, comerciales, industriales, autobuses, remolques, agrícolas/especiales) | `[VERIFICADO ≥2]` dgt-en-cifras, MATRABA |
| Scope nuevo/usado | **Ambos**. El microdato de matriculaciones marca `IND_NUEVO_USADO` (N nuevo / U usado al matricular). Informe cubre todo el ciclo de vida (alta→transferencias→bajas) | `[VERIFICADO]` MATRABA |
| Histórico | Trazabilidad desde **primera matriculación** del vehículo (`FEC_PRIM_MATRICULACION`); historial de titulares, ITV, km y bajas a lo largo de la vida del vehículo | `[VERIFICADO ≥2]` |
| Granularidad geográfica | **Provincia de matriculación, provincia de domicilio, municipio (código INE), localidad, código postal** | `[VERIFICADO]` MATRABA |
| Identificadores de entrada | **Matrícula**, **número de bastidor (VIN)**, **NIVE (nº ITV)** | `[VERIFICADO ≥2]` sede.dgt |
| Restricción de bastidor | Desde **1-feb-2025** los microdatos (MATRABA: matriculaciones/transferencias/bajas) **NO incluyen bastidor completo**; requiere demostrar interés legítimo vía formulario | `[VERIFICADO ≥2]` dgt-en-cifras, datos.gob.es |

---

## 3. Productos + campos atómicos

### 3.0 Las 7 modalidades del Informe de un vehículo (matriz)

| Modalidad | Precio | Quién | Canal teléfono | Núcleo |
|---|---|---|---|---|
| **Informe Reducido** | **Gratis** | cualquiera | NO | Estado semáforo (sin/avisos/incidencias) + fecha 1ª matriculación |
| **Informe Completo** | **8,67€** (tasa 4.1) | cualquiera | SÍ | Todo: titular + ITV + km + cargas + técnica + medioambiental + EuroNCAP + mantenimiento + recalls |
| **Informe Datos Técnicos** | **8,67€** | cualquiera | SÍ | Identificación + potencia/combustible/masas + ITV + EuroNCAP |
| **Informe de Cargas** | **8,67€** | cualquiera | SÍ | Solo cargas/limitaciones de disposición |
| **Informe Vehículos a Mi Nombre** | **8,67€** | solo titular/autorizado (REA) | NO | Vehículos activos a nombre del solicitante |
| **Informe Vehículos Sin Matricular** | **8,67€** | cualquiera | SÍ | Certifica si está matriculado en España |
| **Informe de Titularidad** | **8,67€** | cualquiera | SÍ | Si fue titular en un rango de fechas (máx. 10 vehículos) |

`[VERIFICADO ≥2]` sede.dgt (informe-de-un-vehiculo) + revista.dgt + dgt.es.

---

### 3.1 Informe Completo — el activo central (estructura real, por secciones)

> **Fuente de los labels exactos:** página oficial *"Ayuda para interpretar el Informe Completo de un vehículo"* (sede.dgt). Cita textual: *"El informe del vehículo está dividido en secciones. Si en su informe no aparece alguna de las secciones abajo indicadas significa que el vehículo no tiene ninguna anotación relativa a ella."* Es decir, **secciones condicionales**: solo aparecen si hay dato. `[VERIFICADO]`

**Sección 1 — Datos del Titular**
- `Filiación o razón social del titular`
- `Cotitulares` (identificación, si aplica)
- `Indicador Renting: SI` (si pertenece a empresa de renting)

**Sección 2 — Identificación del Vehículo**
- `Bastidor` (VIN)
- `Marca y modelo`
- `Fecha de matriculación`
- `Condición de renting`
- `Municipio donde se abona el IVTM` (Impuesto de Vehículos de Tracción Mecánica)

**Sección 3 — Datos sobre el Seguro Obligatorio**
- `Constancia de aseguramiento` (asegurado / no asegurado)
- `Nombre de la compañía aseguradora`

**Sección 4 — Inspección Técnica de Vehículos (ITV)** (historial completo)
- `Historial de inspecciones` (todas las ITV pasadas)
- `Fecha de realización` (de cada inspección)
- `Estación ITV` (responsable)
- `Defectos detectados`
- `Plazo de caducidad` / próxima ITV
- `Kilometraje reportado` (en la inspección)
- `Estado ITV`: valores → **favorable / desfavorable / caducada / negativa**

**Sección 5 — Historial de Bajas**
- `Situación actual` (baja temporal / baja definitiva)
- `Motivo de la baja`
- `Período de la baja`

**Sección 6 — Historial de Lecturas del Cuentakilómetros**
- `Fecha de lectura`
- `Lectura (km)`
- `Origen`: estaciones ITV / declaraciones voluntarias / talleres

**Sección 7 — Indicador Vehículo con Denegatoria**
- `Incidencia denegatoria` (restricciones pendientes de subsanar)

**Sección 8 — Cargas o Gravámenes** (tipos posibles)
- `Embargo` (autoridad judicial/administrativa)
- `Reserva de Dominio` (venta a plazos, propiedad condicionada)
- `Renting` (contrato de arrendamiento)
- `Precinto` (impedimento de circulación / inmovilización)
- `Leasing` (arrendamiento con opción de compra)
- `Hipoteca Mobiliaria` (garantía de crédito)

**Sección 9 — Información Técnica**
- `Potencia`
- `Combustible`
- `Dimensiones`
- `Masas máximas`
- `Número de plazas`

**Sección 10 — Historial de Titulares**
- `Número total de titulares`
- `Fechas de titularidad`
- `Tipo de titular`: persona física / persona jurídica

**Sección 11 — Información Medioambiental**
- `Combustible` (fuente de alimentación principal)
- `Consumo (Wh/km)`
- `Categoría de vehículo eléctrico`
- `Autonomía eléctrica (km)`

**Sección 12 — Seguridad del Vehículo**
- `Valoración Euro NCAP` (estrellas)

**Adicionales declarados por la sede para el Completo (no enumerados como sección propia en la página de interpretación, pero citados como contenido del Completo):**
- `Llamadas a revisión pendientes` (recalls de fabricante pendientes de subsanar) — `[VERIFICADO ≥2]` sede.dgt + revista.dgt
- `Historial de mantenimiento` (de talleres adscritos al servicio **"Libro Taller"** / libro de mantenimiento digital) — `[VERIFICADO]` sede.dgt
- `Estado de sustracción / robo` (vehículo denunciado como robado) — presente como dato del Registro (campo `IND_SUSTRACCION` en el microdato; citado por fuentes secundarias en el informe) — `[VERIFICADO]` MATRABA + km77/ro-des `[ASUMIDO]` su rotulado exacto en el PDF

> **Total atómico del Completo:** ~35-40 datos concretos distribuidos en 12 secciones condicionales + recalls + mantenimiento.

---

### 3.2 Informe Reducido (gratis) — semáforo de 3 estados

> Fuente: *"Ayuda para interpretar el Informe Reducido"* (sede.dgt). Devuelve **uno de tres estados** + fecha de 1ª matriculación. `[VERIFICADO]`

**Dato base:** `Fecha de primera matriculación en España`

**Estado 1 — Sin incidencias:** el vehículo puede circular y transferirse (recomienda Completo para ver embargos/precintos/concursales).

**Estado 2 — Con avisos** (impiden trámite/circulación):
- `El vehículo no está asegurado o el seguro está caducado`
- `ITV sin datos / caducada / negativa / desfavorable`
- `Llamadas a revisión pendientes de subsanar`

**Estado 3 — Con incidencias** (impedimentos graves a transferencia/circulación):
- `Falta de datos del titular`
- `Limitaciones de disposición`
- `Existencia de cotitulares, poseedor o arrendatarios`
- `Bajas sin finalizar` (excepto baja temporal por transferencia)
- `Incidencias denegatorias`
- `Embargos o precintos`
- `Impago del IVTM`
- `Tutela del titular`

---

### 3.3 Informe Datos Técnicos (8,67€)
- `Identificación básica del vehículo`
- `Potencia`
- `Combustible`
- `Masas máximas`
- `Historial de inspecciones ITV`
- `Resultado Euro NCAP`
`[VERIFICADO ≥2]` sede.dgt + revista.dgt

### 3.4 Informe de Cargas (8,67€)
- `Datos básicos de identificación del vehículo`
- `Cargas o limitaciones de disposición` (embargo / reserva de dominio / precinto / leasing / renting / hipoteca mobiliaria) que afecten a un cambio de titularidad
`[VERIFICADO ≥2]`

### 3.5 Informe Vehículos a Mi Nombre (8,67€) — solo titular/autorizado
- `Listado de vehículos activos a nombre del solicitante` (requiere ser titular o autorizado vía **REA — Registro de Apoderamientos**). `[VERIFICADO]`

### 3.6 Informe Vehículos Sin Matricular (8,67€)
- `Certificación de si el vehículo está matriculado en España`. `[VERIFICADO]`

### 3.7 Informe de Titularidad de Vehículos (8,67€)
- `Verificación de titularidad en un período concreto` (hasta **10 vehículos** por solicitud). `[VERIFICADO]`

---

### 3.8 Microdatos de Matriculaciones (fichero MATRABA) — el FEED atómico (69 campos)

> **Producto distinto del informe per-vehículo:** fichero masivo (diario + mensual) de **datos abiertos** con TODAS las altas del Registro y sus características técnicas. **Formato ancho fijo (.txt, posiciones fijas)**, publicado en ZIP. Es el dataset que cardeep podría **ingerir como feed primario del parque español**. Leído campo a campo del PDF oficial *"Documento de interfaz de Envío de Datos (Matriculaciones)"* (sedeapl.dgt.gob.es). `[VERIFICADO — PDF leído]`

> Hay ficheros hermanos con su propio diseño: **Transferencias** (cambios de titularidad) y **Bajas**, además del de Matriculaciones aquí transcrito.

**Lista completa de los 69 campos (nombre · descripción):**
1. `FEC_MATRICULA` — Fecha de matriculación (DDMMYYYY)
2. `COD_CLASE_MAT` — Código de clase de matrícula
3. `FEC_TRAMITACION` — Fecha de tramitación
4. `MARCA_ITV` — Marca del vehículo (CHAR 30)
5. `MODELO_ITV` — Modelo del vehículo (CHAR 22)
6. `COD_PROCEDENCIA_ITV` — Código de procedencia
7. `BASTIDOR_ITV` — Número de bastidor / VIN (CHAR 21) *[restringido desde 2025]*
8. `COD_TIPO` — Código del tipo de vehículo
9. `COD_PROPULSION_ITV` — Código del tipo de propulsión
10. `CILINDRADA_ITV` — Cilindrada (cc)
11. `POTENCIA_ITV` — Potencia fiscal (CVF)
12. `TARA` — Tara (peso del vehículo)
13. `PESO_MAX` — Peso máximo
14. `NUM_PLAZAS` — Número de plazas
15. `IND_PRECINTO` — Indicador de vehículo precintado (SI/blanco)
16. `IND_EMBARGO` — Indicador de vehículo embargado (SI/blanco)
17. `NUM_TRANSMISIONES` — Número de transmisiones (cambios de titularidad)
18. `NUM_TITULARES` — Número de titulares
19. `LOCALIDAD_VEHICULO` — Localidad del domicilio del vehículo
20. `COD_PROVINCIA_VEH` — Código de provincia de domicilio
21. `COD_PROVINCIA_MAT` — Código de provincia de matriculación
22. `CLAVE_TRAMITE` — Código del trámite
23. `FEC_TRAMITE` — Fecha del trámite
24. `CODIGO_POSTAL` — Código postal del domicilio
25. `FEC_PRIM_MATRICULACION` — Fecha de primera matriculación
26. `IND_NUEVO_USADO` — Nuevo (N) o usado (U) al matricular
27. `PERSONA_FISICA_JURIDICA` — Física (D) / Jurídica (X)
28. `CODIGO_ITV` — Código ITV
29. `SERVICIO` — Código de servicio del vehículo
30. `COD_MUNICIPIO_INE_VEH` — Código INE del municipio
31. `MUNICIPIO` — Nombre del municipio
32. `KW_ITV` — Potencia neta máxima (kW)
33. `NUM_PLAZAS_MAX` — Número de plazas máximo (vehículo cargado)
34. `CO2_ITV` — Emisiones de CO2
35. `RENTING` — Vehículo de renting (S/N)
36. `COD_TUTELA` — Titular menor de edad / tutela judicial (S/N)
37. `COD_POSESION` — Tipo de posesión (V=Venta / S=Subasta)
38. `IND_BAJA_DEF` — Indicador de baja definitiva
39. `IND_BAJA_TEMP` — Indicador de baja temporal (S/N)
40. `IND_SUSTRACCION` — Indicador de vehículo robado (S/N)
41. `BAJA_TELEMATICA` — "En desguace" / blanco
42. `TIPO_ITV` — Tipo del vehículo
43. `VARIANTE_ITV` — Variante del vehículo
44. `VERSION_ITV` — Versión del vehículo
45. `FABRICANTE_ITV` — Fabricante del vehículo completo/completado
46. `MASA_ORDEN_MARCHA_ITV` — Masa en orden de marcha
47. `MASA_MAXIMA_TECNICA_ADMISIBLE_ITV` — Masa máxima técnicamente admisible (MMTA)
48. `CATEGORIA_HOMOLOGACION_EUROPEA_ITV` — Categoría de homologación UE (M1, N1…)
49. `CARROCERIA` — Carrocería del vehículo
50. `PLAZAS_PIE` — Número de plazas de pie
51. `NIVEL_EMISIONES_EURO_ITV` — Nivel de emisiones EURO (Euro 1-6)
52. `CONSUMO_WH/KM_ITV` — Consumo de energía eléctrica (Wh/km)
53. `CLASIFICACION_REGLAMENTO_VEHICULOS_ITV` — Clasificación Anexo II RD 2822/1998
54. `CATEGORIA_VEHICULO_ELECTRICO` — Categoría de vehículo eléctrico (BEV/PHEV/…)
55. `AUTONOMIA_VEHICULO_ELECTRICO` — Autonomía eléctrica (km)
56. `MARCA_VEHICULO_BASE` — Marca del vehículo base
57. `FABRICANTE_VEHICULO_BASE` — Fabricante del vehículo base
58. `TIPO_VEHICULO_BASE` — Tipo del vehículo base
59. `VARIANTE_VEHICULO_BASE` — Variante del vehículo base
60. `VERSION_VEHICULO_BASE` — Versión del vehículo base
61. `DISTANCIA_EJES_12_ITV` — Distancia entre ejes 1-2 (mm)
62. `VIA_ANTERIOR_ITV` — Vía anterior (mm)
63. `VIA_POSTERIOR_ITV` — Vía posterior (mm)
64. `TIPO_ALIMENTACION_ITV` — Monocombustible (M) / Bicombustible (B) / Flexicombustible (F)
65. `CONTRASEÑA_HOMOLOGACION_ITV` — Contraseña de homologación
66. `ECO_INNOVACION_ITV` — Eco-innovación (S/N)
67. `REDUCCION_ECO_ITV` — Reducción eco (pendiente de definir por UE)
68. `CODIGO_ECO_ITV` — Código eco (pendiente de definir por UE)
69. `FEC_PROCESO` — Fecha de grabación del proceso (matriculación/baja/transferencia)

> **Anexos de códigos del fichero** (tablas de decodificación incluidas en el mismo PDF): `COD_CLASE_MAT`, `COD_PROCEDENCIA`, `COD_SERVICIO`, `COD_TIPO`, `COD_PROPULSION`, `COD_PROVINCIA_VEH`, `COD_PROVINCIA_MAT`, `CLAVE_TRAMITE`, `SERVICIO`, `IND_BAJA_DEF`, `CATEGORIA_VEHICULO_ELECTRICO`. `[VERIFICADO]`

---

### 3.9 Dashboard "Parque de Vehículos" (DGT en cifras) — indicadores agregados
Panel interactivo del parque activo español. Indicadores: `tipo de vehículo` · `propulsión/combustible` · `cilindrada` · `distintivo ambiental` · `antigüedad` · `categoría eléctrica` · `tipo de titularidad (física/jurídica)` · `evolución histórica`. `[VERIFICADO]` dgt-en-cifras

**Otros datasets de "DGT en cifras"** (cada uno descargable / dashboard):
- `Matriculaciones definitivas` (características técnicas)
- `Cambios de titularidad / transferencias` (por tipo de vehículo)
- `Bajas` (vehículos retirados + características)
- `Distintivo Ambiental` (dataset descargable de matrícula→etiqueta)
- `Permisos de conducción` y `Censo de conductores` (por CCAA/provincia/municipio)
- `Siniestralidad` (diaria provisional, anual, series históricas, microdatos)
- `Denuncias e ingresos` (nº denuncias, importes, exceso de velocidad)
- `Información municipal` (fichas por municipio: siniestralidad, conductores, parque, sanción)
- `Anuario Estadístico General` (PDF)
`[VERIFICADO ≥2]` dgt-en-cifras

---

### 3.10 Consulta del Distintivo Ambiental (gratis, por matrícula, sin identificación)
**Input:** matrícula → **Output:** clasificación ambiental o motivo de no-elegibilidad.
**Clasificaciones (4 categorías + sin distintivo):**
- `Etiqueta 0 (Azul)` — BEV / autonomía extendida (REEV) / PHEV ≥40 km / pila de combustible
- `Etiqueta ECO` — PHEV <40 km, híbridos no enchufables, GNC/GNL, GLP
- `Etiqueta C (Verde)` — gasolina desde 2006, diésel desde 2015
- `Etiqueta B (Amarilla)` — gasolina desde 2001, diésel desde 2006
- `Sin distintivo` — el 50% más contaminante
**Coste:** consulta **gratis**; **emisión de la pegatina física = 5€**. **Descarga masiva** disponible: fichero con todas las matrículas y sus distintivos (sin identificación). `[VERIFICADO ≥2]` sede.dgt + dgt.es

---

### 3.11 Consulta de datos de tus vehículos (gratis, titular, en miDGT)
Panel privado para el **titular** (login en miDGT / sede). Campos:
- `Matrícula`, `Número de bastidor`, `NIVE`
- `Cilindrada`, `Carburante`, `Distintivo ambiental`
- `Seguro: compañía + fecha de alta`
- `Caducidad de la ITV`, `Kilómetros de la última inspección`
- `Conductor habitual designado` (consulta + comunicación de alternativo)
- `Dirección fiscal del vehículo` (consulta + actualización para IVTM)
- `Tarjeta electrónica ITV` (descarga de copia, no válida para circular)
`[VERIFICADO]` dgt.es/consulta-los-datos-de-tus-vehiculos

---

### 3.12 Informe Telemático de Vehículos (INTV) — web service B2B
**Qué es:** *"consulta de información y generación de informes de vehículos a través de Web Service, pudiendo realizar la consulta en lotes e integrarla dentro de sus propios sistemas."* `[VERIFICADO]`
- **Datos:** *"exactamente los mismos que se obtienen a través del informe de vehículos para ciudadanos de la sede electrónica"* (las 7 modalidades).
- **Entrega:** **PDF** con el mismo formato/estilo que la sede.
- **Acceso:** Web Service vía **certificados electrónicos de dominios TRAFICO o SEDE**; identificación obligatoria + motivo (interés legítimo) + nº de tasa de 12 cifras para los de pago.
- **Alta:** Formulario de Peticiones e Incidencias → categoría "Registro de Vehículos" → subcategoría "(INTV) Informe Telemático de Vehículos".
- **Precio:** reducido gratis; resto **tasa 4.1 = 8,67€/consulta** (pago previo).
`[VERIFICADO ≥2]` sede.dgt (INTV) + dgt.es (informes en lote)

### 3.13 Informes de vehículos en lote — automatización para colaboradores/empresas
Mismo motor que INTV, orientado a empresas con **peticiones continuas**: consultas automatizadas integradas en sus sistemas, alta previa requerida, las 7 modalidades en lote, datos idénticos a ciudadano. `[VERIFICADO]` dgt.es/informes-de-vehiculos-en-lote

---

## 4. Metodología / fuentes de datos

| Fuente | Aporta | Estado |
|---|---|---|
| **Registro de Vehículos (DGT)** | Núcleo: identidad, titulares, transmisiones, cargas, bajas, datos técnicos de homologación | `[VERIFICADO]` |
| **Estaciones ITV** | Historial de inspecciones, defectos, **lecturas de cuentakilómetros**, resultado (favorable/desfavorable/caducada/negativa) | `[VERIFICADO]` |
| **Aseguradoras** | Constancia de seguro obligatorio + compañía + fecha de alta | `[VERIFICADO]` |
| **Fabricantes / homologación UE** | Datos técnicos (categoría UE, EURO, masas, variante/versión, contraseña de homologación), **llamadas a revisión (recalls)** | `[VERIFICADO]` |
| **Euro NCAP** | Valoración de seguridad (estrellas) — dato externo integrado en el informe | `[VERIFICADO ≥2]` |
| **Talleres adscritos ("Libro Taller")** | Historial de mantenimiento | `[VERIFICADO]` |
| **Autoridades judiciales/administrativas, Hacienda, ayuntamientos** | Embargos, precintos, denegatorias, impago IVTM, tutela | `[VERIFICADO]` |
| **Declaraciones voluntarias** | Lecturas de km aportadas por el titular | `[VERIFICADO]` |

**Naturaleza del dato:** **primario y autoritativo** (es el registro oficial), no inferido ni estadístico. La estadística agregada ("DGT en cifras") se deriva del mismo Registro. **No hay valoración de mercado** (precio/valor residual): eso lo aportan terceros (GANVAM/DAT/Eurotax) sobre estos datos. `[VERIFICADO]`

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| **Sede electrónica** (sede.dgt.gob.es) | Cl@ve / certificado digital / DNIe → introducir matrícula → **PDF descargable** inmediato. Reducido gratis sin pago | `[VERIFICADO ≥2]` |
| **App miDGT** (Android/iOS, gratis) | Reducido + Completo (compra de tasa en-app); ruta *Mis trámites > Vehículos > Informe de vehículos*; + panel gratuito de datos del titular | `[VERIFICADO ≥2]` |
| **Teléfono 060** | Completo/Técnico/Cargas/Sin matricular (NO Reducido ni "a mi nombre"); verificación por preguntas; **entrega por email**; 24/7 automático + agente L-V 9-18h; desde extranjero +34 902 887 060 | `[VERIFICADO]` |
| **Presencial** (Jefaturas/Oficinas de Tráfico) | Cita previa + impreso **Mod.01** + identificación + motivo; pago con tarjeta (no metálico); entrega inmediata | `[VERIFICADO]` |
| **INTV — Web Service** (B2B) | Integración por certificados TRAFICO/SEDE; consulta unitaria o **en lote**; salida **PDF** idéntico | `[VERIFICADO ≥2]` |
| **Informes en lote** | Automatización continua para empresas dadas de alta | `[VERIFICADO]` |
| **DGT en cifras / datos abiertos** | **Microdatos ZIP (ancho fijo .txt)** diarios+mensuales; **dashboards interactivos**; **anuario PDF**; también en datos.gob.es | `[VERIFICADO ≥2]` |
| **Formato del informe** | **PDF**; copias adicionales gratis hasta **4 días**; nº de tasa de **12 cifras** requerido para los de pago | `[VERIFICADO]` |
| **Revendedores (no-DGT)** | coches.com (9,99€, entrega email ≤48h), informevehiculo-dgt.es, vehiculosdgt.com, etc. revenden el informe oficial con margen de gestión | `[VERIFICADO ≥2]` |

---

## 6. Precio (modelo)

| Concepto | Precio | Estado |
|---|---|---|
| Informe Reducido | **0€ (gratis)** | `[VERIFICADO ≥2]` |
| Informe Completo / Técnico / Cargas / a mi nombre / sin matricular / titularidad | **8,67€** cada uno (**tasa 4.1**) | `[VERIFICADO ≥2]` |
| Consulta de distintivo ambiental | **0€**; **pegatina física = 5€** | `[VERIFICADO ≥2]` |
| Consulta de datos del titular (miDGT) | **0€** | `[VERIFICADO]` |
| Microdatos / dashboards / anuario | **0€ (datos abiertos)**; bastidor restringido desde 2025 (interés legítimo) | `[VERIFICADO ≥2]` |
| INTV / lote (B2B) | reducido gratis; resto **8,67€/consulta** (tasa 4.1) | `[VERIFICADO]` |
| Vía revendedor | **8,67€ tasa + margen de gestión** (p.ej. coches.com 9,99€ = 8,67 + 1,32) | `[VERIFICADO]` |

**Conclusión:** pricing **público, fijo y regulado** (tasa estatal), no de mercado. Modelo radicalmente distinto al de los proveedores privados (quote/subscription): aquí el dato es barato, oficial y autoservicio. `[VERIFICADO]`

---

## 7. Placement — DÓNDE coloca cada dato (patrón a copiar por cardeep)

> Doble patrón: (a) el **PDF del informe** = secciones condicionales en orden fijo; (b) el **trámite de la sede/app** = embudo identificación→input→pago→PDF; (c) el **panel de datos abiertos** = dashboard + descarga.

| Dato / métrica | Ubicación en la UI/informe DGT | Estado |
|---|---|---|
| Estado global del vehículo | **Informe Reducido = semáforo de 3 estados** (Sin incidencias / Con avisos / Con incidencias) — veredicto de un vistazo, gratis, antes del detalle | `[VERIFICADO]` |
| Fecha 1ª matriculación | Dato de cabecera del Reducido y del Completo | `[VERIFICADO]` |
| Titular + cotitulares + renting | **Sección 1 "Datos del Titular"** (arriba del Completo) | `[VERIFICADO]` |
| Identidad técnica (bastidor/marca/modelo/fecha/IVTM) | **Sección 2 "Identificación del Vehículo"** | `[VERIFICADO]` |
| Seguro | **Sección 3** (compañía + constancia) | `[VERIFICADO]` |
| ITV (historial + defectos + km + estado) | **Sección 4 "ITV"** — tabla histórica por inspección | `[VERIFICADO]` |
| Bajas | **Sección 5 "Historial de Bajas"** | `[VERIFICADO]` |
| Kilometraje / anti-clocking | **Sección 6 "Historial de Lecturas del Cuentakilómetros"** — tabla `fecha · lectura · origen` (ITV/declaración/taller) | `[VERIFICADO]` |
| Denegatoria | **Sección 7** (indicador) | `[VERIFICADO]` |
| Cargas (embargo/reserva dominio/precinto/leasing/renting/hipoteca) | **Sección 8 "Cargas o Gravámenes"** — bloque crítico para compraventa | `[VERIFICADO]` |
| Datos técnicos (potencia/combustible/masas/plazas/dimensiones) | **Sección 9 "Información Técnica"** | `[VERIFICADO]` |
| Historial de titulares (nº + fechas + física/jurídica) | **Sección 10** | `[VERIFICADO]` |
| Medioambiental (combustible/consumo/categoría EV/autonomía) | **Sección 11** | `[VERIFICADO]` |
| Seguridad | **Sección 12 "Euro NCAP"** (estrellas) | `[VERIFICADO]` |
| Recalls + mantenimiento | dentro del Completo (avisos de revisión + Libro Taller) | `[VERIFICADO]` |
| **Secciones condicionales** | *"si no aparece la sección, no hay anotación"* → la ausencia de sección **es** información (limpio) | `[VERIFICADO]` |
| Distintivo ambiental | **Servicio aparte, por matrícula, sin login** → etiqueta 0/ECO/C/B/sin | `[VERIFICADO]` |
| Datos del propio coche | **Panel privado miDGT** (titular) — ficha resumida gratis | `[VERIFICADO]` |
| Parque/matriculaciones | **Dashboard interactivo + microdatos descargables** (plano agregado, separado del per-vehículo) | `[VERIFICADO]` |

**Patrón clave para cardeep:**
1. **Reducido = semáforo gratis** que precede al informe de pago (gancho + veredicto rápido) → cardeep puede ofrecer un *estado de un vistazo* gratuito antes del detalle.
2. **Secciones condicionales** (solo se muestran si hay dato; la ausencia comunica "limpio") → UI por bloques que aparecen/desaparecen.
3. **Kilometraje como tabla fecha·lectura·origen** = patrón anti-clocking idéntico al NMR de HPI → cardeep debería renderizar km así.
4. **Separación nítida** entre **ficha per-vehículo** (informe) y **plano agregado** (dashboards/microdatos del parque).
5. **Identidad técnica densa** (categoría UE, EURO, variante/versión, masas, vía, distancia entre ejes) disponible como **feed estructurado** (MATRABA) — base de homologación per-VIN.

---

## 8. Diferencial (lo que ofrece y casi nadie más)

1. **Autoridad registral oficial:** es **la fuente de verdad** del vehículo en España; todos los demás (GANVAM/INTEVES, DAT, aseguradoras, revendedores) **derivan** de aquí. Confianza institucional irreplicable. `[VERIFICADO]`
2. **Cargas/embargos/reserva de dominio/precinto/hipoteca con valor legal** — dato que ningún agregador privado puede certificar con la misma fuerza. `[VERIFICADO]`
3. **Historial oficial de km** (lecturas ITV + declaraciones + talleres) con origen trazable → anti-clocking respaldado por el Estado. `[VERIFICADO]`
4. **Precio fijo, barato y público (8,67€ / gratis el reducido)**, autoservicio, multicanal (web/app/teléfono/presencial). `[VERIFICADO]`
5. **Datos abiertos masivos** (MATRABA: 69 campos técnicos/administrativos por alta; parque; transferencias; bajas) → **feed nacional ingestible** gratis. `[VERIFICADO]`
6. **Distintivo ambiental autoritativo** por matrícula, gratis, descargable en bloque. `[VERIFICADO]`
7. **Web service INTV + lote** para integración B2B con los mismos datos. `[VERIFICADO]`
8. **Cobertura del 100% del parque** y de **todo el ciclo de vida** (alta→transferencias→ITV→bajas→desguace). `[VERIFICADO]`
9. **Identidad técnica de homologación completa** (categoría UE, variante/versión, vehículo base, EURO, masas, vías) — granularidad de ficha técnica oficial. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Solo España.** Sin cobertura pan-europea (es autoridad nacional). `[VERIFICADO]`
2. **NO valora a mercado:** sin precio retail/trade, sin valor residual %, sin days-to-sell, sin price-to-market, sin curva de depreciación, sin índice oferta/demanda. Solo Euro NCAP como "calidad". Es estado **administrativo/técnico**, no inteligencia de pricing. `[VERIFICADO]`
3. **Sin API REST/JSON pública moderna ni sandbox:** el B2B es **SOAP/Web Service por certificado** + alta por formulario; la salida es **PDF**, no JSON estructurado por campo. Fricción de integración alta vs. proveedores privados. `[VERIFICADO]`
4. **Bastidor (VIN) restringido desde feb-2025** en los microdatos → el feed abierto pierde la clave per-VIN salvo interés legítimo aprobado. Limita el matching VIN↔registro a escala. `[VERIFICADO]`
5. **El informe es un PDF, no datos consultables campo a campo** por el ciudadano (hay que parsear el PDF). `[VERIFICADO]`
6. **Sin huella digital de punto de venta / dealer:** no cataloga concesionarios, su web, su inventario online ni su presencia digital (territorio propio de cardeep). `[VERIFICADO]`
7. **Sin datos de anuncios / mercado vivo:** no scrapea ofertas, no conoce precios pedidos ni stock en venta. `[VERIFICADO]`
8. **Datos personales del titular muy limitados/regulados** (protección de datos): el informe da filiación/razón social pero no es un buscador de personas. `[VERIFICADO]`
9. **Mantenimiento ("Libro Taller") parcial:** solo talleres adscritos; cobertura no universal. `[ASUMIDO]` (depende de adhesión de talleres)
10. **Portal Estadístico clásico discontinuado** (1-jul-2024) → migración a "DGT en cifras"; cierta fricción/cambio de URLs y formatos. `[VERIFICADO]`
11. **Latencia por revendedor:** vía intermediario (coches.com) la entrega puede ser **≤48h por email**, no instantánea como la sede directa. `[VERIFICADO]`

---

## 10. Fuentes (URLs)

**First-party — Sede electrónica / dgt.es (producto Informe)**
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/informe-de-un-vehiculo/ (7 modalidades, canales, tasa 4.1, SIA 202342)
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/informe-de-un-vehiculo/ayuda-para-interpretar-el-informe-del-vehiculo/ (**12 secciones del Completo + labels exactos**)
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/informe-de-un-vehiculo/ayuda-para-interpretar-el-informe-reducido-de-un-vehiculo/index.html (**3 estados del Reducido**)
- https://www.dgt.es/nuestros-servicios/tu-vehiculo/tus-vehiculos/informe-de-un-vehiculo/ (tipos, contenido, canales)
- https://revista.dgt.es/es/tramites/2025/1015-Informe-de-un-vehiculo.shtml (7 tipos, EuroNCAP, recalls)

**First-party — B2B / profesional**
- https://sede.dgt.gob.es/es/vehiculos/tramites-para-empresas/informe-telematico-de-vehiculos/ (INTV web service, lote, PDF, alta)
- https://www.dgt.es/nuestros-servicios/para-colaboradores-y-empresas/otras-empresas-y-proveedores/informes-de-vehiculos-en-lote/ (informes en lote)

**First-party — Servicios relacionados**
- https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/distintivo-ambiental/ (consulta gratis + 4 etiquetas + pegatina 5€ + descarga masiva)
- https://www.dgt.es/nuestros-servicios/tu-vehiculo/tus-vehiculos/distintivo-ambiental/ (etiquetas, criterios)
- https://www.dgt.es/nuestros-servicios/tu-vehiculo/tus-vehiculos/consulta-los-datos-de-tus-vehiculos/ (panel titular miDGT)

**First-party — Datos abiertos / estadística**
- https://www.dgt.es/menusecundario/dgt-en-cifras/ (catálogo de datasets + indicadores del parque)
- https://www.dgt.es/menusecundario/dgt-en-cifras/dgt-en-cifras-resultados/dgt-en-cifras-detalle/Microdatos-de-Matriculaciones-de-Vehiculos-mensual/ (microdatos mensuales, restricción bastidor 2025)
- https://sedeapl.dgt.gob.es/IEST_INTER/pdfs/disenoRegistro/vehiculos/matriculaciones/MATRICULACIONES_MATRABA.pdf (**diseño de registro = 69 campos, PDF leído íntegro**)
- https://datos.gob.es/es/catalogo/e00130502-microdatos-de-matriculaciones-de-vehiculos-mensual (ficha datos.gob.es, licencia)
- https://datos.gob.es/en/peticiones-datos/datos-de-vehiculos (peticiones, 28 GB, MATRABA)

**Identidad institucional / verificación cruzada**
- https://es.wikipedia.org/wiki/Direcci%C3%B3n_General_de_Tr%C3%A1fico (Ley 47/1959, HQ, director, plantilla, presupuesto, registros)
- https://www.dgt.es/conoce-la-dgt/quienes-somos/historia/ (historia, 1959)
- https://www.interior.gob.es/opencms/es/el-ministerio/funciones-y-estructura/subsecretaria-del-interior/direccion-general-de-trafico/ (adscripción Ministerio Interior)

**Terceros / revendedores / explainers (verificación cruzada de campos y precio)**
- https://www.km77.com/revista/engendro-mecanico/como-solicitar-informe-vehiculo/ (campos, robo, siniestros, embargos)
- https://www.coches.com/informe-trafico-dgt/ (9 secciones + desglose precio 8,67+1,32=9,99 + entrega ≤48h)
- https://andaluciainforma.eldiario.es/tramites/coche-de-segunda-mano-danos-ocultos-dgt-informe/ (8,67€, uso compraventa)
- https://www.cebriangestoria.com/como-pedir-un-informe-de-vehiculo-en-la-dgt-y-usarlo-para-evitar-problemas-en-una-compra-venta/ (uso gestoría)

> **Marcas [ASUMIDO] / a reconfirmar:** rotulado exacto del campo "robo/sustracción" dentro del PDF del Completo (confirmado en microdato `IND_SUSTRACCION` y por secundarias, no leído literal en la página de interpretación); cobertura real del "Libro Taller" (mantenimiento); cifras de plantilla/presupuesto (vía Wikipedia, no boletín oficial); diseño de registro de los ficheros hermanos Transferencias y Bajas (no transcritos campo a campo, solo el de Matriculaciones). Todo lo demás verificado en fuente oficial first-party o en ≥2 fuentes.

---

## 11. Resumen para schema

- **slug:** `dgt-informe-de-veh-culo`
- **subdominio:** `official-data`
- **productos:** 13 (Informe Reducido, Completo, Datos Técnicos, Cargas, Vehículos a Mi Nombre, Sin Matricular, Titularidad; Microdatos MATRABA; Dashboard Parque; Distintivo Ambiental; Datos del titular miDGT; INTV web service; Informes en lote).
- **diferencial central:** **fuente registral OFICIAL** del vehículo en España (cargas/embargos/titulares/ITV/km con valor legal) + **feed de datos abiertos de 69 campos** por matriculación, a precio fijo público (8,67€ / gratis).
- **gap central para cardeep:** no valora a mercado (sin pricing/residual/days-to-sell), API legacy SOAP+PDF (no JSON), VIN restringido en open data desde 2025, solo España, sin huella digital de dealers/anuncios.
