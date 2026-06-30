# GANVAM — Auditoría atómica de inteligencia de automoción

> **Slug:** `ganvam` · **Subdominio (categoría cardeep):** `valuation`
> **Auditado:** 2026-06-30 · **Confianza global:** ALTA en identidad/productos/campos · MEDIA en precio (opaco) y en placement del producto B2B (tras login).
> **Convención:** cada afirmación va marcada `[VERIFICADO]` (leído en fuente) o `[ASUMIDO]` (inferencia declarada). Nunca se presenta un asumido como verificado.

> **Nota crítica de naturaleza:** GANVAM **NO es una empresa de datos al uso**: es la **patronal/asociación** del sector de venta y reparación de vehículos de España. Su "producto de datos/inteligencia" es un brazo de servicios para asociados + una **referencia oficial de valoración de VO** que el mercado, Hacienda, la DGT, aseguradoras y tribunales aceptan. El motor de valoración profesional moderno se vehicula a través de la **alianza GANVAM-DAT** (con el grupo alemán DAT, operado en España por DAT Automóvil Ibérica SLU). `[VERIFICADO]`

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre completo | Asociación Nacional de Vendedores y Reparadores de Vehículos (histórico: "...de Vehículos a Motor, Reparación y Recambios") | `[VERIFICADO]` footer ganvam.es 2024 |
| Marca corta | GANVAM | `[VERIFICADO]` |
| Naturaleza | Asociación patronal / organización empresarial (no sociedad mercantil de datos) | `[VERIFICADO]` |
| Fundación | ~1959 ("más de 65 años de actividad" a 2024) | `[VERIFICADO]` footer first-party |
| Antigüedad publicando valores VO | Desde **1966** (>50 años de referencia de mercado) | `[VERIFICADO]` ficha Google Play (texto oficial GANVAM) |
| HQ | C/ Príncipe de Vergara, 74 – 2ª Planta, 28006 Madrid | `[VERIFICADO]` first-party |
| Tel / email | 914113663 / 914113745 · ganvam@ganvam.es | `[VERIFICADO]` |
| Idiomas web | ES / EN / PT | `[VERIFICADO]` |
| Posición | "Organización decana y más representativa de la distribución (venta y reparación) de vehículos en España" | `[VERIFICADO]` |

### Brazo de valoración profesional: GANVAM-DAT
| Campo | Valor | Estado |
|---|---|---|
| Entidad | GANVAM-DAT — entidad **neutral** facilitadora del valor de referencia del mercado de ocasión | `[VERIFICADO]` |
| Alianza | GANVAM (patronal ES) + **DAT Group** (corporación alemana, pionera en IA aplicada a valoración) | `[VERIFICADO]` |
| Operador técnico ES | **DAT AUTOMÓVIL IBÉRICA SLU** — CIF **B62394762** — Rambla de Catalunya 60, 1-1, 08007 Barcelona | `[VERIFICADO]` footer discover.datiberica.com |
| Formalización del acuerdo | **2024** | `[VERIFICADO]` (autospare, posventa, renting-automocion) |
| Partner histórico (legacy) | **EUROTAX** — colaboración tradicional de las tablas; aún citado en blogs SEO y en el "Informe de Evolución Precios Eurotax-Ganvam". El motor **actual/oficial es DAT** (2024+). | `[VERIFICADO]` (transición Eurotax→DAT confirmada por fuentes 2024) |

**Clientes objetivo:** concesionarios oficiales e independientes, compraventas, empresas de renting/leasing, fabricantes (OEM), peritos, gestores de flotas, aseguradoras, financieras, administraciones públicas, tribunales/peritos judiciales, talleres. Grupos que ya usan el Índice GANVAM-DAT: **Grupo Marcos Automoción, Movento, Grupo Oliva, Yomovo, Automóviles Alhambra, Grupo Untoria, HR Motor**. `[VERIFICADO]` posventa.com

---

## 2. Cobertura

