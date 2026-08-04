# Plan maestro — Hero + Buscador Cardeep

> Estado: PLAN. Cero código escrito. Fecha: 2026-08-03.
> Base de evidencia: 28 agentes / 7 frentes / 2,86M tokens, con pase adversarial
> que refutó 15 afirmaciones marcadas como verificadas. Todo número de aquí abajo
> está medido contra la base viva o marcado como estimación.

---

## 0. Veredicto

El panel de búsqueda no tiene un problema de gusto: tiene tres agujeros
estructurales que ninguna cantidad de CSS tapa.

1. **No existe buscador.** Los 92 endpoints de la API no incluyen ninguna búsqueda
   de vehículos. El panel hace `window.location.href = '/marketplace?q=…'`.
2. **No existen los atributos.** Ni color, ni carrocería, ni versión, ni potencia,
   ni plazas. La columna `title` cubre el 96,9% pero solo lleva color en el 0,04%
   de las filas y carrocería en el 2,0%.
3. **El conteo en vivo no es computable hoy.** Un `count(*)` filtrado mide
   ~1.100–2.700 ms contra un presupuesto de 150 ms.

Sumado a esto, dos defectos de datos que envenenan cualquier cifra que se muestre:
**233.250 filas disponibles (9,28%) tienen `make` vacío**, y `MERCEDES` (9.673) va
por libre de `MERCEDES-BENZ` (148.015) — una fuga del 6,1% en la marca premium más
grande. Cualquier contador publicado hoy miente por defecto.

---

## 1. Correcciones del pase adversarial (leer antes de fiarse del resto)

| Afirmación caída | Corrección |
|---|---|
| "Los tokens no están en el corpus" | Sí están: `rojo` 90 docs, `familiar` 799, `grande` 17.327. Escasos, no ausentes. |
| "Anidar `backdrop-filter` es un no-op garantizado" | Falso como causalidad. El defecto real es **inversión de elevación**: el menú es más oscuro que el panel. |
| Medidas de contraste del panel (2,70:1 etc.) | **Fabricadas.** El muestreo del backdrop no correspondía a la geometría real del `object-cover`. Hay que volver a medir sobre el píxel real. |
| "~130 marcas = picker funcionalmente completo" | Denominador inflado: excluía las 233.250 filas sin marca. |
| "Route D son 7 conectores, 1 semana" | Hay **41 clases `Vehicle`** y 41 puntos de INSERT. Coste real muy superior. |
| Latencias de conteo (1.006–2.175 ms) | No reproducibles con precisión; el rango real medido es 601–2.694 ms. La dirección aguanta: muy por encima de 150 ms. |
| "`work_mem` corta el conteo 2,1x" | Falso: el plan no tiene ningún nodo consumidor de `work_mem`. Efecto teórico máximo 0 ms. |

**Regla derivada:** ninguna cifra de este plan se publica en la UI sin re-medirla
en el momento de implementarla.

---

## 2. Arquitectura elegida

Cuatro bloques. Los dos primeros no tocan una línea de front y no requieren red.

### BLOQUE 0 — Cimiento de datos (sin front, sin red, reversible)

**0.1 Higiene de dimensiones.** Tablas `make_canon` + `make_alias`. Normalización
en un solo sitio: decode de entidades HTML → NFKD → sin diacríticos → colapsar
`&`/`-`/`_`/espacios → mayúsculas. Reconstruir `mv_market_make_model` agrupando por
`make_slug`, no por `make_raw` (hoy emite las 3.501 grafías sucias a la API).
Ganancias medidas: Mercedes-Benz +11.077 filas, Citroën +3.281, DS +2.035,
Land Rover +1.435, KGM/SsangYong consolida 4 grafías en 8.648.
Los modelos-como-marca (`GOLF` 431, `IBIZA` 65, `POLO` 37…) se **reasignan** con
`kind='model_as_make'` + `implied_model`, nunca se borran.

**0.2 Recuperar las 233.250 filas sin marca** por prefijo más largo del `title`
contra `make_canon`+`make_alias`. Sin esto todo contador infravalora hasta un 9,3%.

