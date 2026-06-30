# Fasecolda — Guía de Valores — Auditoría atómica

> Slug: `fasecolda-gu-a-de-valores` · Subdominio cardeep: **valuation** · Región: **Colombia** (mercado único)
> Auditado: 2026-06-30 · Doctrina VAM: cada afirmación con fuente; `[VERIFICADO]` (leído) / `[PARCIAL]` / `[NO-VERIFICADO]` donde no se confirmó al 100%. Cero invención.
> Naturaleza: la **Guía de Valores** es la **referencia nacional del valor comercial promedio** de los vehículos que
> circulan en Colombia, publicada por **Fasecolda** (gremio de aseguradoras, sin ánimo de lucro) y **elaborada por un
> tercero especializado contratado**. Es el estándar de facto del mercado colombiano para asegurar, indemnizar,
> tasar impuestos y comprar/vender usados. **Dato núcleo: el valor comercial (COP) por `código Fasecolda` + año modelo**,
> acompañado de una **ficha técnica rica** (≈49 atributos por versión) y una **serie de valor multi-año**.
> ⚠ La herramienta oficial de consulta (`guiadevalores.fasecolda.com/ConsultaExplorador/`) **geobloquea** las IP
> fuera de Colombia: redirige a la home `fasecolda.com` (302) tanto en WebFetch como en navegador headless. La UI/campos
> se reconstruyeron vía: páginas oficiales del **Centro de Ayuda** (Primeros pasos, FAQ, Servicios adicionales, Glosario),
> el **glosario oficial de Colombia Compra Eficiente**, y el **esquema atómico real** que exponen los **revendedores de
> API** que espejan el dato Fasecolda (**Verifik** `api.verifik.co` con respuesta de ejemplo verbatim, y **guiadevalores.com**).

---

## 1. Identidad

| Campo | Valor | Fuente |
|---|---|---|
| Producto | **Guía de Valores** (de Fasecolda). Marca coloquial: "valor/precio Fasecolda" | fasecolda.com/guia-de-valores |
| Editor / propietario | **Fasecolda — Federación de Aseguradores Colombianos** | fasecolda.com; colombiacompra.gov.co |
| Naturaleza jurídica | **Entidad gremial sin ánimo de lucro** (NO organismo público; agrupa compañías de seguros, reaseguros y sociedades de capitalización) | WebSearch (LinkedIn/historia); fasecolda.com/nosotros/historia |
| Creación de Fasecolda | **23 de junio de 1976** (originalmente *"Unión de Aseguradores Colombianos"*; renombrada *"Federación de Aseguradores Colombianos"* en **1997**) | WebSearch (historia Fasecolda) `[VERIFICADO 1 fuente]` |
| HQ | **Bogotá, Colombia** — Carrera 7 # 26-20, Pisos 11 y 12 | WebSearch `[VERIFICADO 1 fuente]` |
| Quién **elabora** la guía | **Un tercero especializado contratado por Fasecolda** (el nombre del contratista **no se publica** oficialmente). Fasecolda valida/consolida. | fasecolda.com FAQ ("Elaborada por un tercero especializado contratado por Fasecolda") `[VERIFICADO]` |
| Quién **provee la API** a aseguradoras | **Inverfas** (brazo tecnológico del ecosistema Fasecolda) desarrolla el web service/API REST en tiempo real para aseguradoras afiliadas | fasecolda.com FAQ; WebSearch (Inverfas) `[VERIFICADO 2 fuentes]` |
| Mesa de ayuda / códigos nuevos | **`service.colserauto.com`** (solicitud de códigos nuevos) y **`mesadeayuda.fasecolda.com`** (requerimientos/disputas de valor) | fasecolda.com Servicios adicionales `[VERIFICADO]` |
| Revendedores de API (terceros, NO Fasecolda) | **guiadevalores.com** (portal comercial, planes anuales) · **Verifik** (`api.verifik.co`, plataforma de verificación de identidad/vehículos LatAm) | guiadevalores.com; docs.verifik.co `[VERIFICADO]` |