- **País:** **España exclusivamente** (no pan-europeo). `[VERIFICADO]` "marcas y modelos comercializados en España".
- **Scope nuevo/usado:** ambos. Estadísticas de **VN** (matriculaciones) + valoración y estadísticas de **VO** (núcleo del prestigio). `[VERIFICADO]`
- **Antigüedad de valoración:** hasta **12 años** en el boletín/app estándar; producto aparte para **>12 años** en tienda online. `[VERIFICADO]`
- **Tipos de vehículo cubiertos:** turismos, todoterrenos/SUV, vehículos comerciales, vehículos industriales (camiones/autobuses), **motocicletas, ciclomotores, quads**, **microcoches**, **tractores agrícolas**, vehículos de alquiladores. Cobertura de motorizaciones: gasolina, diésel, híbrido no enchufable (HEV), híbrido enchufable (PHEV), eléctrico puro (BEV). `[VERIFICADO]`
- **Granularidad geográfica (datos de mercado):** por **provincia**, por **marca**, por **municipio** (>50.000 hab.), por **código postal**. `[VERIFICADO]` first-party datos-mercado.

---

## 3. Productos + campos atómicos

### P1 — Boletín de Valores de VO / App "GANVAM Valores VO" (valoración estándar)
La referencia clásica. App móvil (Android/iOS/APK) + boletín. Selección táctil de criterios.
- **Inputs:** `marca`, `modelo`, `versión`, `antigüedad` (año matriculación, ≤12 años), `tipo de vehículo` (coche/moto/ciclomotor/quad).
- **Output:** `valor de mercado VO` = **precio real de venta de profesional a cliente final** (retail), no estimación teórica.
- **Gestión:** módulo de **gestión de stock/inventario** en la app.
- **Base:** >**8.000 datos mensuales** de ventas reales aportados por ~**800 empresas**. `[VERIFICADO]` (ficha Google Play, oficial)
- Nº campos atómicos: ~6.

### P2 — Boletín Blanco (Boletín Estadístico de Vehículos de Ocasión)
- Campos: `valoración del turismo usado` + `impuestos` + `gastos de transferencia` + `garantía`. (Es decir, valor + costes asociados a la operación.) `[VERIFICADO]` (búsqueda; coherente entre fuentes)
- Variantes: Boletín Blanco de **ciclomotores/motocicletas/quads**.
- Nº campos: ~4 (+ identificación marca/modelo/año).

### P3 — Boletín Azul
- Recurso para asociados **orientado a la venta** de vehículos (valores de venta). `[VERIFICADO PARCIAL]` — la distinción exacta Blanco/Azul no está en páginas públicas first-party (contenido tras login); las fuentes secundarias coinciden en que Azul se asocia a **venta** y Blanco al **boletín estadístico con valoración+impuestos+transferencia+garantía**. Marcar como dato a reconfirmar con acceso de asociado.
- Variante motos/ciclomotores/quads.

### P4 — Boletines de motos/ciclomotores/quads (estructura de tabla verificada en web)
Estructura real de la tabla de consulta (renderizada):
- **Filtros:** `Periodo`, `Marca`, `Tipo`, `Modelo`, `Año`.
- **Columnas de resultado:** `Modelo`, `Tipo`, `Valor`.
- `[VERIFICADO]` snapshot ganvam.es/motos-boletin-blanco.
- Nº campos: ~6.

### P5 — GANVAM-DAT · "Valoración de Stock" / Índice GANVAM-DAT (producto profesional B2B)
El motor moderno. Plataforma multidispositivo (sin instalación) + carga masiva. **Este es el producto más rico en campos.**
- **Identificación:** `VIN` (auto-identificación vía **IdentifyVIN**) o `matrícula` → identificación "100% confiable y detallada".
- **Datos del vehículo:** `datos técnicos`, `equipamiento de serie`, `equipamiento opcional`, `versión exacta`, `PVP/precio de tarifa original`.
- **Valores económicos:** `valor de venta` (retail), `valor de compra` (trade), `valor residual %`, `valor de mercado real`, `depreciación / evolución de valor a futuro`.
- **Variables de cálculo (más allá de antigüedad/km):** `antigüedad`, `kilometraje` (+ ajuste por km), `tipo de motorización` (BEV/PHEV/HEV/gasolina/diésel), `estado de batería (State of Health)`, `estrés de batería`, `tipo y duración de carga`, `datos telemáticos`, `estado actual y futuro del vehículo`, `rotación de stock`, `demanda por canal`, `comportamiento real de mercado`.
- **Fuentes de valor:** `precios reales de transacción` (distribuidores, financieras) + `precios de oferta de plataformas online`.
- **Casos de uso productizados:** cumplimiento contable/fiscal (valoración de stock para balance), estrategia (promociones/renovaciones), valoración por lotes, eficiencia fiscal. Fue la referencia para valorar los vehículos dañados por la **DANA** ante el **Consorcio de Compensación de Seguros**. `[VERIFICADO]`
- Nº campos atómicos: ~22.