**0.3 Normalizar `fuel` y `transmission`.** `fuel` tiene 110 variantes crudas;
`unaccent(fuel) ILIKE '%electr%'` devuelve 107.429 filas frente a 52.330 sin
`unaccent` — **el 51% de los eléctricos es invisible hoy**. `transmission` está
vacía en el 54,3%: se usa como señal de refuerzo, **jamás como filtro duro**.

**0.4 Migración 0098** — añadir a `vehicle`: `color`, `body_type`, `trim`, más
`color_source` / `body_source` (`source|url_slug|model_map|title|NULL`). La
procedencia es obligatoria: sin ella no se puede auditar una cifra.

**0.5 Cosecha de lo que ya tenemos (SQL puro, cero red).**
- `color` para ~282.920 filas por regex sobre `deep_link` (ancla
  `-<fuel>-<colour>-<uuid>` verificada, vocabulario de 13 valores).
- `trim` para ~1.114.226 filas desde `vehicle_event.new_value->>'version'`.
- Resultado día uno: color ~11,3%, versión ~44,3%, **sin descargar un solo byte**.

> Cifras de 0.5 heredadas del frente 7 y **no re-verificadas por el pase
> adversarial**. Se re-miden antes de escribir la migración.

**0.6 `model_attributes`** — la pieza que desbloquea el lenguaje natural.
Tabla de ~943 pares marca+modelo = 77,0% de la flota (2.185 pares → 81,2%).
Etiquetado: carrocería / segmento / plazas / `is_family`. Se paga un modelo
frontera para etiquetar (es 1-2 €, y cada fila apalanca ~2.300 anuncios) y se
revisan a mano los 391 pares que cubren el 80% del volumen. **No** se etiquetan
los 46.397 pares: la cola por debajo del rango 2.185 es el 5% del volumen y ruido.

Criterio de aceptación del bloque: `make` vacío < 1%; suma de contadores por marca
igual al total del censo ±0; `unaccent` aplicado en todo filtro de texto.

### BLOQUE 1 — Motor de búsqueda y conteo (API, sin front)

**1.1 `search_cube`** — tabla (no vista materializada), grano
`make × model × province × year × km_bucket × price_bucket × fuel`.
Medido a 6 dimensiones: 743.166 filas / 66 MB / ~20 s de construcción.
Refresco por **swap atómico** (`build next → index → analyze → BEGIN; DROP; RENAME; COMMIT`),
nunca `REFRESH CONCURRENTLY`: la doctrina PG del proyecto prohíbe generar tuplas
muertas. Cadencia 5 min. `computed_at` se sirve en cada respuesta.
La provincia se resuelve **en construcción** vía `entity_ulid → entity.province_code`
(no existe en `vehicle`), eliminando el join de 3.222 ms del camino de ejecución.

**1.2 Endpoints.**
- `GET /search/count` → `{count, as_of, exact:true, snapshot_age_seconds}`
- `GET /search/facets` → todas las facetas en un round-trip vía `GROUPING SETS`
- `GET /search` → resultados
Ambos entran en `CACHEABLE_PATH_PREFIXES` (hoy un prefijo nuevo no cachea nada),
con `computed_at` del cubo dentro de la clave de caché.

**1.3 Tres carriles de búsqueda, con el LLM FUERA del camino caliente.**
- **Carril A — experto** (~80% del tráfico): tokenizador determinista contra el
  diccionario canónico (~1.100 entradas, cacheable en memoria de la API) + regex de
  versión + `websearch_to_tsquery` sin acentos. `unaccent` necesita envoltorio
  `IMMUTABLE` para poder usarse en columna generada. Los typos se resuelven contra
  el **diccionario**, nunca con similitud trigram sobre 2,5M filas.
- **Carril B — lenguaje natural** (~15%): moderación barata → Haiku con salida
  estructurada → devuelve **filtros, jamás SQL ni IDs** → validador duro (enums,
  rangos, coherencia) → se ejecuta por el camino del carril A. Caché de consulta
  normalizada. **Nunca** se llama al LLM para el contador del botón.
