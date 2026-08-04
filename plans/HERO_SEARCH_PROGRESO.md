# Progreso — Hero + Buscador Cardeep

## RONDA 2 (2026-08-04) — revisión del owner

Siete puntos, todos ejecutados. Lo importante es lo que la investigación encontró
en el trabajo de la ronda 1: **cuatro bugs propios**, todos de la clase "produce una
respuesta plausible y falsa".

| # | Punto | Estado |
|---|---|---|
| 1 | Neón rehecho con la técnica neon-gradient-card (gradiente lineal deslizante + copia desenfocada), paleta Cardeep | ✅ |
| 2 | 12 ejemplos nuevos por segmento real del comprador español; animación arreglada | ✅ |
| 3 | Submarcas fundidas (5) + `is_listable` honrado + familias de versión | ✅ |
| 4 | Logos: 30% → **98,4%** de cobertura local, manifiesto generado desde disco | ✅ |
| 5 | Año/km: atajos fuera, cajón sin cortar, entrada manual de km | ✅ |
| 6 | Carrusel foto-primero según la referencia | ✅ |
| 7 | Copy del hero reescrito con ancla medida | ✅ |

### Los cuatro bugs propios que la investigación destapó

1. **El símbolo `€` era código muerto.** `norm()` lo borraba antes de que corrieran
   los patrones de precio; la rama `(?:euros?|eur|€)` no se alcanzaba nunca. Tres
   de los siete ejemplos que el campo enseñaba usaban una sintaxis que el parser
   descartaba. **El corpus de tests no lo cazó porque yo siempre escribí "euros"** —
   un test que solo habla como su autor no encuentra cómo escribe un usuario.
2. **El contador ignoraba combustible, precio y km mientras el panel los pintaba
   como chips.** Inflación medida hasta **115×**. Es el mismo fallo que el cubo
   existía para impedir, reintroducido una capa más arriba. Arreglado añadiendo
   `fuel`, `price_bucket` y `seats` al grano (+17,4% de filas, dentro del techo
   teórico de +38% que impone que el cubo nunca puede tener más filas que coches).
3. **`fuel_norm` archivaba 50.376 híbridos como gasolina.** La etiqueta española es
   `Electro/Gasolina` y la regex buscaba `electric`, no `electro`. Verificado por
   modelo: Toyota C-HR, Corolla, Yaris, Renault Arkana, Kia Sportage. Otros 5.076
   con `Híbrido no enchufable` estaban clasificados como enchufables porque la
   prueba de "enchufable" corría antes que la negación.
4. **`is_listable` era decorativo.** El selector lee del cubo y nunca consultaba la
   bandera, así que Yamaha, Ducati, Benimar y Hymer aparecían en un selector de
   coches. 155 → **113 marcas listables**.

### Decisiones tomadas contra la recomendación recibida

- **El "5 veces más" del copy quedó descartado**: el verificador demostró que
  mezclaba universos (277.083 filas de `platform_listing` contra 1.483.606 cabezas
  de clúster). Re-medido con el MISMO universo en ambos lados: el mayor portal
  especializado cubre 215.494/1.483.606 = **uno de cada siete**. El titular usa esa
  cifra, no la refutada.
- **Vauxhall NO se fundió en Opel** pese a estar en la tabla de la investigación:
  los 3 coches son clásicos británicos de los 60-70, no gemelos de Opel, y el alias
  los habría re-archivado como Opel. Tres coches no justifican publicar una
  falsedad.

### Familias de versión

`pipeline/search/version_family.py` — 3 modos (premium alemán / VAG / PSA-Renault),
porque la potencia es RUIDO en los dos primeros e IDENTIDAD en el tercero
("PureTech 130" y "PureTech 110" son coches distintos). **102.337 versiones →
18.907 familias**; la tabla del selector baja de 106.246 a 42.713 filas.
Clase A: 427 versiones → A 180 · A 180 d · A 200 · A 200 d · A 250 e · A 45 AMG…
Trampa resuelta: `C 220 d AMG Line` → `C 220 d` (paquete de acabado), mientras
`A 45 AMG 4MATIC` → `A 45 AMG`. Confundirlas duplicaría cualquier recuento de AMG.

### Abierto