### P6 — Datos de Mercado V.N. y V.O. (Dashboard "Informes Dashboard VN y VO")
- `Matriculaciones VN` mensuales por tipo (turismos, todoterreno, comerciales, industriales, motocicletas, tractores agrícolas, alquiladores) × `provincia` × `marca`.
- `Matriculaciones VN` de turismos/todoterreno por `municipio` (>50.000 hab.) × `código postal`.
- `Transferencias` (cambios de titularidad VO) por tipo de vehículo.
- `Bajas de propiedad` (deregistrations) por tipo.
- `Histórico de matriculaciones`, `Avance de matriculaciones` (preview), `cuota de mercado`, `infografías/resúmenes mensuales`.
- `[VERIFICADO]` first-party.
- Nº campos: ~10.

### P7 — Tabla promedio de kilometraje
- `kilometraje promedio` por `antigüedad`/`tipo de vehículo` — usada como referencia de **ajuste por km** sobre el valor base. `[VERIFICADO]`

### P8 — Buscador de Matrículas
- Input `matrícula` → `fecha de matriculación` (cobertura registral ~1900 → actualidad). `[VERIFICADO]` (servicios)

### P9 — INTEVES (informe DGT)
- Informe oficial de información del vehículo de la DGT: `datos oficiales de matriculación`, `historial del vehículo`. Es un **passthrough de datos DGT**, no dato propietario de GANVAM. `[VERIFICADO]`

### P10 — Valores de vehículos con más de 12 años (tienda online)
- `valoración VO` para vehículos fuera del rango estándar (>12 años). `[VERIFICADO]`

### P11 — Baremos de transferencias
- `importe/baremo de transferencia` de referencia para calcular costes de cambio de titularidad. `[VERIFICADO]`

### P12 — Informes de inteligencia/tendencias (analítica de mercado, no per-vehículo)
- **Informe MADE**, **Informe de Movilidad GANVAM–NTT DATA**, **Previsiones 2026-2030**, **Diagnosis de la posventa en España**, **Informe técnico Plan de Achatarramiento**, "La Clave de QVADRIGAS", serie de vídeo-análisis.
- Métricas que publican (con definición verificada):
  - `precio medio VO` global y por `antigüedad` (p.ej. ≤10 años, >15 años) y por `motorización`.
  - `retención de valor a 3 años (%)` = precio tras **60.000 km a 36 meses** vs precio de tarifa original (HEV ~68%, gasolina ~60,2%, PHEV ~59,4%, diésel ~58,3%, BEV ~48% en lectura 2025).
  - `margen VO vs VN` (~8,8% VO vs ~8,5% VN), `rotación de stock` (vueltas/año), `coste por día en stock`, `volumen de ventas VO`, `relación/ratio VO:VN`.
- `[VERIFICADO]` notas de prensa GANVAM 2025-2026.

### P13 — Estadísticas a Medida
- `datos estadísticos personalizados` bajo demanda (B2B). `[VERIFICADO]` (tienda online)

---

## 4. Metodología y fuentes de datos