- **Carril 0 — escalera de relajación** (tu "prohibido mostrar cosas random"):
  quitar techo de km → ensanchar precio ±25% → año ±2 → soltar transmisión (pronto
  y por defecto, está vacía en el 54,3%) → modelo→marca → modelo→segmento → **STOP**.
  Nunca se cae en "coches populares". Cada relajación se **etiqueta en la UI** y se
  ofrece como chip de un clic. Todos los peldaños se calculan en **una sola pasada**
  con agregación condicional.

Criterio de aceptación: p95 del contador < 150 ms; carril A p95 < 60 ms; cero
resultados no solicitados; el contador nunca muestra una cifra que no case con los
resultados que devuelve la misma consulta.

### BLOQUE 2 — Superficie (front) — *no arranca sin tu OK explícito*

**2.1 Sistema de cristal de 3 ejes** (elevación × tinte × borde), sustituyendo las
utilidades ad-hoc. El popover **deja de ser negro**: pasa a superficie opaca *más
clara* que el panel (`#303943`, hover `#39424C`), separada por sombra y luz
superior, no por inversión de luminancia. Opcionalmente con 6-10% de tinte cobalto
para que pertenezca a la marca. Se elimina el `backdrop-filter` del menú: ahí es un
no-op que solo cuesta GPU.
Se re-mide el contraste real sobre la geometría verdadera del `object-cover` antes
de fijar el suelo del panel.

**2.2 Ruido dentro del panel.** Reutilizar el `feTurbulence` que ya existe en
`HeroBackdrop.tsx` a opacidad 0,035 en `mix-blend-mode: overlay`. Un blur de 32px
sobre un cielo en degradado **bandea visiblemente** sin él. Es el salto más barato
de "caja borrosa" a "material".

**2.3 El neón de invitación.** `@property --angle` + `conic-gradient` de un solo
tono cobalto con huecos transparentes, animando **solo** `--angle` (trabajo en
compositor). Reposo: respiración lenta 0,06→0,12 **solo si el campo está vacío y
sin tocar**; muere al primer pulsado. `prefers-reduced-motion` → halo estático.
Institucional, no RGB de gamer.

**2.4 Marca → Modelo y versión.** Dos controles, no tres — que es lo que mobile.de
hace de verdad: un `optgroup` por familia cuyo **primer hijo es el roll-up**
("Clase C (todas)"), seguido de sus versiones. Dos espacios de ID: `g:<model>` y
`v:<model>:<submodel>`, para que "quedarme en Clase C general" sea una elección de
primera clase y no un fallback. El 98,0% de las familias tiene ≤25 versiones.
El enum solo alcanza el 40,2% del inventario → **se acompaña de texto libre**
contra el resto (coches.net, con mejores datos, sigue ofreciendo "Versión" como
campo libre). Enum solo = ocultar en silencio la mayoría del stock.

**2.5 Logos.** Se elimina `cdn.simpleicons.org` (404 en Mercedes-Benz, la marca #3
con 170.760 filas; 21 de 29 marcas probadas fallan). Auto-hospedaje 100% para el
tier 1, con `source_url` + licencia registrados por activo. Se borra el fallback
de texto en Arial — LAND ROVER (20.455 filas) se renderiza hoy como un `<text>` de
Arial, y eso es exactamente el "parece HTML" que señalas. Se sustituye por un
monograma **diseñado** con la tipografía del producto.
Alineación por **área óptica constante** (el rango de aspect ratio medido es
0,62→15,87, 25,6x), no por caja. `logo-ar.json` ya tiene las medidas y **nadie las
consume**.
Se elimina `filter: brightness(0) invert(1)`: aplanar cada marca a silueta blanca
destruye el rondel de BMW, Alfa Romeo y Ferrari. Marcas en color sobre cristal,
desaturadas en estado no seleccionado, color pleno en hover y selección — que es,
además, el estado de hover "diseñado" que el listón exige.
Postura legal: uso nominativo — la misma base sobre la que operan AutoScout24 y
mobile.de. Nunca alterado más allá de escalado uniforme, nunca en lockup que
implique patrocinio, con vía de retirada documentada.