- **24 marcas sin logo** (22.666 coches, 1,6%), Land Rover la mayor con 13.939.
  Simple Icons las ha retirado por peticiones de marca registrada. Necesitan
  sourcing con licencia verificada — decisión del owner, no mía.


Tracker vivo de la ejecución de `HERO_SEARCH_MASTERPLAN.md`.
Al retomar: LEER ESTE FICHERO, no re-auditar.

Autorización: `/goal` del 2026-08-03 — ejecutar el plan completo, incluido el front.

---

## BLOQUE 0 — Cimiento de datos ✅ CERRADO

| Paso | Estado | Resultado medido |
|---|---|---|
| 0.1 Consolidación de marcas (`backfill_make.py`) | ✅ | null-recovery 150.207 · casing 195.229 · model-as-make 3.342 |
| 0.1b Registro canónico (`0099_make_canon.sql`) | ✅ | `make_canon`+`make_alias`+`make_norm()`+`imm_unaccent()` |
| 0.1c Seed (`seed_make_canon.py`) | ✅ | 172 marcas (124 listables) · **99,70% del censo resuelto** |
| 0.4 Atributos (`0098_vehicle_attributes.sql`) | ✅ | `color`/`body_type`/`trim`+procedencia+`model_attributes` |
| 0.5 Cosecha (`backfill_attributes.py`) | ✅ | **color 278.218 (11,1%) · versión 1.114.219 (44,3%)**, cero red |
| 0.6 Etiquetado `model_attributes` | ✅ | **260 pares a mano = 77,8% del parque**; "grande de familia" alcanza 414.783 coches |
| 0.7 Canonicalización de MODELOS (`0101_model_key.sql`) | ✅ | Leon+León→19.860 · Clase CLA+CLA→6.353 · Clase GLC+GLC→5.649 |

## BLOQUE 1 — Motor de conteo ✅ PARCIAL

| Paso | Estado | Resultado |
|---|---|---|
| 1.1 `search_cube` (`0100_search_cube.sql` + `build_search_cube.py`) | ✅ | 624.846 filas / 89 MB / build 192 s / swap atómico |
| 1.2 `/search/count` `/search/makes` `/search/models` | ✅ | **43-60 ms filtrado**, exacto, con `as_of` |
| 1.3 Carril A — parser determinista (`search_parse.py` + `/search/parse`) | ✅ | resuelve marca/modelo/versión/provincia/combustible/color/carrocería/familia/precio/km/año/cambio; devuelve lo NO entendido |
| 1.3b Eval set (`tests/test_search_parse_eval.py`) | ✅ | **27 casos verdes + 5 `xfail`**. Los xfail SON la especificación del carril B. |
| 1.3c Carril B — LLM para lo que el eval marca en rojo | ⏳ ABIERTO | Ollama responde en el host (200). Decisión informada por el eval, no por intuición: hoy el determinista resuelve todo lo medible con vocabulario del censo; los 5 xfail piden juicio ("algo barato", "que gaste poco"), no vocabulario. |
| Job de refresco del cubo | ✅ | `search_cube_rebuild` cada 20 min, registrado y vivo |
| `/search/submodels` + submodelo en el grano del cubo | ✅ | 107.485 versiones; cubo 891.314 filas / 156 MB |

## BLOQUE 2 — Superficie ✅ PARCIAL

| Paso | Estado |
|---|---|
| 2.1 Sistema de cristal 3 ejes + popover invertido | ✅ el menú ya no es negro |
| 2.2 Grano dentro del panel | ✅ |
| 2.3 Neón de invitación (`field-invite`) | ✅ |
| 2.6 Año/km reconstruido (`RangeFields.tsx`) | ✅ fuera scroll y slider; escala no lineal + presets |
| 2.8 Contador en vivo en el botón | ✅ exacto, con debounce+AbortController |
| 2.9 Placeholder animado + Enter-ejecuta-ejemplo | ✅ |
| 2.4 Cascada marca→modelo→**submodelo** | ✅ 3 niveles con roll-up "todas las versiones" primero |
| 2.5 Logos falsos retirados | ✅ **20 SVG eran `<text>` en Arial** disfrazados de marca registrada. Movidos a `public/logos/_retirados_arial/` (reversible) y podados del manifiesto. El monograma diseñado toma el relevo, ahora con iniciales reales (Land Rover → **LR**, no "LA"). Solo 5 de los 20 tenían stock: Land Rover 13.939, Jaecoo 2.217, BAIC/Lotus/INEOS ~100. |
| 2.5b SVG reales para esas 5 marcas | ⏳ ABIERTO — **requiere decisión tuya**: sourcing con licencia auditable (Wikimedia Commons PD + `logo_source_url`/`logo_license` en `make_canon`, columnas ya creadas). No lo hago unilateralmente: es postura legal, no código. |
| 2.7 Contadores por provincia | ✅ condicionados a la marca (BMW en Madrid = 17.364, no "coches en Madrid") |

