# ANFAC — Auditoría atómica de inteligencia de automoción

> **Slug:** `anfac` · **Web:** https://anfac.com/ · **Subdominio (categoría cardeep):** `official-data`
> **Auditado:** 2026-06-30 · **Confianza global:** ALTA en identidad/productos/campos · MEDIA en placement granular de tablas online (render dinámico) y en precio del dato detallado (vía IDEAUTO, opaco).
> **Convención:** cada afirmación va marcada `[VERIFICADO]` (leído en fuente) o `[ASUMIDO]` (inferencia declarada). Nunca se presenta un asumido como verificado.
> **Método:** WebSearch + WebFetch intensivo (20+ páginas/PDFs). No había servidor MCP de Exa registrado en el entorno; se usó WebSearch/WebFetch (consistente con auditorías peer). Los PDFs de ANFAC devuelven binario no parseable vía WebFetch; los campos provienen de las **páginas HTML de nota de prensa** (que reproducen las cifras) y de las páginas de producto, no se inventó ningún dato.

---

> **NOTA CRÍTICA DE NATURALEZA (leer primero).**
> ANFAC **NO es una empresa de datos/tasación al uso** (no es Autovista, ni Schwacke, ni una valoración VO, ni un decodificador VIN, ni un historial de vehículo). Es la **patronal/asociación de los FABRICANTES** de automóviles y camiones de España. Su "producto de datos/inteligencia" es un **cuerpo de estadística sectorial oficial y de facto** (matriculaciones, producción, exportación, parque, comercio exterior, electromovilidad, logística) que el Gobierno, las administraciones, los medios y todo el sector citan como **fuente de referencia del país**. El motor estadístico que ANFAC publica lo elabora **IDEAUTO** (Instituto de Estudios de Automoción) a partir de datos de la **DGT**; IDEAUTO es la misma tubería que alimenta a GANVAM y FACONAUTO (fuente unificada de matriculaciones). `[VERIFICADO]`
> **Implicación para cardeep:** ANFAC aporta el **plano AGREGADO de mercado** (cuántos coches se matriculan/producen/exportan, por marca, por canal, por CCAA, por tecnología; estado del parque; red de recarga), NO el plano per-punto-de-venta ni per-vehículo. Es "verdad de denominador" (totales de mercado contra los que normalizar), no "huella digital de dealer".

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Nombre completo | **Asociación Española de Fabricantes de Automóviles y Camiones** | `[VERIFICADO]` |
| Marca corta | **ANFAC** | `[VERIFICADO]` |
| Naturaleza | **Asociación empresarial sin ánimo de lucro** (patronal de fabricantes). NO sociedad mercantil de datos. | `[VERIFICADO]` quienes-somos |
| Fundación | **1977** (al amparo de la Ley 19/1977, de 1 de abril, de regulación del derecho de asociación sindical) | `[VERIFICADO]` |
| HQ | **Madrid** (sede social) | `[VERIFICADO]` |
| Director General | **José López-Tafall** (DG desde ~2020, sustituyó a Mario Armero) | `[VERIFICADO]` (LinkedIn + elEconomista + portal-transparencia) |
| Presidente | **Markus Haupt** (CEO de SEAT/CUPRA), nombrado presidente **19-jun-2026** (sucede a Wayne Griffiths) | `[VERIFICADO PARCIAL]` (homepage; nombramiento reciente) |
| Nº de asociados | **57–60+ marcas** miembro (fabricantes de vehículos, motores, componentes + marcas comercializadoras). Absorbió a **ANIACAM** (importadores) | `[VERIFICADO]` (la cifra varía entre páginas: "57 marcas" / "más de 60") |
| Afiliación europea | Miembro de **ACEA** (patronal europea de fabricantes) | `[VERIFICADO]` |
| Afiliación nacional | Miembro de **CEOE** | `[VERIFICADO]` |
| Registro de Transparencia UE | ID **814112514572-47** | `[VERIFICADO]` quienes-somos |
| Idioma web | ES (algunas publicaciones EN) | `[VERIFICADO]` |
| Motor de datos | **IDEAUTO** (Instituto de Estudios de Automoción) — elabora la estadística a partir de **DGT** | `[VERIFICADO]` (fuente citada bajo cada tabla) |

**Misión declarada (verbatim resumido):** "fomentar el adecuado desarrollo del Sector de Automoción contribuyendo a los intereses generales del país"; investiga, profundiza el conocimiento y difunde información técnica/económica/social del sector; asume la representación colectiva de sus asociados ante administraciones y entidades públicas/privadas. `[VERIFICADO]`