**Categoría de producto:** **guía de valoración nacional de referencia** (valor comercial promedio) + **catálogo técnico
de versiones** (ficha técnica por `código Fasecolda`). NO es VIN-decoder global, NO es analítica de mercado (days-to-sell,
oferta/demanda), NO es historial por unidad — aunque el **ecosistema Fasecolda** sí ofrece un dataset **adyacente** de
historial de siniestros por placa (ver §8, fuera del alcance de la Guía).

**Cliente objetivo (declarado):** **aseguradoras, intermediarios, concesionarios, ajustadores, peritos y particulares.**
Usos: suscripción e indemnización del ramo de automóviles; base del valor asegurado; cálculo de indemnización por pérdida
total/hurto; referencia para compraventa; soporte en avalúos, peritajes, procesos judiciales/administrativos y tributarios
(p. ej. patrimonio vehicular en declaración de renta; referencia de contratación pública). (Fuentes: fasecolda.com FAQ;
colombiacompra.gov.co; runt-por-placa.info.)

---

## 2. Cobertura

- **Geografía:** **solo Colombia.** Valor promedio del mercado colombiano; no se desglosa por ciudad/región (la ubicación
  geográfica es un factor que **hace variar** el precio real pero NO se modela en el dato). `[VERIFICADO]`
- **Nuevo Y usado:** ambos. El flujo de consulta exige elegir **"Estado del vehículo: nuevo / usado"**. Para nuevos se usan
  listas de precios y facturas de marcas/concesionarios; para usados, precios de oferta/demanda/transacción. `[VERIFICADO]`
- **Volumen:** **más de 17.000 referencias** (cifra oficial actual). Los revendedores citan **"18.000+"**. Fuentes
  terciarias antiguas hablan de "+10.000" y "modelos de los últimos ~30 años" → tomar **17.000+** como cifra oficial vigente. `[VERIFICADO oficial 17.000+; 18.000+ en reseller]`
- **5 categorías oficiales** (selector "Categoría del vehículo"):
  1. **Livianos pasajeros** (automóviles, camperos/SUV, camionetas de pasajeros)
  2. **Livianos carga** (pick-ups / carga liviana)
  3. **Motos / Motocicletas**
  4. **Pesados carga** (camiones, tractocamiones)
  5. **Pesados pasajeros** (buses / transporte de pasajeros)
  (Fuente: fasecolda.com Primeros pasos; runt-por-placa.info.) `[VERIFICADO 2 fuentes]`
- **Tipos de servicio:** **particular** y **público** (campo `service` = `PARTICULAR` / público). `[VERIFICADO vía API]`
- **Profundidad año-modelo / histórico:** la API devuelve una **serie de valores por año-modelo** (`valueModel[]`, p. ej.
  2016→2013 en el ejemplo real, cada uno con su valor y estado). Las descargas oficiales y la consulta web permiten
  histórico mes a mes. Una fuente terciaria antigua mencionaba rango "2005–2018" (desactualizada). `[VERIFICADO multi-año; rango exacto PARCIAL]`
- **Excluido del universo (sin valor en la guía):** vehículos de **emergencia**, **blindados**, **compactadores**,
  **recolectores de basura**, **mezcladoras de concreto**, **cisternas/tanqueros**, **semirremolques** (y semirremolques
  especiales), **maquinaria amarilla/agrícola**, **modelos anteriores a 1969** y vehículos **modificados**. (Fuente:
  runtplaca.com; comparaonline.) `[VERIFICADO 2 fuentes]`

---

## 3. Productos + campos atómicos

> La Guía es **un único dato núcleo** (valor comercial COP por `código Fasecolda`+año) envuelto en una **ficha técnica
> rica** y entregado por **3 canales oficiales** (web gratis · descarga Excel/plano mensual · API Inverfas para
> aseguradoras) + **APIs de revendedores**. El esquema atómico de SALIDA es **idéntico** en todos: a continuación, el
> esquema real verbatim del endpoint revendedor que espeja el dato Fasecolda.

### 3.1 Esquema atómico de SALIDA (respuesta real, verbatim)

Fuente primaria: **Verifik** `GET https://api.verifik.co/v2/co/fasecolda/values-by-code` (auth JWT, param `codeFasecolda`),
**respuesta 200 de ejemplo real** (Renault Sandero Authentique) capturada verbatim de la doc. Espeja la **ficha técnica
oficial** de Fasecolda. Cada fila = un campo atómico.