- **Inferencia estadística sobre transacciones reales:** ~**800 empresas** del sector (concesionarios oficiales + compraventas independientes) aportan ~**8.000 operaciones reales/mes** de venta de VO profesional→cliente final. `[VERIFICADO]`
- **Frecuencia:** actualización **trimestral** del libro de valoraciones; estadísticas de matriculación/transferencias **mensuales**. `[VERIFICADO]`
- **Fuentes complementarias:** administraciones estatal/autonómica/municipal, aseguradoras, asociaciones de consumidores, DGT. `[VERIFICADO PARCIAL]` (vendertucoche/yamovil; coherente).
- **Motor GANVAM-DAT:** combina `precios reales de transacción` (distribuidores + financieras) + `precios de oferta de plataformas online` + **IA** del DAT Group + red sectorial GANVAM; añade variables de electrificación (batería, carga, telemática) y de mercado (rotación, demanda por canal). Identificación por VIN (IdentifyVIN). Posicionado como **entidad neutral**. `[VERIFICADO]`
- **Limitación metodológica declarada (tablas clásicas):** la valoración base **NO contempla kilometraje real, equipamiento/accesorios extra ni estado general** del vehículo; solo marca/modelo/versión/antigüedad. El ajuste por km se hace con la tabla promedio aparte; el GANVAM-DAT sí incorpora km/equipamiento/estado. `[VERIFICADO]`

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| App móvil | "GANVAM Valores VO" — Android (Google Play, 5.000+ descargas), iOS, APK directo. Login de asociado. | `[VERIFICADO]` |
| Portal web de asociado | **Mi GANVAM** — área privada: descarga de informes/facturas, detalle de operaciones, **monedero virtual**, pago de cuota. | `[VERIFICADO]` (lanzamiento Mi GANVAM) |
| Dashboard web | "Aplicación Informes Dashboard VN y VO" (interactivo) + "Aplicación Ideauto". | `[VERIFICADO]` |
| Boletines | Publicaciones digitales/PDF tras login de asociado. | `[VERIFICADO]` |
| Tienda online | Compra por unidad: INTEVES, valores >12 años, Boletín VN, Estadísticas a Medida. | `[VERIFICADO]` |
| Plataforma GANVAM-DAT | Web multidispositivo (sin instalación), **carga masiva por lotes** de inventario, identificación VIN/matrícula. Acceso B2B vía **demo/contacto comercial** (formulario lead-gen). | `[VERIFICADO]` |
| API / integración DMS | **NO documentada públicamente** en las páginas de GANVAM ni de GANVAM-DAT. DAT Group ofrece APIs en otros productos (weDAT/SilverDAT), por lo que es plausible vía contrato B2B, pero **no confirmado**. | `[ASUMIDO]` / gap |
| Feed/Excel | "Estadísticas a Medida" sugiere entrega de datos personalizados; formato exacto no publicado. | `[ASUMIDO PARCIAL]` |

---

## 6. Precio (modelo)

- **Modelo dominante:** acceso **incluido en la cuota de asociado** (la mayoría de boletines, app y datos de mercado son "solo para afiliados"). `[VERIFICADO]`
- **Pago por unidad:** tienda online para INTEVES, valores >12 años, estadísticas a medida — **precios concretos no publicados** (tras login/checkout). `[VERIFICADO]` (existencia) / `[NO VERIFICADO]` (importes).
- **GANVAM-DAT (B2B):** **presupuesto/demo a medida**; sin tarifa pública. `[VERIFICADO]` (gated por formulario).
- **App:** descarga gratuita; contenido restringido a asociados. `[VERIFICADO]`
- **Conclusión:** pricing **opaco**, no self-serve, orientado a membresía + venta consultiva. `[VERIFICADO]`

---

## 7. Placement — DÓNDE se coloca cada dato (patrón a copiar por cardeep)