**Gobernanza:** Asamblea de socios · **Junta Directiva** (CEOs de las marcas: Manuel Terroba, Jesús Alonso, Leopoldo Satrústegui, Emilio Herrera, Markus Haupt, José María Galofré, etc.) · **Comité de Dirección**. Portal de Transparencia público (quiénes somos, junta directiva, comité de dirección). `[VERIFICADO]`

**Miembros (muestra verificada):** Volkswagen, SEAT, CUPRA, Audi, Mercedes-Benz, BMW, Renault, Dacia, Alpine, Stellantis (Peugeot, Citroën, Opel, Fiat, Abarth, Alfa Romeo, Jeep, Lancia, DS), Ford, Hyundai, Kia, Nissan, Toyota, Porsche, Volvo, BYD, XPeng, IVECO, **Volvo Trucks, Scania** (vehículo industrial), etc. `[VERIFICADO]` (homepage + quienes-somos)

---

## 2. Cobertura

- **País:** **España exclusivamente** (es la patronal nacional; el plano europeo lo cubre ACEA, de la que es miembro). `[VERIFICADO]`
- **Granularidad geográfica:** nacional · **Comunidad Autónoma (CCAA)** · **provincia** (las 50 + Ceuta/Melilla). El Barómetro de Electromovilidad añade objetivos **por provincia y por CCAA**. `[VERIFICADO]`
- **Scope nuevo/usado:** núcleo en **vehículo NUEVO** (matriculaciones = ventas de unidades nuevas; producción; exportación). El **usado** no es producto propio de ANFAC (la transferencia/VO la trabajan GANVAM/IDEAUTO); ANFAC sí publica el **PARQUE circulante** (stock total, incluye todas las edades). `[VERIFICADO]`
- **Tipos de vehículo:** **turismos y todoterrenos (4x4/SUV)** · **vehículos comerciales ligeros (VCL)** · **vehículos industriales (camiones)** · **autobuses y microbuses**. (Motos/ciclomotores NO son scope ANFAC — eso es ANESDOR.) `[VERIFICADO]`
- **Motorizaciones cubiertas:** gasolina, diésel, gas (GLP/GNC), híbrido (HEV), híbrido enchufable (PHEV), eléctrico puro (BEV), pila de combustible; agregados "electrificados" (BEV+PHEV) y "alternativos". `[VERIFICADO]`
- **Profundidad temporal:** series mensuales y anuales; Informe Anual publicado **desde 1977** (hay Informe Anual 1977 en el archivo). `[VERIFICADO]`

---

## 3. Productos + campos atómicos

> ANFAC organiza su "producto de datos" en dos grandes contenedores web: **Cifras Clave** (tablas vivas de mercado/producción, fuente IDEAUTO) y **Publicaciones** (informes/barómetros/PDF). Abajo, cada producto con su lista atómica de campos. Nombres de métrica conservados como aparecen en fuente.

### P1 — Matriculaciones de Turismos y Todoterrenos *(Cifras Clave · fuente IDEAUTO)* — **núcleo**
La cifra-faro del país (ventas de coche nuevo). `[VERIFICADO]`
- **Dimensiones/tablas:** `últimos 12 meses` · `resumen mensual + acumulado del año` · `top ventas del mes` · `top ventas del año`.
- **Desgloses:** por `marca` · por `modelo` (rankings de superventas) · por `CCAA` · por `provincia` · por **canal de venta**: `particulares` · `empresas` · `alquiladores (rent-a-car)`.
- **Por tecnología/combustible:** `gasolina` · `diésel` · `gas (GLP/GNC)` · `HEV` · `PHEV` · `BEV` · `electrificados (BEV+PHEV)` · `alternativos`.
- **Métricas por celda:** `unidades matriculadas` · `variación % interanual` · `cuota de mercado %` · `acumulado YTD` · **`emisiones medias de CO₂ (g/km)`** del conjunto matriculado.
- **Ejemplos verificados (2025 cierre):** total turismos **1.148.650** (+12,9%); particulares **539.642** (+18,1%), empresas **418.574** (+12,0%), alquiladores **190.434** (+2,3%); electrificados **225.617** (cuota **19,6%**, +94,6%); CO₂ medio **103 g/km** (−10,81%). `[VERIFICADO]`
- **Nº campos atómicos:** ~14.

### P2 — Matriculaciones de Vehículos Comerciales Ligeros (VCL) *(Cifras Clave · IDEAUTO)*
Misma estructura que P1. `[VERIFICADO]`
- `unidades` · `marca` · `modelo` · `CCAA` · `provincia` · `variación %` · `cuota %` · `acumulado` · top ventas mes/año · `últimos 12 meses`.
- **Nº campos:** ~10.

