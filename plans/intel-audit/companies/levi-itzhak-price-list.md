# Auditoría atómica — Levi Itzhak Price List (מחירון לוי יצחק)

> Auditoría de inteligencia competitiva nivel institucional para Cardeep.
> Empresa de datos / valoración de automoción de **Israel**. Web: https://levi-itzhak.co.il/
> Fecha auditoría: 2026-06-30. Método: navegación del sitio propio vía navegador real (Playwright; el sitio responde **403 a WebFetch** y **Cloudflare challenge** en el portal B2B — todo el contenido propio se extrajo con navegador headless leyendo el árbol de accesibilidad de cada página), más verificación cruzada con Wikipedia hebreo, Calcalist, TheMarker, Globes, Google Play, ZoomInfo y explicadores de terceros (Suncar, Budget.co.il).
> Convención: **[V]** = verificado (leído en la fuente) · **[A]** = asumido/inferido (marcado siempre).
> Nota sobre el "subdominio: valuation": **`valuation.levi-itzhak.co.il` NO resuelve** (DNS `ERR_NAME_NOT_RESOLVED`, [V]). No existe tal subdominio. Las superficies de valoración reales son: la **app gratuita**, el **portal de agentes B2B** (`portal.levi-itzhak.co.il`), la **herramienta pública de conversión de código de modelo** (`portal.levi-itzhak.co.il/leviconvert/PublicConversion.aspx`) y el sitio web/revista impresa.

---

## 1. Identidad