## BLOQUE 3 — Hero y carrusel ✅ PARCIAL

| Paso | Estado |
|---|---|
| 3.1 Copy nuevo con la cifra dentro del argumento | ✅ |
| 3.2 Contadores fuera + pie del panel fuera | ✅ |
| 3.3 CTAs duplicados fuera | ✅ |
| 3.4 Carrusel = oportunidades reales, compacto, mitad de ancho | ✅ |
| Job de refresco de `deal_score` | ✅ cada 6 h, **publica solo si el run pasa su propia verificación** |
| Gate de publicación en `/market/opportunities` | ✅ el endpoint público servía un run `published=false` — ahora exige publicado |

---

## Hechos verificados durante la ejecución (NO fiarse de la investigación previa)

- **Marcas vacías 234.937 (9,35%) → 84.730 (3,37%).** Mi primera muestra de 8 filas
  parecía basura (páginas de categoría) y estuve a punto de descartarlas: eran las 8
  primeras filas FÍSICAS, no una muestra. Medido bien: 232.297 tenían precio. Eran
  coches reales. **Lección: `LIMIT n` sin `ORDER BY random()` no es una muestra.**
- **Mercedes-Benz 148.015 → 184.189** tras consolidar (la investigación predijo +11.077;
  real +36.174).
- **Deadlock** entre el UPDATE masivo y `autovacuum: VACUUM public.vehicle` (la tabla
  arrastraba 421.217 tuplas muertas y autovacuum no había pasado NUNCA; tras él, 611).
  Toda escritura masiva sobre `vehicle` va por lotes.
- **El cubo cazó dos errores propios antes de publicarse:**
  1. Comparaba el cubo contra la fuente medida 90 s después → descuadre de 4.160 que
     no era un bug sino deriva del censo vivo. Arreglado con un snapshot
     `REPEATABLE READ` que envuelve construcción y verificación.
  2. Grano equivocado: contaba ANUNCIOS (2.510.953) mientras `/stats` contaba COCHES
     físicos (1.482.719). Dos totales contradictorios en la misma pantalla, y una
     búsqueda que habría ofrecido el mismo coche tres veces. Reconstruido sobre
     `v_canonical_vehicle`+`servable_vehicle`: **1.483.272, cuadrado al vehículo.**
- **El selector y el botón discrepaban** (Mercedes 159.133 vs 183.837) porque leían de
  tablas distintas. `/search/makes` y `/search/models` ahora salen del mismo cubo.
- **Las oportunidades ordenadas por ahorro absoluto sacan primero la basura**: un Range
  Rover 2023 a 23.500 € (−81%) y 47 filas con "ahorro" ≥100% del precio de cohorte.
  Banda de credibilidad aplicada: 12-35%, cohorte ≥30, km ≤200.000.
- **24 "logos" son texto en Arial**, incluido `land-rover.svg` (21.620 coches).
- Encoding: reescribir un `.tsx` con `Set-Content -Encoding utf8` en PS 5.1 corrompe
  los acentos (doble codificación). Usar `[System.IO.File]::WriteAllText` con
  `UTF8Encoding($false)`.

- **El eval cazó tres bugs que a ojo no se ven** (por eso existe):
  1. `seat leon 2020` resolvía a **provincia León**, no al modelo. España nombra
     provincias como coches; la provincia se resuelve ahora DESPUÉS de marca+modelo.
  2. `Islas Baleares` no existía: la tabla usa nombres INE (`Balears, Illes`,
     `Coruña, A`). Añadida la inversión del artículo y los nombres castellanos
     (Vizcaya, Gerona, Orense…) — un producto español que falla con "Vizcaya"
     falla con la mitad del país.
  3. Solo en vivo: `peugeot 2008` → `submodel=2` (subcadena sin límites de
     palabra), y `mercedes clase c 220 d` no encontraba su versión porque la
     consulta pedía las 400 versiones **más largas** en vez de las más frecuentes,
     y "C 220 d" —la más listada del modelo— nunca llegaba al matcher.