### P3 — Matriculaciones de Vehículos Industriales, Autobuses y Microbuses *(Cifras Clave · IDEAUTO)*
- Segmentos: `vehículo industrial (camión)` · `autobús` · `microbús` (subdivisión por tonelaje/uso). `unidades` · `marca` · `CCAA`/`provincia` · `variación %` · `cuota %` · `acumulado` · top mes/año. `[VERIFICADO]`
- **Nº campos:** ~9.

### P4 — Producción y Exportación *(Cifras Clave · fuente ANFAC propia, datos de fábricas miembro)*
El otro pilar (lado oferta industrial). `[VERIFICADO]`
- **Producción:** `unidades producidas` (total) · por `tipo` (turismos vs comerciales+industriales) · `producción de alternativos/electrificados` (unidades + `cuota % sobre producción`) · `mensual` · `acumulado` · `variación %`.
- **Exportación:** `unidades exportadas` · `cuota exportada a Europa %` · **`destinos de exportación` por país** (`unidades` + `% sobre exportación total`).
- **`MAPA DE FÁBRICAS con modelos en producción y adjudicados`** — visual interactivo: por **planta/fábrica** (17 fábricas) → `modelos` × `tipo de propulsión (BEV/PHEV/HEV)`. `[VERIFICADO]`
- **Ejemplos verificados (2025):** producción total **2.274.026** (−4,3%); turismos **1.810.331** (−5,7%); comerciales+industriales **463.695** (+1,2%); exportación **1.950.103** uds (−8,2%), Europa **92,6%**; destinos: Alemania **340.179** (17,4%), Francia **337.166** (17,3%), R.Unido **240.826** (12,3%); producción de alternativos **891.290** (+26,1%, **39,2%** del total). `[VERIFICADO]`
- **Nº campos atómicos:** ~14.

### P5 — Barómetro de Electromovilidad *(Publicación trimestral · base 100)* — **el más rico en indicadores compuestos**
Mide penetración de electrificados + desarrollo de la red de recarga; distancia a objetivo **2030 (Fit for 55)**. `[VERIFICADO]`
- **`Indicador global de electromovilidad`** (0–100) = media de los dos siguientes. *(Q1-2026: **25,4**, +1,6 pts.)*
- **`Indicador de penetración de vehículo electrificado`** (0–100). *(Q1-2026: **35,9**, +2,5 pts; media UE **46,3**.)*
- **`Indicador de infraestructura de recarga`** (0–100). *(Q1-2026: **14,8**, +0,7 pts; media UE **29,6**.)*
- **Red de recarga:** `puntos de recarga públicos totales` (Q1-2026: **55.077**) · `nuevos puntos en el trimestre` (**2.005**, +3,8%) · **`puntos instalados pero inoperativos`** (**17.073**, **25%** del total) · `potencial total si operativos` (**72.150**) · `puntos por potencia` (ultra-alta **≥250 kW**: 309 nuevos; alta `>150 kW`; rápida; lenta).
- **Mercado:** `cuota de mercado de electrificados %` (Q1-2026: **19,1%**) · `unidades electrificadas matriculadas` (~68.627) · `distancia a la media UE` (−10,4 pts).
- **Objetivos:** `objetivo de potencia/infra por provincia y por CCAA` · `% de cumplimiento del objetivo` (Q1: 62% del objetivo de potencia; 18 provincias cumplen, 12 por debajo del 50%). **Límite del indicador a máximo 100 pts** (actualización metodológica). `[VERIFICADO]`
- **Nº campos atómicos:** ~16.

### P6 — Barómetro sobre Vehículo Autónomo y Conectado (VA/VC) *(Publicación anual; "único en Europa")*
4ª–5ª edición (2024/2025). Spain vs mundo. `[VERIFICADO]`
- **`Indicador de entorno/ambiental`** (0–100) comparando España con otros países en factores que condicionan el VA/VC. *(España **50,5**; EE.UU. **67,8**, Suecia **63,3**, Finlandia **62,5**.)*
- **`Priorización de tecnología de conectividad`** (encuesta a fabricantes: qué aspectos de conectividad pesan más según necesidad de cliente).
- **`Funcionalidades de conectividad incorporadas en la oferta`** — `% de vehículos ofertados que incluyen cada funcionalidad`, distinguiendo **`de serie` vs `opcional`**.
- **Análisis de situación** de VA/VC en España (regulación, infraestructura, conectividad, entorno). `[VERIFICADO]`
- **Nº campos atómicos:** ~6 (+ ranking de países).