| Campo (API) | Etiqueta ES / significado atómico | Ejemplo real |
|---|---|---|
| `bcpp` | **Valor comercial base** (precio de referencia). Entero **en miles de COP** `[unidad PARCIAL]` | `"64200"` |
| `valueModel[]` | **Serie de valor por año-modelo** (la "mini curva"): array de objetos | (4 años) |
| `valueModel[].modelo` | **Año modelo** | `"2016"` |
| `valueModel[].valor` | **Valor comercial** de ese año (miles de COP) | `34500` |
| `valueModel[].estado` | **Estado**: `USADO` / `NUEVO` | `"USADO"` |
| `valueModel[].modeloId` / `idEstado` | IDs internos del año/estado | `47` / `1` |
| `homoloCode` | **Código de homologación** (cruce con RUNT/ministerio) | `"08001151"` |
| `plate` | **Placa** (la API admite consulta por placa→código) | `"ABC123"` |
| `marke` | **Marca** | `"RENAULT"` |
| `line1` | **Línea / Referencia 1** (modelo base) | `"SANDERO [FL]"` |
| `line2` | **Referencia 2** (acabado/trim) | `"AUTHENTIQUE"` |
| `line3` | **Referencia 3** (versión: motor/equipamiento) | `"MT 1600CC 8V AA"` |
| `category` | **Categoría** (1 de las 5) | `"LIVIANO PASAJEROS"` |
| `class` | **Clase** | `"AUTOMOVIL"` |
| `typology` | **Tipología** (carrocería) | `"HATCHBACK"` |
| `service` | **Servicio**: particular / público | `"PARTICULAR"` |
| `segmentSize` | **Segmento por tamaño** (A/B/C…) | `"B"` |
| `segmentCylinder` | **Segmento por cilindraje** | `"L"` |
| `country` | País | `"COL"` |
| `novelty` | **Novedad** (estado del registro, p. ej. A) | `"A"` |
| `groupUpdate` | **Grupo de actualización** | `"1"` |
| `observation` | **Observación** (texto libre) | `""` |
| `cylinderCapacity` | **Cilindraje** (cc) | `"1598"` |
| `power` | **Potencia** (HP) | `"90"` |
| `fuel` | **Combustible** | `"GASOLINA"` |
| `foodSystem` | **Sistema de alimentación** (inyección/carburador) | `"NO APLICA"` |
| `transmission` | **Transmisión** (config. de tracción 4x2/4x4) | `"4X2"` |
| `typeBox` | **Tipo de caja** (mecánica/automática) | `"MECANICA"` |
| `traction` | **Tracción** (delantera/trasera/total) | `"DELANTERA"` |
| `rearSuspension` | **Suspensión trasera** | `"NO APLICA"` |
| `axles` | **Número de ejes** | `"2"` |
| `weight` | **Peso** (kg) | `"1108"` |
| `long` | **Longitud** (mm) | `"4057"` |
| `doors` | **Número de puertas** | `"5"` |
| `capacityPassengers` | **Capacidad de pasajeros** | `"5"` |
| `capacityLoad` | **Capacidad de carga** (kg) | `"0"` |
| `typeAddress` | **Tipo de dirección** (hidráulica/eléctrica) | `"HIDRÁULICA"` |
| `brakes` | **Tipo de frenos** | `"DISCO/TAMBOR"` |
| `absShow` | **Frenos ABS** (SI/NO) | `"NO"` |
| `airbags` | **Nº de airbags** | `"0"` |
| `airconditioningShow` | **Aire acondicionado** (SI/NO) | `"SI"` |
| `typeAirConditioning` | **Tipo de A/A** (manual/climatizador) | `"MANUAL"` |
| `sunroofShow` | **Techo solar / sunroof** (SI/NO) | `"NO"` |
| `electricChairs` | **Sillas eléctricas** | `"0"` |
| `electricGlasses` | **Vidrios eléctricos** | `"0"` |
| `electricMirrors` | **Espejos eléctricos** | `"0"` |
| `sensorsShow` | **Sensores (de parqueo)** (SI/NO) | `"NO"` |
| `reverseCameraShow` | **Cámara de reversa** (SI/NO) | `"NO"` |
| `explorersShow` | **Exploradoras / antiniebla** (SI/NO) | `"NO"` |
| `tachometer` | **Tacómetro** | `"NO APLICA"` |
| `typeHeadlights` | **Tipo de faros** (halógeno/LED…) | `"HALOGENO"` |
| `upholsteryLeatherShow` | **Tapicería en cuero** (SI/NO) | `"NO"` |
| `importedShow` | **Importado** (SI/NO) | `"NO"` |
| *(meta)* `signature.dateTime` / `signature.message` / `id` | **Sello de certificación** + timestamp + id de transacción | `"…", "Certified by Verifik.co", "mhlt7"` |