| Dato/métrica | Ubicación en UI/pantalla | Estado |
|---|---|---|
| `marca`/`modelo`/`versión`/`antigüedad` | **Pantalla de búsqueda** de la app (selección táctil paso a paso) | `[VERIFICADO]` |
| `valor de mercado VO` | **Pantalla de resultado** de la app, tras seleccionar criterios | `[VERIFICADO]` |
| Inventario propio + valor | Módulo **gestión de stock** dentro de la app | `[VERIFICADO]` |
| `Periodo/Marca/Tipo/Modelo/Año` (motos) | **Filtros** superiores de la tabla web de consulta | `[VERIFICADO]` |
| `Modelo / Tipo / Valor` (motos) | **Columnas de la tabla** de resultados web | `[VERIFICADO]` |
| Identificación VIN/matrícula + datos técnicos + equipamiento | **Ficha de vehículo** del GANVAM-DAT tras IdentifyVIN | `[VERIFICADO]` (descrito) |
| `valor de venta` y `valor de compra` | Bloque de valoración de la **ficha** GANVAM-DAT (par retail/trade) | `[VERIFICADO]` |
| `valor residual %` / depreciación | Salida del **Índice GANVAM-DAT** asociada a la ficha | `[VERIFICADO]` |
| Stock completo valorado | **Vista de lista/lote** tras carga masiva (uso fiscal/contable) | `[VERIFICADO]` (descrito) |
| Matriculaciones / transferencias / bajas | **Dashboard VN/VO** (interactivo) y boletines descargables, segmentado por provincia/marca/municipio/CP | `[VERIFICADO]` |
| `precio medio`, `retención %`, `rotación` | **Notas de prensa / informes de tendencias** (nivel mercado, no per-vehículo) | `[VERIFICADO]` |
| Informes/facturas/operaciones/monedero | Área privada **Mi GANVAM** (panel de cuenta del asociado) | `[VERIFICADO]` |
| Productos de pago (INTEVES, >12 años) | **Tienda online** (catálogo + checkout) | `[VERIFICADO]` |

**Patrón clave para cardeep:** valoración VO presentada como **par venta/compra (retail/trade)** sobre una **ficha identificada por VIN** con equipamiento y datos técnicos; el **valor residual %** y la depreciación cuelgan de esa ficha; las métricas de mercado (precio medio, retención, rotación) viven en un **plano agregado** (dashboard/informe), separadas del per-vehículo. La búsqueda VO de consumidor/profesional es **embudo marca→modelo→versión→antigüedad → 1 valor**.

---

## 8. Diferencial (lo que ofrece y casi nadie más)

1. **Estatus de referencia institucional/oficial en España:** aceptado por **Hacienda** (base ITP, modelo 620), **DGT**, **aseguradoras**, **tribunales/peritos**, **administraciones públicas** y el **Consorcio de Compensación de Seguros**. Es el "valor venal" de facto. `[VERIFICADO]`
2. **Serie histórica desde 1966** (>50 años) → prestigio y profundidad temporal difícil de replicar. `[VERIFICADO]`
3. **Grounding en transacciones reales** profesional→cliente final (~8.000/mes, ~800 empresas), no solo anuncios. `[VERIFICADO]`
4. **Índice neutral GANVAM-DAT** que fusiona transacciones reales + ofertas online + IA + variables EV (salud/estrés de batería, carga, telemática) + señales de mercado (rotación, demanda por canal). `[VERIFICADO]`
5. **Amplitud de tipologías:** coches, motos, ciclomotores, quads, microcoches, tractores, industriales. `[VERIFICADO]`
6. **Doble cara venta/compra (retail/trade)** + identificación VIN con equipamiento, vía la red DAT. `[VERIFICADO]`
7. **Cobertura geográfica fina** (provincia/municipio/CP) para matriculaciones y transferencias. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece / límites)

1. **Solo España.** Sin cobertura pan-europea. `[VERIFICADO]`
2. **Tablas base ignoran km, equipamiento y estado** (solo marca/modelo/versión/antigüedad); el ajuste fino requiere el producto GANVAM-DAT aparte. `[VERIFICADO]`
3. **Sin API pública / acceso self-serve para desarrolladores** documentado. Todo gated por membresía o demo B2B. `[ASUMIDO fuerte]` (no hallada documentación de API)
4. **Sin historial per-VIN propio** (siniestros, ITV, kilometraje histórico). Lo más cercano es **INTEVES**, que es un **passthrough de la DGT**, no dato propietario. `[VERIFICADO]`
5. **Sin métrica per-listing de days-to-sell / market days supply** productizada: la rotación se trata a nivel mercado, no por vehículo individual. `[VERIFICADO]`
6. **Sin producto público de scraping/feed de anuncios** independiente: los precios de oferta online alimentan el índice pero no se exponen como dataset propio. `[ASUMIDO]`
7. **Precio totalmente opaco**, no transparente, no autoservicio. `[VERIFICADO]`
8. **Mayoría de datos tras login** → poca apertura de datos abiertos. `[VERIFICADO]`
9. **Ajuste por daño/estado** no integrado en la valoración base (se externaliza a herramientas DAT como FastTrackAI/weDAT). `[VERIFICADO]`
10. **Distinción Blanco/Azul no documentada públicamente con precisión** (contenido de asociado) → riesgo de reproducir mal el matiz sin acceso. `[GAP de verificación]`