### P7 — Informe del Parque de Vehículos *(Publicación anual ANFAC-IDEAUTO, fuente DGT)*
Estado del stock circulante (todas las edades). `[VERIFICADO]`
- `parque total de vehículos` (2025: **31.706.927**, +1,3%).
- **`edad media`** por tipo: turismos **14,6 años** · VCL **14,8** · industriales **15** · autobuses **11,1**.
- **`distribución por antigüedad`**: `0–10 años` (38%) · `>10 años` (62%) · `>15 años` (~13 M uds) · **`>20 años`** (9,28 M, **29,3%**, +7,2%).
- **`reparto por distintivo ambiental DGT`**: `Etiqueta CERO` (2,3%, +50,9%) · `ECO` (7,3%, +29,1%) · `C` · `B` · `sin etiqueta` (24,5%, 7,75 M, −7,8%).
- **`composición por combustible`**: diésel (57,1%, 18,1 M, −1,8%) · gasolina (33,2%) · electrificados PHEV/BEV (2,4%, 746.510, +50,8%).
- **Desglose por `CCAA`/`provincia`** (p.ej. Madrid 11,5 años, Andalucía 15). `[VERIFICADO]`
- **Nº campos atómicos:** ~13.

### P8 — Balanza Comercial de la Automoción / Comercio Exterior *(Publicación mensual)*
Aportación del sector al comercio exterior. `[VERIFICADO]`
- **Vehículos:** `exportaciones (€)` · `importaciones (€)` · `saldo comercial (€)` · `variación %`.
- **Vehículos + componentes (agregado):** `exportaciones (€)` · `importaciones (€)` · `saldo total (€)`.
- `aportación al saldo de la balanza comercial española` · series `mensual` / `semestral` / `anual`.
- **Ejemplos verificados (2025):** export. vehículos **39.062 M€** (−7,8%), import. **28.871 M€** (+9,4%), saldo vehículos **10.190 M€** (−36,3%); vehículos+componentes export. **50.586 M€**, import. **45.764 M€**, saldo total **4.822 M€** (−53,4%). `[VERIFICADO]`
- **Nº campos atómicos:** ~9.

### P9 — Valoración de la Logística de Vehículos *(Publicación anual; informes por modo)*
Cómo se mueve el vehículo fabricado/importado. `[VERIFICADO]`
- `vehículos totales transportados` (2024: **4,78 M**, −3,8%).
- **`cuota modal`**: `carretera %` (34,1%) · `ferrocarril %` (14%, +0,8 pp) · `marítimo %` (51,9%, −3,2 pp).
- `volúmenes por modo`: `nº camiones` (215.000) · `nº trenes` (2.500) · `vehículos por puerto/barco` (2,5 M).
- Informes específicos: **Valoración de la Logística por Carretera** · **Valoración de la Logística del Transporte Ferroviario** · análisis de puertos. `[VERIFICADO]`
- **Nº campos atómicos:** ~8.

### P10 — Informe Anual *(Publicación anual; foto macro del sector)*
Cuenta de resultados del sector. `[VERIFICADO]`
- `facturación del sector (€)` (2024: **76.855 M€**, −2%) · `empleo directo` (57.189) · `producción (uds)` (2.376.504) · **`inversión en I+D (€)`** (2.434 M€, +2,6%) · `aportación al Estado (€)` (39.838 M€, +1,7%) · `ranking de producción` (2º de Europa, Top-10 mundial) · `contribución al PIB %` (~7,7% del homepage). `[VERIFICADO]`
- **Nº campos atómicos:** ~7.

### P11 — Plan España Auto 2030 *(documento estratégico / hoja de ruta — KPIs OBJETIVO, no dato vivo)*
Plan de reindustrialización. `[VERIFICADO]` (se marca como **metas**, no estadística observada)
- 25 medidas en 3 ejes (industria · mercado · innovación) + 5+1 medidas estrella.
- `valor del sector objetivo` 85.000 → **120.000 M€** · `empleo objetivo` **1,9 M** · `producción objetivo` **2,7 M** uds · `cuota de producción electrificada objetivo` ≥**40%** (2030) · `100% eléctrico 2035` · `inversión pública` **6.000 M€**/5 años + `privada` ~**40.000 M€** · `objetivos anuales de infraestructura de recarga` nacional/regional/provincial. `[VERIFICADO]`
- **Nº campos (KPIs objetivo):** ~8.