**Conteo atómico:** **49 campos de datos del vehículo** (incl. `valueModel` como serie, con 5 subcampos) + 3 metadatos de
certificación. El `signature/message` aquí es del **revendedor** (Verifik); en el canal oficial el sello equivalente es la
**vigencia/mes** del dato Fasecolda.

### 3.2 El identificador: `código Fasecolda` (8 dígitos)

- **Formato:** **8 dígitos numéricos**, único por **marca + tipología + referencia**. Si en la póliza aparece con menos
  dígitos, se **rellena con ceros a la izquierda** hasta 8. Una misma marca/modelo puede tener **varios códigos** (por
  diferenciación técnica/comercial de versiones). `[VERIFICADO oficial]`
- **Estructura (triple-fuenteada):**
  - **Dígitos 1–3** → **marca**
  - **Dígitos 4–5** → **tipología vehicular**
  - **Dígitos 6–8** → **consecutivo** de marca+tipología
  (Fuentes: comparaonline.com; c3carecarcenter.com; grupor5.com.) `[VERIFICADO 3 fuentes]`
- **Rol:** **clave de unión** del ecosistema (pólizas, RUNT vía `homoloCode`, SOAT, impuestos, portales). El valor comercial
  se obtiene combinando `código Fasecolda` **+ año modelo**.

### 3.3 Parámetros de ENTRADA (modos de consulta)

| Modo | Campos / flujo | Fuente |
|---|---|---|
| **Búsqueda básica** | secuencia obligatoria: **Categoría → Estado (nuevo/usado) → Modelo (año) → Marca → Referencia → Tipología** | Primeros pasos `[VERIFICADO]` |
| **Búsqueda avanzada** | básica **+ filtros opcionales**: **tipo de caja · aire acondicionado · tipo de combustible · sunroof · transmisión · tracción · frenos ABS** (para "perfeccionar la búsqueda y disminuir las opciones") | Primeros pasos; runtplaca `[VERIFICADO]` |
| **Búsqueda por código** | input directo del **`código Fasecolda` (8 díg.)** | Primeros pasos `[VERIFICADO]` |
| **(API) por código / por placa** | `codeFasecolda` (req.) **o** placa → devuelve ficha+valores | docs.verifik.co `[VERIFICADO]` |

### 3.4 Lo que el dato NO trae

El núcleo es **valor comercial promedio** + **ficha técnica de versión** + **serie por año**. **NO** trae: precio
retail/trade/wholesale separados, precio de subasta, days-to-sell, market days supply, price-to-market %, índice
oferta/demanda, volumen de anuncios, ajuste por kilometraje/daños/estado, color, MSRP/invoice de nuevo con incentivos,
TCO, ni reviews. La **ubicación, km, daños, accesorios y mantenimiento** se reconocen explícitamente como factores que
**desvían** el valor real, pero **no se parametrizan** en el dato. `[VERIFICADO]`

---

## 4. Metodología / fuentes de datos

- **Fuentes de precio** (declaradas oficialmente):
  - **Portales web de clasificados y publicaciones especializadas.**
  - **Concesionarios y comercializadores de vehículos.**
  - **Importadores y ensambladores de vehículos.** `[VERIFICADO]`
- **Nuevos:** se usan **listas de precios y facturas** proporcionadas por marcas y concesionarios. `[VERIFICADO]`
- **Usados:** se consideran **precios de oferta, demanda y transacción** (aproxima lo que un comprador ofrecería y un
  vendedor aceptaría). `[VERIFICADO]`