**2.6 Año y kilómetros.** Fuera el slider de dos manetas: **todos** los referentes
medidos (mobile.de, coches.net) lo rechazan, y el W3C advierte de huecos de soporte
en tecnología asistiva para multi-thumb táctil. Dos selects desde/hasta con
**espaciado no lineal** (km: 5k, 10k, saltos de 10k hasta 100k, 25k hasta 200k,
"+200.000"; año: 1 en 1 los últimos ~20, luego de 5 en 5), con entrada numérica
libre para expertos. Clamp obligatorio: km a [0, 300.000] con cubo de desbordamiento
(99.725 filas), año a [1950, 2027] — hay 345 filas por encima de 1M km, un máximo de
4.500.007, y años 0 y 2030 que reventarían cualquier eje.
**Sí va la curva de densidad**, pero como sparkline estática y no interactiva encima
de los dos campos, tintada en el tramo seleccionado: la distribución de km es
genuinamente bimodal (pico 0-10k, valle 30-40k, repunte 70-80k), así que informa.
Coste: un rollup de 30 cubos por (marca, modelo) refrescado con el cubo.

**2.7 Provincia.** Mismo tratamiento de cristal y mismo patrón de lista con
buscador; 52 provincias reales desde la API. Añade contador por provincia desde el
cubo.

**2.8 El botón.** `Ver 44.947 coches · datos de hace 3 min`. Cuenta **exacta contra
un snapshot con fecha**, nunca una estimación con "~" (los estimados del planner
salen 9-17x cortos: no son publicables). Refresco inmediato en controles discretos
(1,8-52 ms medidos), debounce solo en continuos (250-300 ms) **siempre** con
`AbortController` + guarda de request-id. Nunca se vacía el número mientras
recarga. Si una combinación da 0, el botón lo dice y ofrece la relajación más
cercana.

**2.9 El campo libre y su placeholder animado.** Etiqueta accesible estable
(`aria-label`) + capa `aria-hidden` superpuesta con el texto que se escribe — el
atributo `placeholder` **no** se muta, lo que elimina de raíz la corrupción del
nombre accesible. La rotación se detiene en foco, hover o cualquier tecla, se
autotermina tras 2 vueltas y descansa en el ejemplo más inclusivo. Con
`prefers-reduced-motion` se pinta estático desde el primer frame.
Ritmo: 45 ms/carácter (anclado a ~22 car/s de lectura silenciosa en español),
±12 ms de jitter, +60 ms en espacio, +180 ms en coma; cruce de 240 ms.
Altura reservada para la cadena más larga → CLS cero.
**Y el detalle que lo convierte en producto:** Enter con el campo vacío ejecuta el
ejemplo que se está mostrando. El daño documentado del placeholder (el usuario cree
que es un valor real y pulsa Enter) se convierte en el camino de menor fricción.

**Los 7 ejemplos, verificados uno a uno contra la base** (para que el botón nunca
diga "Ver 0 coches"):

| # | Ejemplo | Resultados |
|---|---|---|
| 1 | `BMW Serie 3 diésel por menos de 15.000 €` | 12.487 |
| 2 | `Coche eléctrico por menos de 20.000 € en Madrid` | 4.470 |
| 3 | `Volkswagen Golf GTI` | 5.817 |
| 4 | `Híbrido con menos de 50.000 km cerca de Barcelona` | 21.921 |
| 5 | `Mercedes-Benz C 63 AMG` | 469 |
| 6 | `Audi A4 Avant quattro` | 4.511 |
| 7 | `Menos de 5.000 € y menos de 150.000 km` ← reposo | 68.827 |

Progresión deliberada: marca+combustible+precio → capacidad que no sabías que
existía (eléctrico+ciudad) → deseo puro → naturalidad conversacional → precisión
experta → tecnicismo → **red de seguridad sin conocimiento de marca**.
Prohibido: palabras de color (85 filas), segmento genérico (781-4.200), maletero,
CV, puertas o plazas (no existe columna). Prohibido copiar los ejemplos publicados
por coches.net: los tres se apoyan en atributos que Cardeep no almacena.