---

## 10. Fuentes (URLs)

**First-party GANVAM**
- https://www.ganvam.es/ (home, identidad, menú)
- https://ganvam.es/servicios/ (catálogo completo de servicios)
- https://ganvam.es/datos-mercado-vn-y-vo/ (campos de datos de mercado — render verificado)
- https://ganvam.es/boletines-valores-vo/ (boletines VO)
- https://ganvam.es/afiliados/publicaciones-afiliados/boletines-estadisticos/ (boletines estadísticos)
- https://ganvam.es/motos-boletin-blanco/ (estructura de tabla: filtros + columnas — render verificado)
- https://ganvam.es/libro-blanco-ganvam/ (Libro Blanco)
- https://ganvam.es/servicios/aplicacion-ganvam-valores-vo-dispositivos-moviles/ (app valoración)
- https://ganvam.es/el-hibrido-no-enchufable-la-propulsion-que-mas-valor-retuvo-en-2025-con-un-precio-medio-de-21-350-euros/ (métricas de mercado 2025)
- https://ganvam.es/el-vehiculo-seminuevo-ajusta-su-precio-un-10-en-el-ultimo-ano-por-la-presion-competitiva-de-las-nuevas-marcas/ (métricas precio/retención)
- https://play.google.com/store/apps/details?id=com.ganvam.app (ficha oficial app: 1966, 8.000 datos/mes, 5.000+ descargas — render verificado)

**First-party GANVAM-DAT / DAT Ibérica**
- https://discover.datiberica.com/ (catálogo DAT Ibérica: fastVO, weDAT, FastrackAI, fastEQUIPMENT, SilverDAT, Valoración de Stock)
- https://discover.datiberica.com/valoracion-de-stock-vehiculos/ (GANVAM-DAT Valoración de Stock — render verificado, CIF B62394762)
- https://discover.datiberica.com/fastvo/ (motor VO de DAT)

**Terceros / prensa (verificación cruzada)**
- https://autospare.es/motor/acuerdo-ganvam-y-dat/ (acuerdo GANVAM-DAT 2024, % residuales, variables)
- https://renting-automocion.com/20715-2/ y https://autoreport.es/20715-2/ (GANVAM-DAT "libro electrónico", parámetros)
- https://www.posventa.com/texto-diario/mostrar/5899895/ (Índice GANVAM-DAT: variables, grupos usuarios, DANA/Consorcio)
- https://www.posventa.com/texto-diario/mostrar/5864676/ (precio seminuevo -10%)
- https://www.motor.mapfre.es/coches/noticias-coches/ganvam-que-es/ (campos tablas, límites)
- https://www.aeplustest.es/valor-venal-de-un-vehiculo-para-hacienda-y-la-dgt-tablas-y-calculo/ (valor venal, BOE, ITP)
- https://www.allianz.es/descubre-allianz/mediadores/diccionario-de-seguros/g/que-es-ganvam.html (definición sector seguros)
- https://www.cogitival.es/.../servicio-de-consulta-de-valoracion-de-vehiculos-de-plataforma-ganvam (uso por peritos/colegiados)

---

## 11. Resumen para schema

- **slug:** `ganvam`
- **subdominio:** `valuation`
- **productos:** 13 (núcleo: App/Boletín Valores VO, GANVAM-DAT Valoración de Stock, Datos Mercado VN/VO, Boletines Blanco/Azul, Tabla km, Buscador matrículas, INTEVES, Baremos, Informes de tendencias).
- **diferencial central:** referencia OFICIAL de valor venal en España (Hacienda/DGT/seguros/tribunales) + índice neutral GANVAM-DAT con IA y variables EV, sobre transacciones reales desde 1966.
- **gap central para cardeep:** sin API pública, sin historial per-VIN propio, sin days-to-sell per-vehículo, solo España, pricing opaco.