- **Tratamiento estadístico:** **detección de valores atípicos** (outliers) + **modelos estadísticos** para **consolidar un
  valor promedio**. Lo ejecuta el **tercero contratado**; Fasecolda valida/consolida. `[VERIFICADO]`
- **Actualización: mensual** ("se actualizan mensualmente para reflejar las variaciones del mercado"). `[VERIFICADO 3 fuentes]`
- **Naturaleza: voluntaria y NO normativa.** "No es obligatoria: su uso es voluntario"; "no tiene carácter normativo ni
  regulatorio. Sirven solo como una referencia orientativa." `[VERIFICADO]`
- **Disputas/correcciones:** vía **Centro de Ayuda** dentro de la Guía; el usuario adjunta soporte (cotizaciones, facturas,
  avisos de venta) y el caso se evalúa/corrige. `[VERIFICADO]`

---

## 5. Entrega

| Canal | Detalle | Audiencia | Estado |
|---|---|---|---|
| **Portal web público** | `guiadevalores.fasecolda.com/ConsultaExplorador/` — consulta **gratuita**, búsqueda básica/avanzada/por código, **ficha técnica** y **comparador de hasta 4 vehículos** | público general | Oficial `[VERIFICADO; ⚠ geobloqueado fuera de CO]` |
| **App móvil** | consulta por título/declaración de importación/factura/código | público | `[VERIFICADO 1 fuente — comparaonline]` |
| **Descarga mensual** | **archivos Excel** y **archivos planos** con "toda la información: descripción, valores, modelos y especificaciones"; **periodicidad mensual** | público general (Excel); aseguradoras (set limitado en transición) | Oficial `[VERIFICADO]` |
| **API REST — Inverfas** | web service **en tiempo real** para que las aseguradoras afiliadas consulten valores desde sus sistemas; baja latencia, alta disponibilidad | **aseguradoras afiliadas** | Oficial `[VERIFICADO 2 fuentes]` |
| **Solicitud de códigos nuevos** | mesa `service.colserauto.com` para crear códigos de versiones nuevas | **aseguradoras + fabricantes/importadores** | Oficial `[VERIFICADO]` |
| **Mesa de ayuda / requerimientos** | `mesadeayuda.fasecolda.com` — quejas sobre valores o errores de descripción (registro por email, sin contraseña) | particulares | Oficial `[VERIFICADO]` |
| **APIs de revendedores (NO Fasecolda)** | **guiadevalores.com** (`portal.guiadevalores.com`, REST, por membresía) · **Verifik** `api.verifik.co/v2/co/fasecolda/values-by-code` (JWT) — espejan el dato | integradores/empresas | Tercero `[VERIFICADO]` |

---

## 6. Precio

- **Consulta web pública + descarga Excel mensual: GRATIS.** Es el modelo oficial de Fasecolda (acceso libre al público). `[VERIFICADO]`
- **API Inverfas (aseguradoras afiliadas):** por **planes de suscripción con límites de consulta** y control de uso; **tarifas
  NO públicas** (acceso restringido a afiliados). `[NO-VERIFICADO importe]`
- **Revendedor `guiadevalores.com`** (NO es precio oficial de Fasecolda) — membresías **anuales, pago único**: `[VERIFICADO verbatim]`
  - **Plan Estándar:** **$18.000.000 COP + IVA / año** · hasta **7.000 consultas/mes (84.000/año)** · integración API/Web
    Service · soporte técnico.
  - **Plan Empresarial** (*"Más popular"*): **$24.000.000 COP + IVA / año** · hasta **25.000 consultas/mes (300.000/año)**
    · mayor capacidad para picos · soporte prioritario.
  - Todos: documentación completa + actualizaciones automáticas.
- **Verifik:** modelo pay-per-API/crédito; tarifa exacta del endpoint Fasecolda **no publicada** en la doc (requiere credenciales). `[NO-VERIFICADO importe]`

---

## 7. Placement (patrón web — clave para cardeep)