### P12 — Position Papers / Otras publicaciones *(documentos de posición; cualitativo)*
Posicionamiento regulatorio (fiscalidad, ayudas, MOVES, etiquetado, normativa). No dataset estructurado. `[VERIFICADO]` (existencia de la categoría)

---

## 4. Metodología y fuentes de datos

- **Matriculaciones (P1–P3):** las elabora **IDEAUTO** (Instituto de Estudios de Automoción) a partir del registro de la **DGT**; es la **fuente unificada** acordada por **ANFAC + GANVAM + FACONAUTO** para Gobierno, administraciones, medios y sector. `[VERIFICADO]`
- **Producción/Exportación (P4):** dato propio de ANFAC agregado de sus **fábricas asociadas** (17 plantas). Fuente citada: "ANFAC". `[VERIFICADO]`
- **Parque (P7):** ANFAC-IDEAUTO sobre **datos de la DGT** del parque registrado. `[VERIFICADO]`
- **Comercio Exterior (P8):** sobre datos oficiales de aduanas/comercio exterior (DataComex/Aduanas) reelaborados por ANFAC. `[ASUMIDO]` (origen estadístico oficial; ANFAC no detalla el dataset exacto en la nota).
- **Barómetro Electromovilidad (P5):** metodología propia **base 100**; índice = media de penetración + infraestructura; objetivos calibrados al paquete **Fit for 55** y, tras actualización, **objetivos específicos por CCAA**; subindicadores topados a 100. Datos de recarga de fuentes de red + matriculación de IDEAUTO. `[VERIFICADO]` (metodología) / `[ASUMIDO]` (proveedor exacto de puntos de recarga).
- **Barómetro VA/VC (P6):** **encuesta a fabricantes** (priorización/funcionalidades) + indicador de entorno comparado internacionalmente. `[VERIFICADO]`
- **Logística (P9):** valoración propia con datos de operadores logísticos/modos de transporte. `[VERIFICADO PARCIAL]`
- **Frecuencias:** matriculaciones y producción/exportación **mensuales**; comercio exterior **mensual**; barómetro electromovilidad **trimestral**; parque, informe anual, VA/VC, logística **anuales**. `[VERIFICADO]`
- **Limitación metodológica:** ANFAC publica **agregados** (no microdato per-vehículo ni per-concesionario). El detalle granular comercializable (series finas, datos a medida) se canaliza por **IDEAUTO** como servicio de pago, no por la web pública de ANFAC. `[VERIFICADO/ASUMIDO]`

---

## 5. Entrega (delivery)

| Canal | Detalle | Estado |
|---|---|---|
| Web pública "Cifras Clave" | Tablas online vivas (matriculaciones, producción/exportación) + **mapa de fábricas** interactivo. Render dinámico. | `[VERIFICADO]` |
| Notas de prensa (HTML + PDF) | Cada cifra mensual se publica como **nota de prensa** (página HTML con las tablas + PDF descargable). Núcleo de difusión. | `[VERIFICADO]` |
| Publicaciones (PDF) | Repositorio filtrable por categoría (Informe Anual, Barómetros, Comercio Exterior, Logística, Parque, Plan 2030, Position Papers) + buscador + rango de fechas; **32 páginas** de histórico. Todo **PDF descargable gratis**. | `[VERIFICADO]` |
| Sala de Prensa / Eventos | Calendario de prensa, contacto de medios, **#MOBILITYTALKS**, foros (Foro Vehículo Industrial y Bus), presentaciones de barómetros. | `[VERIFICADO]` |
| Blog | Comentario de tendencias/tecnología. | `[VERIFICADO]` |
| Portal de Transparencia | Quiénes somos, junta directiva, comité de dirección, cuentas. | `[VERIFICADO]` |
| Área de socios (login) | Acceso privado para asociados (portal de miembro). | `[VERIFICADO]` (existe link de login) |
| Dato granular / a medida | Vía **IDEAUTO** (servicio comercial de estadística de automoción), **fuera** de la web ANFAC. | `[ASUMIDO]` (IDEAUTO es entidad de servicios de datos; ANFAC es el escaparate público) |
| **API pública / feed / Excel self-serve** | **NO documentada** en ANFAC. La difusión es PDF + tablas web + nota de prensa. | `[VERIFICADO]` (ausencia) / gap |

---

## 6. Precio (modelo)