- **El contador mentía en cuanto conecté el parser.** Los chips decían
  `rojo · para familia · Sevilla` y el botón contaba 83.159 — solo Sevilla —, porque
  color, carrocería y familia no eran dimensiones del cubo. Una cifra MAYOR que la
  verdad, impresa al lado de las condiciones que ignora. Añadidas al grano:
  **194 coches** reales, con los 69.149 sin color publicado declarados en pantalla.
  Coste real +11,5% de filas: carrocería y familia dependen de marca+modelo y no
  crean filas nuevas; solo el color parte grupos.
- **Tres "Mercedes-Benz" en el selector** (115.360 / 882 / 39): el cubo agrupaba por la
  grafía cruda y solo se traducía la etiqueta, así que tres grafías se mostraban
  idénticas y el usuario no podía saber cuál pulsar. El cubo se reconstruyó
  **claveado por la marca canónica**: de 226 filas a **155 marcas reales**.

## Auditoría final de regresiones (2026-08-03)

Ejecutada sobre las superficies que toqué, por lotes (la suite completa de 243
ficheros excede los 12 min y el entorno mata los procesos de fondo largos).

| Lote | Resultado |
|---|---|
| market router (M2/M8) + cache/ratelimit + arbitrage router + no-fabricated-data | 52 ✅ |
| scheduler (4 ficheros) + arbitrage score | 55 ✅ |
| auth + pagination + canonical | 48 ✅ |
| API ampliada + market (exhaustiveness, gaps, lifetime, seal, cohort, compute_stats, metrics) | 180 ✅ |
| eval del parser | 27 ✅ + 5 xfail |

**Cero regresiones introducidas.** Dos fallos encontrados, ambos PREEXISTENTES y
ambos arreglados:

1. `test_arbitrage_no_fabricated_data.py` apuntaba a `web/src/pages/Arbitrage.tsx`,
   ruta que dejó de existir el 2026-07-27 (commit `8cd8c6c`). Llevaba desde
   entonces fallando con `FileNotFoundError` — peor que un test rojo: **un guardia
   que no encuentra su objetivo no está fallando, está sin vigilar nada**.
   Reapuntado a `workspace/` comprobando ambas rutas.
2. `marketing.py:402` filtraba por `v.country_code`, columna que **no existe** en
   `vehicle` (el país vive en `entity`). El endpoint `/entities/{cdp}/channel-radar`
   devolvía 500 en cada llamada desde el 2026-07-19 (commit `d4c029b`). Arreglado
   con el join a `entity`, como hace `stats.py`. 22 ✅.

Atribución verificada en ambos casos con `git status` (cero cambios míos en esos
ficheros) y `git log` del commit que los rompió.

### Build de producción

`npm run build` ✅ en 33,85 s. Verificado que el CSS nuevo viaja al bundle
(`glass-menu`, `field-invite`, `@property --angle`), no solo que compila: esbuild
avisa de que el anidamiento `&::-webkit-scrollbar-thumb` requiere `:is()`, y la
regla se emite correctamente como `#cx-v4 :is(#cx-v4 .glass-menu)::-webkit-...`.
Inocuo: `::-webkit-scrollbar` solo lo honran Chrome y Safari, que soportan `:is()`.
El aviso es previo a esta sesión (glass-menu ya anidaba el scrollbar).

## Riesgos abiertos

1. `cardeep-autopilot` levanta solo con Docker y compite por `vehicle`.
2. ✅ RESUELTO — imagen `cardeep-app:latest` reconstruida y ambos contenedores
   recreados desde ella. Nada depende ya de `docker cp`.
3. `/dev/shm` a 64 MB → `VACUUM` paralelo falla.
4. Build del cubo ~280 s. Cadencia puesta a 20 min por eso.
5. **NUEVO — los MODELOS tienen la misma suciedad que tenían las marcas**: conviven
   "Clase C", "CLASE C" (44) y "Clase C Estate"/"Clase C Berlina" como modelos
   distintos. La capa canónica del Bloque 0 cubrió marcas, no modelos. Es el
   siguiente escalón de calidad del selector.