> Patrón **"selector en cascada → ficha técnica de versión → valor por año → comparador"**, distinto del "ancla única" de
> FIPE: aquí el **valor** viaja **acompañado de una ficha técnica densa** y de una **mini-serie por año**. El `código
> Fasecolda` es el héroe de identidad. (Reconstruido de Primeros pasos + FAQ + esquema API; render en vivo bloqueado por geo.)

**A. Selector de consulta (pantalla de entrada).** Tres pestañas/modos: **Búsqueda básica · Búsqueda avanzada · Búsqueda por
código**. La básica impone una **cascada obligatoria**: Categoría → Estado → Modelo(año) → Marca → Referencia → Tipología.
La avanzada añade chips/filtros (tipo de caja, A/A, combustible, sunroof, transmisión, tracción, ABS) para reducir resultados.

**B. Lista de resultados.** Filas de versiones coincidentes con info básica + dos acciones: **"Ver la ficha técnica"** y
**checkbox para seleccionar hasta 4** vehículos y **"comparar sus características"**.

**C. Ficha técnica de la versión (la "ficha de coche" — núcleo para cardeep):** un bloque por `código Fasecolda` que reúne:
1. **Identidad:** `código Fasecolda` (8 díg) como ancla + Marca + Referencia 1/2/3 (línea→trim→versión) + Tipología + Clase + Categoría + Servicio.
2. **Valor:** **valor comercial (COP)** para el **año modelo** elegido (y, vía API, la **serie `valueModel[]`** de varios años con su estado nuevo/usado → patrón de **depreciación**).
3. **Mecánica:** cilindraje, potencia, combustible, sistema de alimentación, transmisión, tipo de caja, tracción, suspensión, ejes, dirección, frenos (+ABS).
4. **Carrocería/medidas:** puertas, pasajeros, capacidad de carga, peso, longitud, segmento (tamaño/cilindraje).
5. **Equipamiento (flags SI/NO):** A/A (+tipo), sunroof, vidrios/espejos/sillas eléctricos, sensores, cámara de reversa, exploradoras, airbags, tapicería en cuero, faros, importado.

**D. Comparador (hasta 4 versiones lado a lado).** Tabla atributo-por-fila para contrastar características entre códigos. `[VERIFICADO existencia]`

**E. Centro de Ayuda / disputa.** Enlace persistente para **reportar inconsistencia de valor** con soporte documental.

**Lección de colocación para cardeep:** cuando la fuente de un país sea una "Fasecolda-equivalente" (guía nacional con
**ficha técnica + valor**), cardeep debe: (1) usar el **código nacional** (`código Fasecolda` ↔ `cdp_code`) como ancla de
identidad y de unión con homologación/placa; (2) mostrar el **valor comercial + año modelo** como dato principal y exponer
la **serie por año** como mini-curva de depreciación; (3) renderizar la **ficha técnica densa** (mecánica + equipamiento en
flags SI/NO) en la ficha de vehículo; (4) ofrecer **comparador multi-versión**; (5) declarar explícitamente que km/estado/
ubicación **no** están en el dato (gestión de expectativas, igual que Fasecolda).

---

## 8. Diferencial (lo que ofrece y otras no)

1. **Estándar nacional de facto** para asegurar/indemnizar/tasar en Colombia, respaldado por **todo el gremio asegurador** →
   neutralidad percibida (no es de un dealer ni de una sola aseguradora).
2. **`código Fasecolda` (8 díg):** identificador nacional compacto y estructurado (marca|tipología|consecutivo), **join key**
   de pólizas, RUNT (`homoloCode`), SOAT, impuestos y portales. Convierte "valor" en un grafo enlazable.
3. **Ficha técnica rica (≈49 atributos)** acompañando al valor — mucho más que el "número único" de FIPE: mecánica completa
   + equipamiento en flags SI/NO + segmentación. Sirve como **catálogo de versiones**, no solo tasador.