- **Dato público = GRATIS.** Matriculaciones, producción/exportación, barómetros, parque, comercio exterior, informe anual, Plan 2030: **descarga libre** en anfac.com sin login ni pago. Es difusión institucional, no producto comercial. `[VERIFICADO]`
- **Pertenencia:** acceso/servicios de asociado **incluidos en la cuota de socio** (solo fabricantes/marcas elegibles). `[VERIFICADO/ASUMIDO]`
- **Dato granular comercializado:** las series finas/a medida se venden a través de **IDEAUTO** — **tarifa no pública**. `[ASUMIDO]` (modelo del Instituto; no publicado en ANFAC).
- **Conclusión:** modelo **freemium institucional** — agregados abiertos gratis (alto valor de marca/SEO/citación) + detalle premium opaco vía IDEAUTO. NO hay self-serve de pago en ANFAC. `[VERIFICADO]`

---

## 7. Placement — DÓNDE se coloca cada dato (patrón a observar por cardeep)

> ANFAC NO tiene "ficha de coche" ni "ficha de dealer": su unidad es **el agregado de mercado/país**. El patrón de placement es **"sección temática → tabla/indicador + nota de prensa narrativa + PDF"**. Relevante para cardeep como modelo de cómo presentar **totales de mercado** que sirvan de denominador/contexto.

| Dato / métrica | Ubicación en UI/web | Estado |
|---|---|---|
| Matriculaciones turismos (unidades, marca, modelo, canal, CCAA) | **Cifras Clave → "Matriculaciones Turismos y Todoterreno"** (tablas: últimos 12 meses / mes+acumulado / top mes / top año) | `[VERIFICADO]` |
| Matriculaciones VCL e industriales/bus | **Cifras Clave** (subsecciones por tipo, misma estructura) | `[VERIFICADO]` |
| Producción y exportación (uds, destinos, electrificados) | **Cifras Clave → "Producción y exportación"** + **MAPA DE FÁBRICAS** (planta × modelo × propulsión) | `[VERIFICADO]` |
| Cifra mensual + variación + ranking | **Nota de prensa** (página HTML por mes) con tablas embebidas | `[VERIFICADO]` |
| Indicadores de electromovilidad (global/penetración/recarga) | **Publicaciones → Barómetro Electromovilidad** (PDF trimestral) + presentación en evento | `[VERIFICADO]` |
| Puntos de recarga por potencia/CCAA, inoperativos | Dentro del **Barómetro Electromovilidad** (gráficos por CCAA/provincia) | `[VERIFICADO]` |
| Edad media del parque, antigüedad por CCAA, etiquetas | **Publicaciones → Parque Vehículos** (PDF anual ANFAC-IDEAUTO) | `[VERIFICADO]` |
| Saldo/exportaciones/importaciones € | **Publicaciones → Comercio Exterior / Balanza Comercial** (PDF mensual) | `[VERIFICADO]` |
| Cuota modal logística (carretera/tren/barco) | **Publicaciones → Logística** (PDF anual + por modo) | `[VERIFICADO]` |
| Facturación, empleo, I+D, aportación al Estado | **Publicaciones → Informe Anual** (PDF) | `[VERIFICADO]` |
| KPIs objetivo 2030 | **Publicaciones → Plan España Auto 2030** (PDF + presentaciones por CCAA) | `[VERIFICADO]` |
| Gobernanza, miembros, cuentas | **Portal de Transparencia** | `[VERIFICADO]` |

**Patrón clave para cardeep:** el dato de mercado se ancla en una **sección temática estable** (URL persistente tipo `/cifras-clave/matriculaciones-...`) que muestra **4 vistas canónicas** (serie 12m · mes+acumulado · top del mes · top del año) y **cada actualización engendra una nota de prensa fechada** (excelente para SEO y para timeline histórico). La inteligencia compuesta (índices 0–100, objetivos) vive en **barómetros PDF** separados del dato bruto. Es la separación "dato vivo (tablas) vs. análisis (barómetro/informe)".

---

## 8. Diferencial (lo que ofrece y casi nadie más)

1. **Autoridad institucional de denominador nacional:** la fuente de matriculaciones (vía IDEAUTO, unificada ANFAC+GANVAM+FACONAUTO) que cita el Gobierno, el INE-adyacente, los medios y todo el sector. Es "la cifra oficial de ventas de España". `[VERIFICADO]`
2. **Lado OFERTA industrial** que las tasadoras no tienen: **producción por fábrica/modelo/propulsión + exportación por país de destino**. Casi nadie publica el "mapa de fábricas con modelos adjudicados". `[VERIFICADO]`
3. **Barómetro de Electromovilidad** con índice compuesto base-100 y **objetivos por provincia/CCAA** ligados a Fit for 55, incluyendo **puntos de recarga inoperativos** (métrica de calidad de red que pocos exponen). `[VERIFICADO]`
4. **Barómetro VA/VC "único en Europa"** (vehículo autónomo/conectado) con benchmark internacional. `[VERIFICADO]`
5. **Parque circulante con edad media + etiqueta ambiental por CCAA** (input directo para políticas de achatarramiento/LEZ). `[VERIFICADO]`
6. **Comercio exterior y logística modal** del vehículo — vincula automoción con balanza comercial y transporte. `[VERIFICADO]`
7. **Acceso abierto y gratuito** al agregado, con histórico desde 1977 → profundidad temporal y citabilidad. `[VERIFICADO]`
8. **Canal de venta (particular/empresa/alquilador)** en matriculaciones — segmentación de demanda que cardeep puede usar como contexto. `[VERIFICADO]`