| Campo | Valor | Estado |
|---|---|---|
| Marca / producto | **Levi Itzhak Price List** — "מחירון לוי יצחק" (lit. "el precio-listado de Levi Itzhak"). Posicionamiento propio: **"המחירון של המדינה"** = "el precio-listado del Estado/del país" para vehículos, motos y vivienda | [V] |
| Empresa / grupo | **Levi Itzhak Group** — "קבוצת לוי יצחק" (empresa familiar privada) | [V] |
| Fundador | **Levi Itzhak** (nacido **Yitzhak Levi / יצחק לוי**), 1937, **Bulgaria**. Emigró a Israel en 1948 (vivió en Jaffa). Estudió mecánica de automoción (instituto Shevach, Tel Aviv); instructor técnico de mecánicos de tanques en las FDI (cambió su nombre a "Levi Itzhak" en esa época); estudió **peritaje de automoción en Gran Bretaña**; abrió oficina de peritaje en Tel Aviv | [V] |
| Fundación del grupo | **1971** (declaración propia en su web: "fundó el grupo en 1971, al sacar el primer precio-listado") | [V] |
| Primer precio-listado de coches usados | **1973/1974** (Wikipedia hebreo y TheMarker: 1974; Calcalist: 1973) — discrepancia menor con el "1971" corporativo; 1971 = oficina/grupo, 1973-74 = primer mחירון de VO publicado | [V] |
| Sucesión / owner actual | Fallecimiento del fundador el **24-ago-2023, a los 86 años** (enterrado en Morasha, Ramat HaSharon). Dirección transferida a dos de sus tres hijos: **Mi-Ron Levi (מי-רון לוי)** — fue **subdirector general (סמנכ"ל) y experto de la empresa en automoción** — y **Karin Levi-Krauze (קרין לוי-קראוזה)** — fue **directora de marketing, publicidad, promoción y edición, y jefa del depto. de encuesta de viviendas** | [V] |
| HQ | **Tel Aviv** — Derech Menachem Begin 90, "Beit Levi Itzhak" (cubre centro y sur de Israel) | [V] |
| Sucursal | **Haifa / Norte** — Derech HaAtzmaut 104 (cubre el norte de Israel) | [V] |
| Categoría | Editor de **precios-listado de referencia** (price guides) y servicios de **peritaje (שמאות)**. Tres verticales de precios: **rכב/vehículos, אופנועים/motos, נדל"ן/inmobiliario**; más peritaje de rכב, de propiedad/contenido del hogar y de antigüedades, y contenido de seguros/reformas | [V] |
| Autoridad de mercado | Estándar de facto en Israel; **el sector de seguro y peritaje lo reconoce como el documento de referencia**; usado por bancos (garantía de préstamos), aseguradoras (siniestros), leasing, concesionarios e importadores y el público | [V] |
| Notoriedad de marca | Según encuesta **TGI** (citada por ellos), es de las marcas líderes en Israel; por su volumen de tirada anual, su editorial está entre las mayores del país | [V — claim propio] |
| Web / proveedor técnico | Sitio construido por **Catom** (catom.com / catom.co.il). Portal B2B sobre **ASP.NET (.aspx)** tras **Cloudflare** | [V] |

### Clientes objetivo [V]
Aseguradoras · Bancos (valoración de garantía / préstamos de coche) · Compañías de leasing y renting · Concesionarios e importadores · Peritos de seguros (שמאים) · Tribunales / peritaje en litigios · Público general (compra-venta C2C) · Autoridad fiscal (referencia de valor) [A].

---

## 2. Cobertura

### Geográfica [V]
- **Solo Israel.** Mercado nacional único. No hay cobertura paneuropea ni multipaís (contraste fuerte con Eurotax/Autovista, DAT, etc.). Sin versión en inglés del producto de datos (web en hebreo).

### Scope de vehículos [V]
- **Vehículos privados (turismos)** — núcleo del producto.
- **Vehículos comerciales** (hasta ~4 toneladas; con su propia "grupo de licencia/קבוצת רישוי").
- **Camiones (משאיות)** y **autobuses/minibuses (אוטובוסים/מיניבוסים)** — el glosario y el título del diccionario confirman "כלי רכב, משאיות ואוטובוסים".
- **Furgonetas (מסחריות/vans), grúas/camiones-remolque (גוררים/tow trucks), taxis (מוניות)**.
- **Motocicletas y scooters** — vertical separado (מחירון אופנועים), con su propio listado interactivo, magazine digital y archivo.
- **Nuevo y usado**: el precio base de referencia es el de mercado; el cálculo de valor (depreciación) aplica a **usado (יד שנייה)**. El **score de seguridad** cubre coches **nuevos y usados**.
- **Powertrains**: combustión, **híbrido (היברידי)** y eléctrico [A — categorías presentes en el catálogo de modelos; profundidad EV no documentada].

---

## 3. Productos + campos atómicos

El grupo comercializa **cuatro familias de "מחירון" (price guides)** + servicios. Para Cardeep, el producto relevante es el **precio-listado de vehículos**; documento su lista atómica completa y enumero el resto.

### 3.1 Levi Itzhak Car Price List — מחירון רכב (producto núcleo de valoración)
Mecánica verificada en la **página oficial de ejemplos de cálculo** (`/דוגמאות-לחישוב-מחיר-רכב-יד-שניה`): se parte de un **precio medio/base** por modelo+fecha y se aplican **deducciones porcentuales encadenadas**. Ejemplos textuales [V]:
> **Ej.1:** Precio medio en el listado, alta 2014/01 = **41.000 ₪** → *deducción por ex-leasing (החכרה) −21% = 8.610 ₪* → 32.000 → *deducción adicional por km (200.000 km) −3% = 960 ₪* → **final 31.000 ₪**.
> **Ej.2:** Precio medio, alta 2017/01 = **103.000 ₪** → *ex-leasing en uso de conductor único −17% = 17.500 ₪* → 85.000 → *km (130.000) −7% = 6.000 ₪* → 79.000 → *nº de manos (4 "ידיים") −7% = 5.500 ₪* → **final 73.000 ₪**.

**Campos / métricas atómicas del producto de coche** (consolidado de ejemplos + FAQ comunitaria + diccionario + explicador Suncar) [V salvo marca]:

*Identificación del vehículo*
1. **Código de modelo (קוד דגם)** — identificador numérico Levi por versión (p.ej. 683601, 724093, 778541). [V]
2. **Fabricante (יצרן)**. [V]
3. **Modelo / submodelo / acabado (דגם / גימור)** (p.ej. "Limited", "Active", "Sprit"). [V]
4. **Año de fabricación (שנת ייצור)**. [V]
5. **Fecha de alta / primera matriculación (תאריך עליה לכביש)** — mes/año; base de la depreciación. [V]
6. **Cilindrada / nº de motor (נפח מנוע, סמ"ק)**. [V]
7. **Tipo de combustible (סוג דלק)** — gasolina/diésel/híbrido/eléctrico. [V]
8. **Transmisión (תיבת הילוכים)** — automática/manual/robotizada. [V]
9. **Nº de puertas (מספר דלתות)** (3/5). [V]
10. **Potencia / CV (כ"ס)**. [V]
11. **Color (צבע)** [V — minor].
12. **Categoría/carrocería** (privado / comercial / camión / bus / furgoneta / grúa / taxi). [V]

*Valores*
13. **Precio base / medio del listado (מחיר בסיס / מחיר ממוצע)** — precio "de libro" por modelo+fecha. [V]
14. **Precio ponderado/calculado online (מחיר משוקלל)** — precio final ajustado que devuelve el sistema online (puede diferir del "de libro"). [V]
15. **Depreciación mensual (ירידת ערך חודשית)** — importe ₪/mes por modelo aplicado por antigüedad desde el alta (un FAQ cita ~**1.900 ₪/mes** para un modelo). [V]
16. **Precio histórico (מחיר היסטורי)** — valor del listado en una fecha pasada concreta (vía archivo). [V]

*Ajustes (cada uno como % de deducción o adición sobre el base)*
17. **Ajuste por kilometraje (הפחתה/תוספת בגין ק"מ)** — relativo a la media anual esperada; **deducción** si exceso (ej. −3% a 200k; −7% a 130k) y **prima** por km bajo. [V]
18. **Ajuste por nº de propietarios / "manos" (מספר ידיים/בעלים קודמים)** — deducción escalonada (ej. −7% por 4 manos). [V]
19. **Ajuste por tipo de propiedad / uso previo (סוג בעלות)** — familia de deducciones: [V]
    - **Leasing financiero (ליסינג מימוני)**
    - **Leasing operativo (ליסינג תפעולי)**
    - **Alquiler / renting / ex-flota de hire (השכרה / החכרה)**
    - **Empresa (חברה / רכב חברה)**
    - **Uso de conductor único (נהג יחיד)** — *reduce* la deducción de leasing
    - **Autoescuela (לימוד נהיגה)** [A — categoría aludida]
    - **Ejército / gobierno (צבא)**, **Kibutz**, **Yeshivá/institución**
    - **Taxi (מונית)** — base y umbrales propios
    - **Importación personal (יבוא אישי)**
    - **Discapacitado (נכה)** [A]
20. **Deducción combinada** (p.ej. leasing+empresa = −21%; rangos citados en FAQ −8% a −22%). [V]
21. **Ajuste por accidente / pérdida de valor (ירידת ערך בגין תאונה)** — aun reparado; depende de **ubicación e intensidad del golpe, calidad de la reparación y demanda del modelo**. [V]
22. **Ajuste por daño estructural / chasis (פגיעה בשאסי)**. [V]
23. **Umbral de pérdida total (אובדן גמור / אובדן להלכה)** — difiere por uso (taxi vs privado pueden divergir: total como taxi, reparable como privado). [V]
24. **Adiciones por equipamiento/extras (תוספות אבזור)** — suman valor: [V]
    - **Sistema de gas GLP/GPM (מערכת גפ"מ)**
    - **Techo solar (גג נפתח / סאן רוף)**
    - **Tapicería de cuero (ריפודי עור)**
    - **Puertas extra (5 vs 3)**
    - **Upgrade de potencia (תוספת כ"ס, p.ej. +167 CV)**
    - Otros extras de fábrica (מפרט/אבזור)
25. **Estado general (מצב כללי)**. [V]
26. **Garantía de fabricante vigente (אחריות יצרן)** — efecto en valor (incl. casos de motor sustituido). [V]
27. **Tasa de licencia/circulación y su renovación (אגרת רישוי וחידושה)** — dato auxiliar de la tabla. [V — vía Budget/Suncar]
28. **Grupo de licencia (קבוצת רישוי)** — para privados y comerciales ≤4t. [V — vía Budget/Suncar]

*Datos asociados (features nuevas)*
29. **Score de nivel de seguridad (ציון רמת בטיחות)** — para coches nuevos y usados; basado en el sistema de seguridad del **Ministerio de Transporte**. [V]
30. **Oferta/demanda cualitativa (היצע וביקוש)** — citada como factor que mueve el precio del modelo (no es un índice numérico publicado). [V/A]
31. **Indicación de matriculación previa** ("רישום קודם" del permiso) usada para inferir propiedad empresa/leasing. [V]

> **Importante:** Levi Itzhak **no publica la tabla completa de coeficientes** en abierto; los porcentajes exactos viven en el **producto pagado** (revista impresa: "tablas auxiliares") y en el **portal B2B**. Los % anteriores son los ejemplos oficiales + valores citados en su FAQ. [V]

### 3.2 App "מחירון רכב לוי יצחק" (consumo, gratuita)
- Búsqueda por **número de matrícula (לפי מספר רכב)** o por parámetros (**fabricante → modelo → año → versión/מפרט**). [V]
- Devuelve **valor de mercado** del vehículo (precio base + ponderado). [V]
- **iOS + Android** (`com.levinew.app`, v12.0.2; **100.000+ descargas** en Google Play; existe también paquete `com.kenlo_group.levicars`). [V]
- Marketing: **búsquedas ilimitadas gratis**; una fuente indica "**10 búsquedas gratis el primer mes**" (posible freemium). [V claim / A modelo exacto]
- Claim de marketing terceros: "**+750.000 usuarios**" (no verificable; Play marca 100k+ descargas). [A]

### 3.3 Revista impresa mensual de coche — מחירון רכב מודפס
- Listado tabular por fabricante/modelo/código con **precio base** + **tablas auxiliares de ajuste** (km, manos, propiedad, equipamiento). [V]
- Cadencia **mensual** (ediciones identificadas, p.ej. "מחירון רכב מרץ 2026"). [V]

### 3.4 Archivo de precios — ארכיון מחירון רכב
- Pedido del **listado de un mes pasado concreto** (para tasaciones retroactivas, siniestros y litigios). Servicio de pago puntual. [V]

### 3.5 Herramienta de conversión de código de modelo — טבלת המרה לקודי דגם
- `portal.levi-itzhak.co.il/leviconvert/PublicConversion.aspx` — mapea el **código de modelo del permiso/Ministerio ↔ código Levi**. Pública pero tras **Cloudflare challenge**. [V]

### 3.6 Portal de agentes B2B — כניסת סוכנים
- `portal.levi-itzhak.co.il/bit/` y `portal01.levi-itzhak.co.il/bit/` — acceso profesional (login, Cloudflare). Incluye el módulo **"סקר דירות"** (encuesta de viviendas) además del de rכב. [V]

### 3.7 Otros productos del grupo (no-auto, enumerados)
- **מחירון אופנועים / קטנועים** (motos/scooters): listado interactivo + "מפורט", magazine digital, archivo, noticias dos-ruedas. [V]
- **מחירון דירות / נדל"ן** (inmobiliario): **calculadora interactiva de valor de vivienda (מחשבון שווי דירה)**, costes de construcción, magazine digital, dirות מכונס נכסים, etc. [V]
- **Peritaje (שמאות)**: rכב (vehículos), רכוש/תכולה (propiedad/contenido del hogar), עתיקות (antigüedades) — servicio profesional. [V]
- Contenido editorial: seguros de coche, guías de compra VO, leasing, transferencia de propiedad, formularios legales (gilui naot, zikhron dvarim), reformas. [V]

---

## 4. Metodología y fuentes de datos

- **Origen histórico (años 70-80):** encuestas **telefónicas** a propietarios que vendían su coche para fijar el precio de mercado; asignación de **código numérico** a cada modelo. [V]
- **Hoy:** equipos telefónicos + **datos de plataformas de venta online (anuncios)** + aportes de **peritos, comerciantes de trade-in y encuestadores internos**. [V]
- **Cálculo:** todos los parámetros entran en una **fórmula propietaria de Levi Itzhak** que produce un "símbolo/valor de modelo"; sobre el **precio base** se aplican deducciones/adiciones de las **tablas auxiliares** (km, manos, propiedad, equipamiento, estado, accidente). [V]
- **Doble precio:** "de libro" (מחיר בסיס impreso) vs **"ponderado" online (משוקלל)** — pueden divergir; el online incorpora más ajustes. [V]
- **Cadencia:** **mensual** (cada edición fija el valor del mes; la depreciación se reconoce mes a mes). [V]
- **Score de seguridad:** importado del sistema del **Ministerio de Transporte**. [V]
- **No hay** divulgación pública de modelado estadístico/ML ni de tamaño de panel; metodología tratada como **caja negra propietaria** (criticada por prensa como opaca y casi-monopólica). [V]

---

## 5. Entrega

| Canal | Detalle | Estado |
|---|---|---|
| **App móvil** | iOS + Android, gratuita; lookup por matrícula o parámetros | [V] |
| **Web pública** | sitio en hebreo; páginas de ejemplo, FAQ, score de seguridad; lookup online (ponderado) | [V] |
| **Revista impresa mensual** | suscripción anual; tablas + listados | [V] |
| **Portal B2B de agentes** | `portal.levi-itzhak.co.il` (login, Cloudflare) — aseguradoras/peritos/concesionarios; módulo encuesta de viviendas | [V] |
| **Herramienta de conversión de código de modelo** | pública (Cloudflare) | [V] |
| **Magazine digital (flipbook)** | alojado en `online.fliphtml5.com` (moto/nadlan) | [V] |
| **Archivo / pedido puntual** | listado de un mes pasado bajo demanda | [V] |
| **API pública** | **No documentada / no hallada** — sin docs de REST/feeds/Excel públicos | [V — ausencia] / GAP |
| **Integración DMS** | No documentada públicamente | [A] / GAP |

---

## 6. Precio

- **Suscripción anual al listado impreso de coche:** **840 ₪** ("מחירון בודד במשך 12 חודשים", **IVA + envío incluidos, sin fraccionar pagos**). [V]
- **App:** **gratuita** (búsquedas ilimitadas; posible "10 gratis el primer mes"). [V claim]
- **Archivo:** pago puntual por edición pasada (importe no publicado). [V que existe / importe GAP]
- **Portal B2B / licencia profesional:** **no público** — cotización/contrato (aseguradoras, peritos, concesionarios). [V que no es público] / GAP
- Existe también "**מחירון בהנחה**" (listado con descuento) como gancho promocional. [V]

---

## 7. Placement — dónde se ubica cada dato en su UI
> Patrón a copiar por Cardeep. Mapeo pantalla → dato. Modelo de "tasación por deducciones encadenadas sobre un precio base mensual".

| Datum | Dónde aparece (sección/pantalla) | Estado |
|---|---|---|
| **Entrada de identificación** | App/online: campo único **matrícula**, o flujo **fabricante→modelo→año→versión**; el código de modelo es la clave interna | [V] |
| **Precio base / medio (₪)** | Primera línea del resultado de valoración (impreso: columna de precio junto al modelo y su código) | [V] |
| **Precio ponderado/final online (₪)** | Resultado online (משוקלל), distinto del impreso | [V] |
| **Deducción por tipo de propiedad (leasing/empresa/alquiler) (% y ₪)** | Resultado de cálculo, **2ª línea** tras el base ("הפחתה בגין החכרה −21% = 8.610 ₪"), con precio corrido | [V] |
| **Deducción por kilometraje (% y ₪)** | **Línea siguiente**, sobre el subtotal ("בגין מספר ק"מ −3% = 960 ₪") | [V] |
| **Deducción por nº de manos (% y ₪)** | **Línea siguiente**, sobre el subtotal ("בגין מספר ידיים −7% = 5.500 ₪") | [V] |
| **Precio final (₪)** | **Última línea** destacada ("מחיר סופי") | [V] |
| **Tablas auxiliares (km / manos / propiedad / equipamiento)** | Páginas de **tablas** anexas en la revista impresa y en el portal | [V] |
| **Score de seguridad** | **Sección/feature dedicada** ("ציון רמת בטיחות רכב"), por modelo, nuevo+usado | [V] |
| **Depreciación mensual (₪/mes)** | Implícita en la actualización mensual; explicada en FAQ | [V] |
| **Precio histórico (fecha pasada)** | **Archivo** (pedido del listado del mes X) | [V] |
| **Equivalencia de código de modelo** | **Herramienta de conversión** (portal) | [V] |
| **Acceso profesional (todas las tablas/cálculo)** | **Portal de agentes** (login) | [V] |
| **FAQ / casos de cálculo** | Páginas "שאלות נפוצות" y "דוגמאות לחישוב" (Q&A comunitario + ejemplos resueltos) | [V] |

---

## 8. Diferencial (lo que ofrece y otras no)

- [V] **Estándar nacional de facto, con lock-in institucional** (bancos, aseguradoras, leasing, tribunales) — su precio "es" el valor legal/financiero del coche en Israel. Casi-monopolio histórico (criticado por prensa).
- [V] **Modelo de "valor = precio base mensual − deducciones encadenadas transparentes"**: el usuario ve **cada ajuste como % e importe** (propiedad → km → manos → final). Patrón de placement muy claro y replicable.
- [V] **Taxonomía de propiedad/uso muy granular y local** (leasing financiero vs operativo, השכרה, חברה, נהג יחיד, מונית, צבא, קיבוץ, יבוא אישי, נכה) con coeficiente propio cada una — más fino que la mayoría de guías occidentales.
- [V] **Sistema propio de código de modelo (קוד דגם)** + herramienta pública de conversión permiso↔Levi.
- [V] **Distinción explícita "precio de libro" vs "precio ponderado online"** (משוקלל) — doble verdad impreso/digital.
- [V] **Score de seguridad integrado** (nuevo+usado) sobre datos del Ministerio de Transporte.
- [V] **Cobertura amplia de tipos** en un solo producto: turismo, comercial, camión, bus, furgoneta, grúa, taxi; y verticales hermanos de **motos** e **inmobiliario** bajo la misma marca.
- [V] **Archivo histórico** consultable por mes — clave para siniestros y litigios.
- [V] **App gratuita** de gran adopción (lookup por matrícula) — penetración de marca enorme en el consumidor.

## 9. Gaps (lo que NO ofrece / no expone)

- [V] **Solo Israel.** Cero cobertura multipaís; sin armonización paneuropea.
- [V/ausencia] **Sin API pública ni feeds/Excel documentados** — no hay capa de integración para terceros descrita; integración solo vía portal/archivo.
- [V] **Sin métricas de inteligencia de mercado en tiempo real** tipo *days-to-sell, market days supply, price-to-market %, índice demanda/oferta numérico, curva de depreciación proyectada a futuro* — es un **price-book de valoración**, no una plataforma de analítica de mercado (esas métricas las añadieron sus competidores Yad2 y el listado del Ministerio).
- [V] **Sin historial por VIN/Carfax**: no ofrece historial de siniestros, propietarios, ITV ni verificación/fraude de kilometraje; el km y los accidentes son **inputs declarados por el usuario**, no datos certificados.
- [V] **Sin especificación técnica profunda multimarca** (configurador, tiempos de mano de obra, precios de piezas OEM, TCO, datos de batería EV) — fuera de su alcance.
- [V] **Metodología opaca** (caja negra propietaria); sin transparencia de panel, muestreo ni modelo estadístico; criticada por casi-monopolio y por divergencias libro/online.
- [V] **Precios B2B y de archivo no públicos**; tabla completa de coeficientes solo en producto pagado.
- [V] **Competencia creciente**: **Yad2** (índice basado en transacciones reales del mayor marketplace) y el **listado oficial del Ministerio de Transporte (`carlistprice.mot.gov.il`, ~2021)** erosionan el monopolio.
- [A] **Profundidad EV/híbrido limitada** y previsión de valor residual a futuro inexistente (no es un proveedor de RV forecasting para leasing al estilo Autovista/DAT).
- [A] **Riesgo de continuidad/innovación** tras el fallecimiento del fundador (2023) y la presión regulatoria/competitiva.

---

## 10. Fuentes (URLs)

**Sitio propio (navegador real; el sitio responde 403 a WebFetch):**
- https://levi-itzhak.co.il/Home — homepage, obituario del fundador (1937-2023, "fundó el grupo en 1971"), mapa de navegación, verticales.
- https://levi-itzhak.co.il/דוגמאות-לחישוב-מחיר-רכב-יד-שניה — **ejemplos oficiales de cálculo** (deducciones −21%/−17% leasing, −3%/−7% km, −7% manos).
- https://levi-itzhak.co.il/מחירון-רכב — Q&A del listado (código de modelo, base vs ponderado, tipos de vehículo: comercial/camión/taxi).
- https://levi-itzhak.co.il/רכבים-שאלות-נפוצות — FAQ comunitaria (factores: leasing 12-22%, manos, km, accidente/total-loss, GPM, importación, etc.).
- https://levi-itzhak.co.il/אפליקציה-לבדיקת-רכב-מחירון-רכב-לוי-יצחק — app (matrícula/parámetros, iOS+Android, gratis).
- https://levi-itzhak.co.il/מחירון-רכב-מנוי-שנתי — **precio 840 ₪/año** (IVA+envío, sin fraccionar).
- https://levi-itzhak.co.il/אודות-קבוצת-לוי-יצחק — about (fundación 1971, Bulgaria, HQ Tel Aviv Begin 90 + Haifa HaAtzmaut 104, empresa familiar, TGI).
- https://levi-itzhak.co.il/ציון-רמת-בטיחות-רכב — **score de seguridad** (nuevo+usado, fuente Ministerio de Transporte).
- https://levi-itzhak.co.il/מילון-מונחים-רכב — diccionario "כלי רכב, משאיות ואוטובוסים".
- https://levi-itzhak.co.il/מחירונים — catálogo: rכב, אופנועים, דירות, ארכיון.
- https://portal.levi-itzhak.co.il/leviconvert/PublicConversion.aspx — conversión de código de modelo (Cloudflare).
- https://portal.levi-itzhak.co.il/bit/ y https://portal01.levi-itzhak.co.il/bit/ — portal de agentes B2B (login, Cloudflare).
- `valuation.levi-itzhak.co.il` — **NO resuelve** (verificación negativa del "subdominio valuation").

**Prensa / referencia (verificación cruzada de identidad y mercado):**
- https://he.wikipedia.org/wiki/לוי_יצחק_(שמאי) — biografía (1937 Bulgaria, 1974 primer listado, muerte 24-ago-2023 a los 86, hijos Mi-Ron y Karin).
- https://www.themarker.com/dynamo/cars/2023-08-25/... — obituario TheMarker (muerte a los 86, fundador del מחירון).
- https://www.calcalist.co.il/local_news/car/article/h1wkemip3 — por qué se volvió dominante; competidores (Yad2, Ministerio de Transporte); sucesión (Mi-Ron Levi, Karin Levi-Krauze).
- https://en.globes.co.il/en/article-israels-transport-ministry-launches-used-car-price-list-1001371825 — listado oficial del Ministerio (competidor).
- https://www.haaretz.com/2010-03-23/ty-article/levi-itzhak-no-longer-the-auto-pricing-monopoly/ — fin del monopolio (contexto competitivo).
- https://play.google.com/store/apps/details?id=com.levinew.app — app (100k+ descargas, v12, gratis).
- https://www.zoominfo.com/c/levi-itzhak-group/429988420 — ficha de empresa (Levi Itzhak Group).
- https://www.budget.co.il/en/sale_in_israel/buy_a_car_articles/levi_itzhak_price_list/ — explicador EN (tablas auxiliares: km, manos, tasa de licencia, grupo de licencia, estado; tipos: privados, buses, minibuses, camiones, furgonetas, grúas, taxis).
- https://suncar.co.il/מה-זה-מחירון-לוי-יצחק/ — explicador de cálculo (fórmula propietaria, parámetros, accidente, seguridad/airbags, specs).
- https://carlistprice.mot.gov.il/ — listado oficial del Estado (competidor directo).

> **Verificación:** identidad corporativa y sucesión verificadas con ≥3 fuentes independientes (Wikipedia he + TheMarker + Calcalist). Mecánica de deducciones y precio 840 ₪ leídos directamente en páginas propias [V]. Porcentajes exactos de la tabla completa, precios B2B y existencia de API = **no públicos** (marcados GAP/[A]). Cifra "750.000 usuarios" = claim de marketing no verificado [A]; Google Play confirma 100k+ descargas [V]. El "subdominio valuation" del encargo **no existe** (DNS negativo, [V]).