4. **Serie de valor multi-año (`valueModel[]`)** por código → depreciación observable en un solo request.
5. **Triple entrega oficial gratuita/afiliada:** web pública + Excel/plano mensual + **API en tiempo real (Inverfas)** para aseguradoras.
6. **Gobernanza de disputas:** Centro de Ayuda con soporte documental y proceso de corrección — trazabilidad de calidad.
7. **Cobertura ancha de clases:** livianos pasajeros/carga, motos, pesados carga/pasajeros (no solo autos).
8. **Ecosistema adyacente Fasecolda** (fuera de la Guía pero del mismo gremio): **verificación de siniestros por placa**
   (`api.verifik.co/v2/co/fasecolda/sinister` → array de siniestros con `accidentDate`, `protection` p. ej. "Pérdida Menor
   Cuantía") — señal de historial que las guías puras (FIPE, GANVAM) no tienen. `[VERIFICADO; adyacente, NO parte de la Guía de Valores]`

---

## 9. Gaps (lo que NO ofrece)

1. **Solo Colombia** → hueco geográfico para cardeep.
2. **Una sola métrica de valor** (comercial promedio). **Sin** retail/trade/wholesale/subasta separados, sin rango low–high.
3. **Sin ajuste por kilometraje, estado, daños, accesorios ni ubicación** — se reconocen como factores externos no modelados.
4. **Sin analítica de mercado:** ni days-to-sell, ni market days supply, ni price-to-market %, ni índice oferta/demanda, ni volumen de anuncios.
5. **Sin curva de depreciación proyectada / forecast / valor residual futuro** (la `valueModel[]` es histórica/observada, no predictiva).
6. **Sin VIN-decode global** (usa `código Fasecolda` nacional + `homoloCode`, no VIN 17). El historial por unidad (siniestros) es **adyacente**, por placa, y **no integrado** en la ficha de valor.
7. **Sin MSRP/invoice con incentivos de nuevo, sin TCO/coste de propiedad, sin reviews/editorial.**
8. **Sin desglose regional** (valor nacional único pese a que la ubicación afecta el precio real).
9. **API oficial en tiempo real restringida a aseguradoras afiliadas;** el público sólo tiene web + Excel. El acceso
   programático abierto depende de **revendedores** (guiadevalores.com, Verifik) con coste y sin aval oficial explícito.
10. **Contratista que elabora la guía no divulgado** → opacidad parcial de la cadena de producción del dato.
11. **Exclusiones de catálogo:** emergencia, blindados, maquinaria amarilla/agrícola, semirremolques, cisternas, pre-1969 y
    modificados → nichos sin valor.
12. **Unidad de los importes** (miles de COP) no siempre explícita en los espejos → riesgo de mala interpretación. `[PARCIAL]`

---

## 10. Fuentes

**Oficiales Fasecolda**
- Guía de Valores (landing): https://www.fasecolda.com/guia-de-valores/
- Acerca de la Guía: https://www.fasecolda.com/fasecolda-guia-de-valores/
- Centro de Ayuda — Primeros pasos (modos de búsqueda, cascada, ficha técnica, comparador, código 8 díg): https://www.fasecolda.com/fasecolda-guia-de-valores/centro-de-ayuda/primeros-pasos/
- Centro de Ayuda — Preguntas frecuentes (metodología, fuentes, nuevo/usado, mensual, voluntaria/no normativa, factores km/daños/ubicación): https://www.fasecolda.com/ramos/automoviles/guia-de-valores/centro-de-ayuda/preguntas-frecuentes/ · https://www.fasecolda.com/fasecolda-guia-de-valores/centro-de-ayuda/preguntas-frecuentes/
- Centro de Ayuda — Servicios adicionales (Excel/archivos planos mensual, códigos nuevos vía colserauto, requerimientos): https://www.fasecolda.com/fasecolda-guia-de-valores/centro-de-ayuda/servicios-adicionales/
- FAQ ramo automóviles (17.000+ referencias, marca/línea/versión/año, API Inverfas): https://www.fasecolda.com/ramos/automoviles/preguntas-frecuentes/
- Herramienta de consulta (geobloqueada fuera de CO; redirige a home): https://guiadevalores.fasecolda.com/ConsultaExplorador/
- Historia/identidad Fasecolda (1976, Bogotá, gremio sin ánimo de lucro): https://www.fasecolda.com/fasecolda/nosotros/historia/ · https://co.linkedin.com/company/federacion-de-aseguradores-colombianos-fasecolda

**Glosario oficial del Estado**
- Colombia Compra Eficiente (definición oficial: "guía de precios… en formato Excel… último mes disponible"): https://www.colombiacompra.gov.co/archivos/glosario/guia-de-valores-de-fasecolda

**Esquema atómico (revendedores que espejan el dato)**
- Verifik — Vehículo por código (esquema JSON completo + ejemplo real verbatim, endpoint, JWT, `bcpp`, `valueModel[]`, ~49 campos): https://verifik.gitbook.io/verifik/verifik-es/validacion-de-vehiculo/colombia/vehiculo-por-codigo-fasecolda · https://docs.verifik.co/vehicle-validation/colombia/vehicle-by-code-fasecolda
- Verifik — Verificación de siniestros por placa (adyacente): https://docs.verifik.co/vehicle-validation/colombia/sinister-verification-fasecolda
- Verifik — artículo de producto (API de valuación Colombia): https://verifik.co/en/get-instant-vehicle-valuations-in-colombia-with-the-fasecolda-api/
- guiadevalores.com — Producto (valores de referencia + datos históricos + características técnicas; campos Categoría/Estado/Modelo/Marca/Referencia/Combustible): https://www.guiadevalores.com/producto/
- guiadevalores.com — Planes y precios (Estándar $18M / Empresarial $24M COP+IVA/año; cupos de consultas): https://www.guiadevalores.com/planes/
- guiadevalores.com — landing (API REST, 18.000+ referencias, baja latencia): https://www.guiadevalores.com/

**Terciarias (estructura del código, campos, usos) — usadas para doble/triple verificación**
- Estructura código 8 díg (3 marca / 2 tipología / 3 consecutivo): https://www.comparaonline.com.co/blog/autos/seguro-todo-riesgo/datos-de-la-guia-de-valores-fasecolda/ · https://www.c3carecarcenter.com/blog/valores-fasecolda-lo-que-necesitas-saber-para-tu-vehiculo/ · https://www.grupor5.com/blog/movilidad/guia-de-valores-fasecolda
- Campos por vehículo / clases / exclusiones / modos de búsqueda: https://consulta.runtplaca.com/fasecolda-guia-valores/ · https://runt-por-placa.info/guia-valores-fasecolda/ · https://www.colconectada.com/fasecolda-precio-de-vehiculos/

### Notas de verificación
- **Geobloqueo:** `guiadevalores.fasecolda.com/ConsultaExplorador/` y `…/Default.aspx` devuelven **302 → `www.fasecolda.com`**
  tanto en WebFetch (US-only) como en navegador headless. La UI/placement se reconstruyó de páginas oficiales del Centro de
  Ayuda + esquema API. **Render pixel-exacto del tool en vivo: `[PARCIAL]`** (no invención: el flujo y los campos están en
  fuentes oficiales).
- **Esquema atómico (≈49 campos):** **verbatim** de la respuesta 200 de ejemplo de Verifik (espejo del dato Fasecolda),
  corroborado por los filtros de "búsqueda avanzada" oficiales (caja, A/A, combustible, sunroof, transmisión, tracción, ABS).
- **`bcpp`** = "base commercial price" (valor comercial base) según la doc del revendedor; importes en **miles de COP** por
  convención observada (ej.: `valor:34500` ↔ $34.500.000) → **unidad marcada `[PARCIAL]`**, no afirmada como certeza.
- **Código de 8 díg (3-2-3):** **triple fuente** terciaria concordante; el rellenado con ceros a la izquierda es oficial.
- **Precios de API (Estándar $18M / Empresarial $24M COP+IVA/año):** son del **revendedor guiadevalores.com**, **NO** tarifa
  oficial de Fasecolda. La tarifa de Inverfas a aseguradoras **no es pública** (`[NO-VERIFICADO]`).
- **Contratista que elabora la guía:** oficialmente "tercero especializado contratado"; **nombre no divulgado** → no inventado.
- **Verificación de siniestros:** producto **adyacente** del ecosistema Fasecolda (por placa), **NO** parte de la Guía de
  Valores; incluido en §8 con su límite declarado.
- **Fundación de Fasecolda (1976) y sede (Bogotá, Cra 7 #26-20):** `[VERIFICADO 1 fuente]` (WebSearch historia); no contrastado
  contra un segundo documento primario.