---

## 9. Gaps (lo que NO ofrece — clave para cardeep)

1. **NO es censo de PUNTOS DE VENTA / concesionarios.** No hay directorio de dealers, ni huella digital, ni inventario por punto de venta, ni `cdp_code`. Trabaja a nivel **marca/mercado/país**, no per-dealer. (Justo el hueco que cardeep llena.) `[VERIFICADO]`
2. **NO es tasación/valoración.** No da `valor residual %`, `retail/trade price`, `days-to-sell`, `price-to-market`, depreciación, ni precio de un coche concreto. (Eso es GANVAM-DAT/Autovista/Eurotax.) `[VERIFICADO]`
3. **NO es VIN-céntrico.** Sin ficha técnica por VIN, sin decodificador, sin historial per-vehículo (siniestros/km/ITV). `[VERIFICADO]`
4. **NO microdato.** Solo **agregados** (totales por marca/CCAA/canal/tecnología); nada de transacción individual ni anuncio individual. `[VERIFICADO]`
5. **Sin API pública / feed / Excel self-serve.** Entrega = PDF + tablas web + nota de prensa. El dato fino se compra fuera, vía IDEAUTO (opaco). `[VERIFICADO]` (ausencia) / `[ASUMIDO]` (IDEAUTO de pago).
6. **Solo España.** Sin cobertura pan-europea propia (delega en ACEA). `[VERIFICADO]`
7. **Usado limitado.** El VO/transferencias no es producto ANFAC (lo cubren GANVAM/IDEAUTO); ANFAC solo aporta el **parque** (stock), no el flujo de segunda mano ni su precio. `[VERIFICADO]`
8. **Sesgo "fabricante".** Es patronal de OEMs → el dato y el relato sirven al interés de fabricantes (ej. presión pro-ayudas/electrificación); no es un proveedor neutral de datos comerciales. `[VERIFICADO/ASUMIDO]`
9. **PDFs no estructurados para máquina** (la difusión rica está en PDF binario, no en JSON/CSV) → fricción para ingestión automática. `[VERIFICADO]` (los PDFs no parsean limpio).

---

## 10. Fuentes (URLs)

**First-party ANFAC**
- https://anfac.com/ — homepage, navegación, presidente, 7,7% PIB `[VERIFICADO]`
- https://anfac.com/cifras-clave/ — índice de cifras clave, fuente IDEAUTO `[VERIFICADO]`
- https://anfac.com/cifras-clave/matriculaciones-turismos-y-todoterreno/ — tablas de matriculaciones (4 vistas) `[VERIFICADO]`
- https://anfac.com/cifras-clave/produccion-y-exportacion/ — producción/exportación + mapa de fábricas `[VERIFICADO]`
- https://anfac.com/publicaciones/ — repositorio (categorías: Informe Anual, Position Papers, Barómetro Electromovilidad, Plan España Auto 2030, Barómetro VA/VC, Comercio Exterior, Logística, Parque Vehículos, Otras) `[VERIFICADO]`
- https://anfac.com/2025-cierra-con-1-148-650-ventas-de-turismos-un-129-mas-que-2024/ — canales + electrificados + CO₂ `[VERIFICADO]`
- https://anfac.com/la-produccion-de-vehiculos-cae-un-43-en-2025-con-2-274-026-unidades/ — producción/export 2025 + destinos `[VERIFICADO]`
- https://anfac.com/el-primer-trimestre-de-2026-registra-2-005-nuevos-puntos-de-recarga-con-un-total-de-55-077-en-espana/ — indicadores electromovilidad Q1-2026 `[VERIFICADO]`
- https://anfac.com/la-edad-media-de-los-turismos-en-espana-sigue-envejeciendo-hasta-los-146-anos-de-antiguedad/ — parque 2025 (edad, etiquetas, combustible) `[VERIFICADO]`
- https://anfac.com/el-sector-de-la-automocion-alcanzo-los-76-855-millones-de-euros-de-facturacion-en-2024/ — Informe Anual 2024 (facturación, empleo, I+D, aportación) `[VERIFICADO]`
- https://anfac.com/la-balanza-comercial-de-los-vehiculos-tuvo-en-2025-su-peor-registro-desde-2009/ — comercio exterior 2025 `[VERIFICADO]`
- https://anfac.com/el-transporte-de-vehiculos-registra-un-ligero-descenso-del-38-en-2024-con-48-millones-de-unidades-transportadas/ — logística modal 2024 `[VERIFICADO]`
- https://anfac.com/plan-espana-auto-2030-la-hoja-de-ruta-para-reindustrializar-la-automocion-y-situar-espana-a-la-vanguardia-europea/ — Plan 2030 (ejes, KPIs objetivo) `[VERIFICADO]`
- https://anfac.com/portal-de-transparencia/quienes-somos/ — fundación 1977, naturaleza, misión, ACEA, Registro UE `[VERIFICADO]`
- https://anfac.com/portal-de-transparencia/comite-de-direccion/ y /junta-directiva/ — gobernanza `[VERIFICADO]`