### BLOQUE 3 — Hero y carrusel

**3.1 Copy.** Fuera el subtítulo actual. Tres candidatos, ninguno "elegido" hasta
que lo veas:
- `Dos millones y medio de coches. Un solo mapa.`
- `El mercado entero, medido. Antes de que se note.`
- `Sabemos qué vale. Sabemos cuánto lleva parado. Sabemos dónde está.`

**3.2 Fuera los contadores.** Se elimina la `<dl>` de vehículos / puntos de venta /
provincias y se elimina el pie `20.034 puntos de venta · 52 provincias` bajo el
botón. La escala no desaparece del producto: **se absorbe en el argumento**
(el titular o la etiqueta del campo la llevan), que es donde vende en vez de
ocupar sitio.

**3.3 Fuera los CTA duplicados.** Hoy hay tres entradas a "Explorar el índice" en la
misma pantalla. Se queda una.

**3.4 El carrusel.** Hoy es `TABLESAMPLE SYSTEM` — muestreo **literalmente
aleatorio**, y la UI lo confiesa ("una muestra viva, distinta en cada visita").
Se sustituye por oportunidades reales: la tabla `deal_score` ya existe, con **48.474
vehículos** puntuados por z-score contra la mediana de su cohorte y bandas propias
`chollo_fuerte` / `bajo_mercado` más el ahorro en euros. El criterio es de la casa;
no hay nada que inventar.
**Bloqueo a resolver:** está congelada desde el 18/07 y ninguno de los 12 jobs del
scheduler la refresca. Hay que añadir el job antes de enchufar el carrusel, o
nacería caducado.
Geometría: altura reducida, ancho acotado a ~50% de la sección, deriva horizontal
continua a velocidad constante, doble render con desplazamiento de exactamente el
ancho de una copia para que la costura no se vea. Se mantienen las flechas: con
`prefers-reduced-motion` la fila no se mueve, y sin flechas quedaría inservible.

---

## 3. Lo que NO se va a hacer, y por qué

- **Color desde las fotos (Route A): rechazado.** ~184 GB de descarga y ~18,75 días
  de reloj a ritmo del governor, en una máquina sin GPU, para cubrir como mucho el
  79% (el 20,8% de los enlaces de foto están muertos) y con la peor precisión justo
  en el 75,4% de la flota que es blanca/gris/plata/negra. `model_attributes` da
  mejor cobertura por una hora de cómputo local y cero red. Se archiva para una
  pasada dirigida sobre el ~14,5% sin marca+modelo, el día que haya GPU.
- **pgvector: aplazado.** No está en la imagen `postgres:16` y obligaría a cambiarla.
  El léxico determinista cubre el grueso de forma explicable y auditable. Se revisa
  solo si los fallos medidos del carril B lo exigen.
- **"Todas las marcas del mundo" como rejilla: descartado.** El censo tiene 3.534
  grafías de marca, de las que 2.546 aparecen exactamente una vez. Un selector de
  3.534 entradas es inusable. Registro de dos niveles: ~130 marcas curadas visibles,
  y la cola alcanzable escribiendo pero nunca pintada como logo.
- **Slider de dos manetas para km/año: descartado.** Ver 2.6.

---

## 4. Riesgo declarado

El riesgo mayor no es técnico: es **silencio**. Cuando `model_attributes` cubra el
77% de la flota, el 23% restante no tiene carrocería. Si "grande de familia" filtra
duro, ese 23% desaparece sin que nadie lo sepa — y el producto habrá empezado a
mentir por omisión. Contrato obligatorio: los atributos derivados **puntúan y
ordenan**, no excluyen; y cuando una faceta es parcial, la UI declara el
denominador (`Automático (471.030 de 1.148.276 con dato)`).

## 5. Orden de ejecución

`Bloque 0` → `Bloque 1` → (OK explícito) → `Bloque 2` → `Bloque 3`.

Los bloques 0 y 1 no tocan el front y son enteramente reversibles (migraciones
aditivas, tablas nuevas, endpoints nuevos). El bloque 2 no arranca sin tu visto
bueno, por la regla permanente de no escribir front sin autorización.