**Barómetros / informes (PDF, citados; binario no parseable vía WebFetch)**
- https://anfac.com/wp-content/uploads/2026/04/Barometro-Electromovilidad-ANFAC-1T-2026.pdf
- https://anfac.com/wp-content/uploads/2025/11/Barometro-ANFAC-sobre-Vehiculo-Autonomo-y-Conectado-2025.pdf
- https://anfac.com/wp-content/uploads/2026/02/Informe-ANFAC-Ideauto-Parque-de-Vehiculos-Espana-2025.pdf
- https://anfac.com/wp-content/uploads/2025/12/Plan-Espana-Auto-2030.pdf
- https://anfac.com/wp-content/uploads/2024/10/INFORME-ANFAC-Valoracion-Logistica-por-Carretera-2023.pdf

**Terceros / verificación cruzada**
- https://www.motor.es/que-es/anfac-acea — qué es ANFAC vs ACEA `[VERIFICADO]`
- https://www.autopista.es/noticias-motor/faconauto-se-suma-a-las-estadistica-de-matriculaciones-de-anfac-y-ganvam_125835_102.html — FACONAUTO se une a la fuente unificada `[VERIFICADO]`
- https://www.eleconomista.es/ecomotor/motor/noticias/10356034/02/20/Anfac-elige-a-Jose-LopezTafall-como-nuevo-director-general.html — DG López-Tafall `[VERIFICADO]`
- https://www.ceoe.es/en/partners/current-members/asociacion-espanola-de-fabricantes-de-automoviles-y-camiones-anfac — miembro CEOE `[VERIFICADO]`
- https://www.smartgridsinfo.es/2026/04/13/espana-alcanza-55-077-puntos-recarga-publica-primer-trimestre-2026-segun-anfac — corrobora 55.077 puntos `[VERIFICADO]`
- https://www.mobilitycity.es/informes/barometro-anfac-de-la-electromovilidad/ — descripción del barómetro `[VERIFICADO]`

**Verificación DNS**
- `nslookup official-data.anfac.com` → **Non-existent domain** ⇒ `official-data` es **categoría taxonómica de cardeep**, no subdominio DNS real (consistente con convención peer). `[VERIFICADO]`

---

## 11. Resumen para schema

- **slug:** `anfac`
- **subdominio (cardeep):** `official-data`
- **naturaleza:** patronal de fabricantes (institucional), publicadora de **estadística oficial de mercado** vía IDEAUTO/DGT. NO tasación, NO censo de dealers, NO VIN.
- **productos:** 12 (núcleo: Matriculaciones turismos/VCL/industriales [IDEAUTO], Producción y Exportación [propio], Barómetro Electromovilidad, Parque, Comercio Exterior, Logística, Informe Anual, Barómetro VA/VC, Plan España Auto 2030, Position Papers).
- **diferencial central:** autoridad de **denominador nacional** (ventas/producción/exportación de España) + lado **oferta industrial** (fábricas/destinos) + barómetros compuestos (electromovilidad con red de recarga e inoperativos; VA/VC único en Europa) + parque con edad/etiqueta por CCAA. Abierto y gratis.
- **gap central para cardeep:** sin punto de venta/dealer, sin valoración, sin VIN, sin microdato, sin API/feed; solo agregados España en PDF. ANFAC es **contexto de mercado** (totales para normalizar), no fuente de huella digital de puntos de venta.
