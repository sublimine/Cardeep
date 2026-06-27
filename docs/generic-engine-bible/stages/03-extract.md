# Etapa 3 · Extraer/Normalizar — Biblia
> Estado adversarial: **NEEDS_REWORK** (`holds=false`). El esquema de receta y el prefijo `cdp_code` están parametrizados por país y verificados; la **lógica de extracción/normalización es country-BLIND** (gate INE ES, derivación `zip[:2]`, precio en euros, sin moneda, fuel/transmission en español, tokenizador solo-Latin). No se transcribe lo roto como hecho: cada rotura del inquisidor lleva abajo su resolución o su OPEN ITEM con causa+gating.
> Fuente: Wave 1 (path:línea verificado). Stack vivo CAÍDO: cifras DB = punto-en-el-tiempo.

> **Funnel** · `README.md` → `00-MASTER.md` → **stages/03-extract** (aquí) → `04-identity` (geo-adapter cierra la mitad GEO) → `COVER-NEW-COUNTRY.md`.
> **Provenance** · `[VERIFIED path:línea]` = leído en esta redacción · `[VERIFIED·W1 path:línea]` = anclado por la Ola-1, no re-leído aquí · `[ASSUMED]` = inferencia sin línea · `[CORREGIDO]` = afirmación de la Ola-1 comprobada y **falsa**; se da el hecho corregido.

> **v2 (profundo) ·** este capítulo integra los **26 sub-proyectos institucionales (360 por faceta)** — ver [Sub-proyectos institucionales](#indice-subproyectos). La estructura v1 (Misión · Lo que existe HOY · Motor/Pack · Costuras · Diseño genérico A→Z · Onboarding · Sellado · Veredicto adversarial · Mejoras · Riesgos) se **conserva intacta**; el bloque profundo se añade al final, tras Riesgos.

---

## Misión

Convertir el crudo de cada anuncio (HTML/JSON de la etapa 2) en un `CanonicalVehicle` **country-agnóstico** —forma única que `delta`/`ingest`/`identity` ya consumen— **sin retener crudo** (sample-verify-delete: la receta es el activo). La etapa tiene tres planos ortogonales: **ACQUIRE** (transporte, ya motor), **LOCATE** (selector → campos), **NORMALIZE** (locale → canónico). El país entra como **DATOS** (LocaleProfile + brands + selectores), nunca como rama de código. La capa-2 IA local está pre-cableada y **dormante (€0)**.

El listón de sellado no es "la receta cuenta bien": es "la receta produce filas **servibles y coherentes cross-país**" (moneda presente, enums neutrales, provincia resoluble, marca recuperada). Hoy el sello solo mira el conteo — esa es la primera grieta que cerramos.

---

## Lo que existe HOY (verificado)

- **Esquema de receta durable y round-trippable**: `Transport/Fingerprint/Pagination/Parsing/Evidence/Recipe` como dataclasses, `SCHEMA_VERSION=2`, vocabulario de status cerrado (`DRAFT/VERIFIED/FAILED`), (de)serialización YAML estable. [VERIFIED recipe_schema.py:63-109] (`Parsing`, `Evidence.parse_loss`, `Recipe`) · [VERIFIED·W1 recipe_schema.py:27,30-33,118-167].
- **Escalera de coste §4 declarada**: `Parsing.engine = next_data|jsonld|css|llm_local` con `field_map: dict[str,str]` como mapa declarativo. **PERO** `engine` es un `str` con default `"next_data"`, **no un enum** — vocabulario ABIERTO. [VERIFIED recipe_schema.py:64-69].
- **Arnés source-agnóstico** `EXTRACT(sample k)→VERIFY(VAM)→PERSIST(YAML)→DELETE`; `decide_status` es veredicto PURO (offline-testable) y `_offline_verdict` espeja el quórum sin DB. [VERIFIED·W1 recipe_harness.py:135-194,94-117,196-207].
- **Registro de 5 extractores enchufables** (autoscout24, web_generic, coches_com, coches_net, autocasion); cada uno expone `recipe_template`+`sample` (k acotado que REUSA la parse fn ya verificada, no un 2º scraper). [VERIFIED·W1 recipe_extractors.py:280-286,42-92].
- **Peldaño web genérico** (CMS/DMS de concesionario): extrae `schema.org Car|Vehicle|MotorizedVehicle|Motorcycle|Product` de JSON-LD y MICRODATA; web sin JSON-LD ⇒ sample vacío ⇒ receta `FAILED` con razón (recipe-first honesto). [VERIFIED recipe_extract_web.py:27-34,53-109,117-118].
- **Parsers reales por conector** que materializan `make/model/year/km/price/fuel/transmission/photo_url` en el dataclass `Vehicle`; identidad = `(deep_link, source_ref)`. [VERIFIED sources/autoscout24.py:40-51] · [VERIFIED·W1 platform/{coches_com,coches_net,autocasion}_wholesale.py].
- **Saneamiento numérico compartido** (única pieza de normalización ya centralizada): `PRICE_MAX=5_000_000`, `KM_MAX=1_500_000`, `YEAR_MIN=1900`, `sanitize_year_km` (cruce edad×km imposible), aplicado en el borde de ingest. [VERIFIED price_sanity.py:49-53] · [VERIFIED ingest.py:83-88].
- **Canonicalizador de marca compartido**: `_CANON` (~70 marcas con alias) + `normalize_make()` que recupera la marca del token líder del título cuando el conector la dejó NULL, preservando marcas desconocidas verbatim (Law I: under-fill > mis-fill). [VERIFIED identity/make_normalizer.py:19-76] · [VERIFIED ingest.py:95].
- **Enrutado de paths por país YA genérico**: `country_of_cdp` parsea `CDP-([A-Z]{2})-`; `recipe_root/recipes_flat_dir/data_root/census_dir` aceptan `country_code` (default ES). [VERIFIED·W1 paths.py:30,33-63].
- **Persistencia con auto-chequeo de round-trip** (falla en WRITE si el YAML no re-parsea) a `countries/<country_of_cdp>/recipes/<cdp>.yaml`. [VERIFIED·W1 recipe.py:43-94].
- **VERIFY reusa el VAM cero-confianza**: `record_count_verdict(subject_type='recipe_sample')` sobre quórum `declared/fetched/parsed`; `parse_loss = fetched-parsed` debe ser 0 para VERIFIED. [VERIFIED recipe_schema.py:89-93] · [VERIFIED·W1 recipe_harness.py:157-161,80-117].
- **Replay desde YAML** prueba que la receta relocaliza la fuente — **PERO re-ejecuta `extractor.sample()` (Python), NO interpreta el `field_map`**; el intérprete field-map-driven está explícitamente NO reclamado. [VERIFIED·W1 recipe_harness.py:220-255,228-231].
- **Recetas ES persistidas**: **[CORREGIDO]** el flat `countries/ES/recipes/*.yaml` = **61** ficheros (lo que el arnés escribe vía `recipe.py`), **no 641**. El 641 es el conteo del **árbol geo completo** `countries/ES/**`. [VERIFIED `ls countries/ES/recipes/*.yaml | wc -l = 61`; `find countries/ES -name '*.yaml' | wc -l = 641`]. La narrativa de certificación de la Ola-1 atribuyó mal la cifra (ver sealing-hole SH5).
- **Capa-2 (IA local) = 0 líneas**: `llm_local` solo existe como valor de enum y disclaimer; no hay extractor, ni gramática/GBNF, ni modelo, ni invocación. [VERIFIED recipe_schema.py:67] · [VERIFIED·W1 recipe_harness.py:229].
- **Superficie de test**: 11 ficheros cubren receta, arnés, los 4+1 extractores, `price_sanity`, `make_normalizer`, reshape — **todos asertan comportamiento ES** (ver SH4). [VERIFIED·W1 tests/test_recipe*.py, test_price_sanity.py, test_make_normalizer.py].

---

## Motor (invariante, reusado byte-idéntico por país)

Lo que un país nuevo **NO toca**:

1. **Esquema de receta** (`Transport/Fingerprint/Pagination/Parsing/Evidence/Recipe` + `SCHEMA_VERSION` + status cerrado + round-trip). `recipe_schema.py` idéntico.
2. **Ciclo del arnés** `EXTRACT→VERIFY→PERSIST→DELETE` con `decide_status` PURO y `_offline_verdict`. `recipe_harness.py` drivea cualquier `Extractor` protocol.
3. **Doctrina sample-verify-delete**: k≈3-5 acotado, `parsed.clear()` como delete, cero crudo en disco. Invariante de coste y legalidad para todo país.
4. **Contrato de salida `CanonicalVehicle`**: la forma que delta/ingest/identity consumen aguas abajo (hoy por duck-typing). **Se versiona y se le añade `currency`** (ver Diseño A→Z).
5. **VAM cero-confianza como juez**: `record_count_verdict` sobre quórum `declared/fetched/parsed`; `parse_loss==0` obligatorio. Mecanismo idéntico, datos por país.
6. **Física universal del número**: `sanitize_km` (≥0, sentinela 1.5M), `sanitize_year` (≥1900, ≤now+1), `sanitize_year_km` (edad×km imposible). La LÓGICA del gate es universal; el **techo de precio es parámetro de país** (y currency-aware — hoy NO lo es).
7. **Escalera de transporte por tiers** (http/curl_cffi/browser vía `engine.fetch`) y la escalera de coste estructurado-primero (next_data/json_api → jsonld/microdata → css → llm_local).
8. **Enrutado de paths por país** (`paths.country_of_cdp` + árbol per-country). Genérico ya hoy; ES es el default.
9. **Maquinaria de verificación**: replay + golden + Ferrari + CI (`db-tests`/`unit`). El banco es idéntico; **los fixtures son por país** (hoy son ES — SH4).
10. **Prefijo de identidad** `CDP-<CC>-<NN>-<8 base32>` minteado por la misma rutina; el país entra como segmento.

> **[CORREGIDO] sobre `normalize_make`.** La Ola-1 listó como motor "el ALGORITMO de `normalize_make`; solo la tabla de marcas es pack". **Falso.** El paso de tokenización `title.strip().split()[0]` [VERIFIED make_normalizer.py:54] asume **escritura delimitada por espacios** (Latin) — un título japonés `トヨタプリウス` no tiene espacios, `split()[0]` devuelve la cadena entera y **nunca** matchea `_CANON` (que además es solo-Latin [VERIFIED make_normalizer.py:19-40]). El algoritmo está **acoplado al país**. La parte realmente invariante es: *"recupera la marca del texto del título usando la tabla del pack, preservando lo desconocido verbatim (Law I)"*. El **CÓMO** se extrae el token (split vs match anclado en `brand_table`) **es pack/motor reparametrizable**, no constante. Resolución €0 en el Diseño A→Z (anclaje por `brand_table`, no `split()`).

---

## Pack por país (lo que cada país aporta para esta etapa)

Un país es un directorio de **datos**, no código:

- **`countries/<CC>/recipes/`** — plantillas de receta por fuente (`recipe_template`): `Transport{base_url, impersonate, timeout, charset}`, `Pagination{strategy, url_template, page_size, declared_path, stop}`, `Parsing{engine∈enum, container_path, field_map (mini-DSL)}`. Los **selectores deterministas** de cada superficie.
- **`countries/<CC>/locale.yaml`** — `LocaleProfile`: `decimal_sep, thousand_sep, currency, price_max, date_fmt, stock_hints, count_words, marketplace_blocklist, fuel_map, transmission_map, brand_table, postcode_format, source_encoding`.
- **`countries/<CC>/brands.yaml`** — tabla de alias de marca calibrada a la **distribución real del país** (frecuencia + alias locales + **script**: para JP/CN, terminales `日産/トヨタ/ホンダ`). ES privilegia SEAT/CUPRA/EBRO.
- **Diccionarios de enum → código neutral**: `fuel_map` (Diesel/Gasolina/Benzin/Gasóleo → `DIESEL/PETROL/EV/HYBRID/…`), `transmission_map` (1/2/Automatik/Caixa automática → `AUTOMATIC/MANUAL`).
- **Cotas numéricas calibradas**: `price_max` = techo del mercado de ocasión nacional **en la moneda local** (ES ~€5M; JP ~¥50-100M); km/year se heredan (universales).
- **Esquema postcode→región** (lo consume el geo-adapter de la etapa 4): formato (DE PLZ 5d, FR 5d→département, IT alfa 2-letra, PT NNNN-NNN, JP 7d) + tabla/regla de mapeo. **El parser de la etapa 3 emite el string CRUDO**; la resolución es de la etapa 4 (PK `(country_code, code)`).
- **Gramática GBNF de la capa-2** (cuando exista modelo): vocabulario de marcas/combustibles del país como terminales. Hoy vacío, €0.
- **Segmento de prefijo** `CDP-<CC>-` y, si aplica, mapeo de tipo de superficie a `kind`.

---

## Costuras ES-hardcoded → fix

Tabla consolidada (es_seams de la Ola-1 + las costuras GEO que el diseño había repartido + la costura `normalize_make` que la Ola-1 había clasificado mal como "motor"). Líneas marcadas `[V]`=verificadas en esta redacción, `[W1]`=ancladas por la Ola-1.

| location | issue | fix |
|---|---|---|
| `ingest.py:49-50` `[V]` | Gate `d.province_code.isdigit() and "01"<=code<="52"` = INE ES **duro**; comentario literal "real Spanish INE province (01-52)". Alfa (IT `MI/RM`) falla `isdigit()` ⇒ país entero rechazado; JP 01-47 ⊂ 01-52 ⇒ mis-geo silencioso; antes hay `cdp_code()`+`municipality_code()` que corrompen geo | El parser emite región/CP **CRUDO** + `country_code`; el gate se vuelve `RegionScheme.validate(raw, CC)` pack-driven (etapa 4, PK `(country_code,code)`). Saca el rango INE del pipeline |
| `sources/autoscout24.py:232` `[V]` (y `coches_com/net`, `autocasion` `_prov*`) `[W1]` | `prov = str(zip)[:2]` = convención INE; FR `75008`→`75`=Toledo, DE PLZ no mapea a Land por prefijo, PT `NNNN-NNN` mal cortado | El parser **NO deriva provincia**: emite CP/region crudo; la derivación es del geo-adapter por país (formato+mapa) |
| `complete.py:89` `[V]` | `_CDP_CODE_RE = ^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$` clava ES; un dealer de otro país jamás pasa a COMPLETED (G1, vigilado por xfail strict) | Widening a `^CDP-([A-Z]{2})-([0-9]{2})-[…]{8}$` capturando CC; quitar el xfail. 1 línea + test |
| `complete.py:305` / `:309` `[V]` | La LECTURA hardcodea `root/"countries"/"ES"` mientras `recipe.py` ESCRIBE vía `country_of_cdp`. **Asimetría**: una receta DE escrita correctamente jamás se encuentra al completar | `paths.recipe_root(country_of_cdp(cdp))` + `recipes_flat_dir(country_of_cdp(cdp))` en lectura; cierra el round-trip por país |
| `price_sanity.py:49` `[V]` | `PRICE_MAX=5_000_000` calibrado en **EUR** (docstring: "€3.6M Chiron", "€5M ceiling", "9.99M sentinela"). En JPY un SUV rutinario supera 5M ¥ ⇒ NULL masivo del mercado legítimo | `price_max` por `LocaleProfile`, comparación **currency-aware** (requiere la dimensión moneda); la lógica de sentinelas pasa a ser set por locale |
| `ingest.py:101` `[V]` | Inserta `v.fuel, v.transmission` **VERBATIM** (a diferencia de `make`, que sí normaliza en `:95`). El eje fuel/transmission queda en el idioma de origen | Normalizar en el borde con `fuel_map/transmission_map` del pack → códigos neutrales, igual que `make` |
| `coches_net_wholesale.py:130` `[W1]` (+ AS24.de `'Benzin'/'Automatik'`, `carandclassic 'petrol'→'Gasolina'`) | Labels de transmisión/fuel hardcodeados y el objetivo canónico de-facto es **ESPAÑOL**, no neutral. Un conector IT (`Benzina/Automatico`) fragmenta la columna contra ES | enum-maps por locale → `AUTOMATIC/MANUAL`, `PETROL/DIESEL/EV/HYBRID`; **migrar las facetas de la served-surface** off-Spanish (NO es "solo un dict" — ver O2) |
| `recipe_extract_web.py:28-30/:32/:33` `[V]` | `_STOCK_HINT/_COUNT_HINT/_MARKETPLACES` en **español incrustados en el motor**; FR `'occasion'≠'ocasion'`, DE `'Fahrzeuge/Gebrauchtwagen'` no matchean ⇒ no encuentra la página de stock | Mover a `LocaleProfile.stock_hints/count_words/marketplace_blocklist`; `GenericWebExtractor` los lee del pack inyectado |
| `recipe_extract_web.py:79` `[V]` | `offers.get("price")` **DESCARTA** `priceCurrency` | Capturar `priceCurrency`; poblar `CanonicalVehicle.currency` |
| `recipe_extract_web.py:104` `[V]` | Precio microdata `[\d.,]+` **sin parse EU**: `'24.900'` se lee `24.9` (€24,90) — bug de locale latente, quizá ya sirviendo precios mal | Enrutar TODO precio-texto (incluido este peldaño) por `parse_money(text, LocaleProfile)` compartido |
| `dealerprobe.py:127/:256` (+ `family_builder…:167`, `family_cms…:345`) `[W1]` | Parse de número EU re-implementado ad-hoc por familia; asume `dot=miles/comma=decimal` ⇒ MX/JP/US `1,234.56` leído ~1000× mal y aún pasa sanity | **Un solo** `parse_money(text, LocaleProfile)` en módulo locale compartido. Reconstrucción de corrección, no swap de separador |
| `make_normalizer.py:54` (+ `_CANON :19-40` Latin-only) `[V]` | `split()[0]` asume tokenización por espacios; CJK ⇒ string entero, nunca matchea. El diseño lo llamó "motor puro" — **[CORREGIDO]** falso | Match anclado en `brand_table` (longest-alias prefix), **script-agnóstico €0**; alias CJK = pack; LLM capa-2 solo para variant free-text (diferido, O1) |
| `recipe_schema.py:67` `[V]` (+ `recipe_extractors.py:245/:130` `[W1]`) | `Parsing.engine` = vocabulario **ABIERTO** (`str` libre, p.ej. `'ssr_ref_re + graphql_ad'`) y `field_map` pseudo-expresión ⇒ la receta **NO es ejecutable**; replay re-corre Python (`recipe_harness.py:228-231,248`) | Cerrar `engine` a **enum** `Selector` + **mini-DSL** `field_map` interpretable; el extractor se vuelve intérprete genérico, la receta se vuelve el pack |
| `recipe.py:20-40` ("defaults to ES") + `make_normalizer.py:9` ("grounded in LIVE ES data") `[W1]` | ES como base **implícita universal**, no como pack #1 explícito | Reificar `countries/<CC>/locale.yaml` + `brands.yaml` cargados por CC; ES pasa a ser el primer pack explícito, sin reescribir su contenido |

---

## Diseño genérico A→Z

La etapa se factoriza en **tres planos ortogonales** con una sola interfaz de salida. El país entra como **datos** en cada plano.

### Plano A — ACQUIRE (transporte) — *ya es motor*
`engine.fetch` con escalera de tiers (http/curl_cffi/browser) gobernada por el governor. El pack aporta `Transport{base_url, impersonate, timeout, charset}` y `Pagination{strategy, url_template, page_size, declared_path, stop}`. **Adición**: `Transport.charset` (Shift-JIS/EUC-JP) + **decode al borde de fetch** antes de parsear — hoy los conectores solo reconfiguran stdout a UTF-8, no establecen el decode de la página fuente para mercados no-UTF-8 (cierra MP7). El sample es acotado (k); el `declared` del oráculo de la fuente alimenta el VAM solo si `full_dealer` — regla universal.

### Plano B — LOCATE (selector) — *el hueco estructural mayor*
Hoy `Parsing.engine` es texto libre y `field_map` descriptivo; el parse real vive en Python por fuente y el replay re-ejecuta `sample()` en vez de interpretar el `field_map`. El diseño **cierra `Parsing.engine` a un ENUM de clases `Selector` ejecutables** — `next_data, json_api, jsonld, microdata, css, regex_hydrate, llm_local` — cada una implementando un `Protocol locate(bytes, container_path, field_map) -> list[dict]`. El `field_map` deja de ser prosa y pasa a un **mini-DSL de path-expressions deterministas** (`'price.amount'`, `'images[0].href'`, `'host+listing.url'`, `'transmissionTypeId|map:transmission'`). Así un conector nuevo —o un país nuevo sobre una fuente conocida, p.ej. `autoscout24.de`— es un **YAML de pack, no Python nuevo**. Los 5 extractores actuales se reescriben como instancias de estos `Selector` parametrizados por su `field_map`; la lógica de muestreo acotado sube al motor. Esto convierte el replay en **intérprete real** y hace la receta un activo autosuficiente de verdad.

### Plano C — NORMALIZE (locale) — *donde vive todo el sesgo ES*
Una única función motor **`normalize_vehicle(raw_fields, LocaleProfile) -> CanonicalVehicle`** concentra lo hoy disperso y duplicado:
- `parse_money(text, profile)` — `decimal_sep/thousand_sep/currency`; soporta convenciones **invertidas** (dot-decimal/comma-thousands MX/JP/US) y miles con espacio/NBSP (FR). Reconstrucción de corrección (los parsers EU actuales corrompen ~1000× los locales invertidos).
- `parse_date(text, profile)` / `parse_year(profile)` — formatos `dd.mm.yyyy` (DE), `yyyy年mm月dd日` (JP); hoy AS24 sobrevive por ISO `firstRegistrationDate[:4]`, un CMS genérico no tiene parser de fecha (cierra MP9).
- `sanitize_km/sanitize_year/sanitize_year_km` — física universal, ya compartidos.
- `normalize_make(value, title, brand_table, segmenter)` — algoritmo motor + **anclaje por `brand_table`** (longest-alias match, script-agnóstico) en vez de `split()[0]`; `segmenter` del pack para CJK.
- `fuel_map` / `transmission_map` — **enum-mappers nuevos** (pack) que faltan hoy; fuel/transmission dejan de guardarse verbatim en español.

`LocaleProfile` es el **único objeto de país** en este plano: `{decimal_sep, thousand_sep, currency, price_max, date_fmt, stock_hints, count_words, marketplace_blocklist, fuel_map, transmission_map, brand_table, postcode_format, source_encoding}`. Los parsers por conector dejan de inlinear bounds y delegan, eliminando la incoherencia 5M-vs-1.5M.

### Contrato de salida — `CanonicalVehicle` versionado **+ moneda**
```
CanonicalVehicle{ deep_link, source_ref, title, make, model, year, km,
                  price, currency,            # <- dimensión NUEVA, no-opcional cuando hay price
                  fuel_code, transmission_code,   # neutrales (enum), NO strings de país
                  photo_url, raw_locale_fields }  # crudo preservado para auditoría
CONTRACT_VERSION
```
`currency` es la pieza que hoy **no existe en ningún sitio** de `pipeline/` (el `Vehicle` actual es `price: float|None` sin moneda [VERIFIED autoscout24.py:49]). Sin ella, EUR/JPY/MXN caen en la **misma columna `price`** y son indistinguibles. El cambio es un **bump de `CONTRACT_VERSION`** que toca aguas abajo (`ingest`/`delta`/served-facets) — estructural, no cosmético.

### Dónde entra la capa-2 IA local (hoy €0, 0 código)
**EXCLUSIVAMENTE en el Plano C** y SOLO para campos sucios irreducibles que ningún selector ni regla de locale resuelve: `make/model/variant` desde un título/descripción libre en peldaños `css|regex` (classifieds y CMS "cutres" sin make/model estructurado). La IA **NO toca jamás** un `next_data/json_api` que ya trae make/model. Salida **por gramática** (GBNF/constrained decoding): el modelo emite ÚNICAMENTE un JSON cerrado `{make ∈ brand_table ∪ null, model, fuel ∈ enum, transmission ∈ enum}` — imposible alucinar fuera del vocabulario del pack. **Gate de activación** (determinista-primero, Law I): se invoca el LLM sii (a) tras `normalize_vehicle` quedan `make` O `model` NULL **y** hay título/descripción; (b) el rung es `css|regex|llm_local` (nunca estructurado); (c) **piso**: la salida se acepta solo si `make ∈ brand_table`, si no se descarta y el campo queda NULL. Corre como `NormalizerLLM` Protocol con **fallback determinista** ("sin recuperación") → el sistema es idéntico con o sin modelo: hoy gana siempre el fallback (€0, dormante). Claude (capa-3) **nunca normaliza en caliente**; solo decide/orquesta en ráfagas (p.ej. aprobar un nuevo `field_map` de pack).

---

## Onboarding de país nuevo (pasos para esta etapa)

1. **Crear el árbol**: `countries/<CC>/recipes/` + `countries/<CC>/locale.yaml` + `countries/<CC>/brands.yaml`. ES es el pack #1 de referencia a copiar.
2. **Rellenar `LocaleProfile`**: `decimal_sep, thousand_sep, currency, price_max` (techo nacional **en moneda local**), `date_fmt, source_encoding, stock_hints, count_words, marketplace_blocklist` en el idioma del país.
3. **Declarar enum-maps**: `fuel_map` y `transmission_map` (label/código de la fuente → neutral `PETROL/DIESEL/EV/HYBRID`, `AUTOMATIC/MANUAL`), validados contra muestra real.
4. **Calibrar `brands.yaml`** con la distribución de marcas del país (top tokens de títulos make-null + distribución existente), HIGH precision: solo marcas conocidas, **nunca adivinar**. Para CJK, alias en el script nativo.
5. **Por cada fuente**: escribir `recipe_template` (`base_url`, `pagination.url_template+declared_path`, `parsing.container_path+field_map` en mini-DSL). **Reusar un `Selector` existente** si comparte engine (p.ej. `next_data` de `autoscout24.<tld>`).
6. **Fuente nueva sin engine reusable**: implementar el `Selector` ejecutable **una sola vez** (cae bajo el enum cerrado) — la única línea Python admisible; idealmente 0 si encaja en `next_data/json_api/jsonld/microdata/css`.
7. **Registrar los extractores** en `EXTRACTORS` (o registro por-país inyectado), sin tocar el arnés.
8. **Correr el arnés offline** sobre k=3-5 dealers piloto por fuente: verificar `parse_loss==0`, `status VERIFIED` **y el piso de normalización** (fill-rate make/fuel/transmission + vocab canónico — ver Sellado). Un FAILED trae razón precisa que apunta al `field_map` o al locale.
9. **Verificar round-trip de paths**: la receta se ESCRIBE y se LEE bajo `countries/<CC>/` (requiere el fix `complete.py:305/309` + regex `:89` aplicados — ver Costuras).
10. **Fixtures golden del país** (HTML/JSON capturados) + `test_recipe_<source>_<CC>` espejando los ES; al CI `db-tests/unit`. **El sello de 03 del país exige ESTOS fixtures verdes**, no los ES.
11. **Ejecutar el sello** (siguiente sección) en dry-run sobre `:5434`/efímero, comparar con golden, pasar Ferrari local + CI.
12. **(Opcional, diferido €0)** si quedan `make/model` irreducibles en rungs `css/regex`: añadir gramática GBNF del país y activar el gate de capa-2 cuando exista modelo local.

---

## Sellado + verificación multi-vía + rollback

### Criterio de SELLADO (etapa 03, por país) — **dos capas**
**Capa de conteo (existe hoy)**: cada fuente declarada tiene receta persistida con `status VERIFIED` y `evidence.parse_loss==0` sobre su sample acotado.
**Capa semántica (NUEVA — cierra SH1/SH2/SH3/SH6)**, sin la cual una receta "count-clean" puede ser servicialmente vacía:
- **Piso de fill-rate** sobre el sample: `make/model` y `fuel_code/transmission_code` por encima de un umbral (hoy `_valid()` solo exige `name + (price|url)` [VERIFIED recipe_extract_web.py:112-114] — insuficiente).
- **Check de vocabulario canónico**: `fuel_code/transmission_code ∈ enum`, `make ∈ brand_table` o explícitamente-desconocido-preservado, `currency` presente en toda fila con precio.
- **Reconciliación post-ingest**: para el piloto, `ingested_count > 0` **y** provincia resuelta dentro del `RegionScheme` del país (no rechazada en bloque — IT — ni mis-mapeada — JP/FR/DE). Hace **VISIBLE** el fallo silencioso que hoy queda aguas abajo del sello de receta.
- **Techo y enum-maps calibrados** contra muestra real, no asumidos.

> El 100% es un **INTERVALO**: cota inferior = fracción de fuentes con receta VERIFIED, `parse_loss 0` **y** capa semántica verde, con margen que encoge según crece el golden. Nunca un entero. **"Sellado" de 03 para el país X = fixtures de X verdes** (ES verde es necesario, no suficiente — SH4).

### Verificación por 2ª vía ortogonal
- **Vía primaria** = el propio arnés (`parse_loss` + VAM `record_count_verdict` sobre `declared/fetched/parsed`).
- **Vía ortogonal independiente** = **REPLAY desde YAML** en proceso limpio: re-extrae solo desde el YAML y exige `reproduced==True` (`parsed>0 ∧ loss==0`) — prueba autosuficiencia sin crudo. [VERIFIED·W1 recipe_harness.py:237-255].
- **3ª vía barata** = el VAM cruza el `declared` del oráculo de la fuente (`full_dealer`) contra `fetched/parsed` — familia de path distinta (source vs http vs db); un parser que invente filas es REFUTED.
- Sobre esto: **golden fixtures** (deterministas, sin red) + **Ferrari local** + **CI** (`db-tests/unit`) cierran la regresión.

### Rollback
Toda la etapa es **aditiva y reversible**. Las recetas son YAML versionados (`schema_version`) y commiteados; revertir = `git revert` del pack del país o restaurar el YAML previo (`write_recipe` loguea clobber semántico). El piloto se prueba en DSN efímero `:5434`, nunca en `:5433` productivo; el sample se borra siempre (`parsed.clear()`), así que **no hay crudo que limpiar**. Un `field_map`/`LocaleProfile` defectuoso se detecta como **FAILED-con-razón antes de tocar inventario**, y se revierte editando el pack **sin migración de datos**. El widening de regex/paths se protege con `xfail strict` hasta verde, de modo que **ES no regresiona** mientras se onboarda el país #2.

---

## Veredicto adversarial: roturas → resolución

`holds=false / NEEDS_REWORK`. La causa raíz transversal: **el `country_code` se enhebró en el ESQUEMA y el prefijo `cdp_code`, pero NO en la lógica de pipeline/serving** — todo es country-BLIND por debajo del esquema. Las 14 roturas + 9 missing-pack + 6 sealing-holes se agrupan en **11 familias de causa raíz**; ninguna se oculta. Mapeo íntegro al final.

> Cada rotura se diseca átomo a átomo en su **sub-proyecto institucional** — ver [Sub-proyectos institucionales (360 por faceta)](#indice-subproyectos). Mapeo familia→faceta: **F1**→[21](#faceta-21) · **F2**→[11](#faceta-11)/[12](#faceta-12) · **F3**→[14](#faceta-14) · **F4**→[15](#faceta-15) · **F5**→[18](#faceta-18)/[19](#faceta-19) · **F6**→[6](#faceta-6) · **F7**→[17](#faceta-17) · **F8**→[22](#faceta-22) · **F9**→[20](#faceta-20) · **F10**→[2](#faceta-2)/[1](#faceta-1)/[9](#faceta-9) · **F11**→[26](#faceta-26)/[8](#faceta-8)/[25](#faceta-25).

**F1 · GEO country-blindness** — `ingest.py:49-50` gate INE duro + `zip[:2]` como derivación de provincia.
Cubre: **B1**(JP 01-47⊂01-52 → mis-geo a provincia ES), **B7**(IT alfa `MI/RM` falla `isdigit()` → **país entero rechazado**, "no inventory" falso), **B9**(FR `75008`→Toledo), **B11**(DE PLZ no mapea a Land; `>52` dropeado, `≤52` mis-mapeado), **B13**(PT `NNNN-NNN` mal cortado), **MP3**, **MP4**, **SH3**.
→ **RESOLUCIÓN (cross-stage 03↔04)**: el parser de 03 **deja de derivar provincia** y emite **CP/region CRUDO + `country_code`**; el `RegionScheme` por país (formato+mapa+rango de validación) vive en el **geo-adapter de la etapa 4** sobre el PK `(country_code,code)` ya existente. DE necesita **tabla** PLZ→Land (no slice). El gate `'01'<=code<='52'` se sustituye por `RegionScheme.validate(raw, CC)`. La **reconciliación post-ingest** del sello (SH3) hace visible el rechazo/mis-geo silencioso. €0, aditivo. *Acoplado con F-paths (regex `:89` + lectura `:305/:309`) — mismo PR, verificar round-trip.*

**F2 · CURRENCY absent** — no hay dimensión moneda en el contrato.
Cubre: **B3**(JP en columna `price` EUR-compartida), **B6**(MXN indistinguible de €350k), **MP1**, **MP2**, **SH2**.
→ **RESOLUCIÓN €0 (bump `CONTRACT_VERSION`)**: `CanonicalVehicle.currency` + capturar `priceCurrency` (hoy descartado en `recipe_extract_web.py:79`) + `currency` por defecto del pack. El sello se vuelve currency-aware (SH2). Toca aguas abajo (`ingest/delta/facets`) — estructural pero aditivo. *Ver O3 (recompute ES) por el lado de PROD-write.*

**F3 · NUMBER parse corruption** — parser EU disperso asume dot=miles/comma=decimal.
Cubre: **B5**(MX `1,234.56` leído ~1000× mal y pasa sanity), **MP8**, y el latente `recipe_extract_web.py:104` (`'24.900'`→24.9).
→ **RESOLUCIÓN €0**: un solo `parse_money(text, LocaleProfile)` (Plano C) con convenciones invertidas + NBSP. **Reconstrucción de corrección**, no swap de separador; los parsers EU dispersos (`dealerprobe:127/256`, `family_builder:167`, `family_cms:345`) colapsan en uno. *Ver O3.*

**F4 · PRICE ceiling EUR-bound** — `PRICE_MAX=5_000_000` en euros.
Cubre: **B2**(JP NULLea mercado legítimo).
→ **RESOLUCIÓN €0**: `price_max` por `LocaleProfile` (ES ~€5M, JP ~¥50-100M) + comparación **currency-aware** (depende de F2). La lógica de sentinelas "all-9s" pasa a set por locale. *Ver O3.*

**F5 · ENUM fuel/transmission sin normalizar, objetivo español** — `ingest.py:101` verbatim; canon de-facto ES.
Cubre: **B8**(IT `Benzina/Automatico` fragmenta vs ES), **B12**(DE `Benzin/Automatik`), **B14**(PT colisión "por suerte" en `Gasolina` pero diverge `Gasóleo/Elétrico/Caixa automática`), **MP5**.
→ **RESOLUCIÓN €0 en el borde + O2 aguas abajo**: `fuel_map/transmission_map` por locale → códigos neutrales, normalizado en ingest como `make`. **PERO** la served-surface filtra hoy por **labels españoles**: migrar facetas a códigos neutrales (o estandarizar el pack en el canon ES existente) — **no es "solo un dict"**, toca la served-of-record → **O2 (gate PROD-write, dry-run primero)**.

**F6 · LEXICON español incrustado en el motor** — `_STOCK_HINT/_COUNT_HINT/_MARKETPLACES`.
Cubre: **B10**(FR `'occasion'≠'ocasion'` → recipe FAILED), parte de **B12**(DE `'Fahrzeuge'`).
→ **RESOLUCIÓN €0**: `LocaleProfile.stock_hints/count_words/marketplace_blocklist` inyectados al `GenericWebExtractor`.

**F7 · TITLE segmentation Latin-only** — `make_from_title` `split()[0]` + `_CANON` Latin.
Cubre: **B4**(JP `トヨタプリウス` → string entero, recuperación de marca muerta; **el diseño lo llamó "motor puro" — falso**), **MP6**.
→ **RESOLUCIÓN €0 (deterministe, script-agnóstico)**: reemplazar `split()[0]` por **match anclado en `brand_table`** (longest-alias prefix/substring) — funciona para Latin **y** CJK con los alias del pack (`日産/トヨタ/…`). Para DE/FR/IT/PT (Latin space-delimited) es byte-idéntico a hoy. El **LLM capa-2 NO es necesario** para esto; queda como lever diferido solo para `variant`/`model` desde free-text (**O1**).

**F8 · ENCODING non-UTF-8 source** — conectores solo fijan stdout UTF-8.
Cubre: **MP7**(Shift-JIS/EUC-JP).
→ **RESOLUCIÓN €0**: `Transport.charset` (pack) + decode al borde de fetch (Plano A).

**F9 · DATE format per locale** — sin `parse_date` en el pack.
Cubre: **MP9**(`dd.mm.yyyy` DE, `yyyy年mm月dd日` JP).
→ **RESOLUCIÓN €0**: `parse_date(text, LocaleProfile)` (Plano C). JP necesita tokens de fecha CJK (menor, dentro de €0).

**F10 · RECIPE no ejecutable** — `engine` `str` libre + `field_map` descriptivo.
Cubre: es_seam `recipe_schema.py:67` + `recipe_extractors.py:245/130` (la receta no es pack ejecutable; replay re-corre Python).
→ **RESOLUCIÓN €0 (estructural)**: enum `Selector` + mini-DSL `field_map` (Plano B). El extractor se vuelve intérprete; la receta se vuelve el pack. *Cerrar el enum en `__post_init__` puede romper las 61 recetas ES con engine de texto libre → **O4** (alias-compat/migración antes del strict).*

**F11 · SEAL count-only (semánticamente ciego)**.
Cubre: **SH1**(sella con make/fuel/transmission NULL), **SH4**(tests certifican ES, no el país), **SH5**(**[CORREGIDO]** 641 vs 61 — narrativa de certificación con cifra mal atribuida), **SH6**(país "sellado pero servicialmente vacío"). SH2/SH3 atan a F2/F1.
→ **RESOLUCIÓN €0**: la **capa semántica** del sello (fill-rate floor + vocab canónico + currency-present + reconciliación post-ingest + fixtures por país). **SH5 corregido aquí**: el sello cuenta el **flat `countries/<CC>/recipes`** (lo que el arnés escribe), no el árbol geo — ES = **61**, no 641.

### Mapeo íntegro (ninguna rotura oculta)
| ID | país/área | familia | estado |
|---|---|---|---|
| B1 | JP geo | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| B2 | JP precio | F4 | RESUELTO €0 (dep. F2) · O3 |
| B3 | JP moneda | F2 | RESUELTO €0 (bump contrato) |
| B4 | JP make | F7 | RESUELTO €0 · O1 (solo variant) |
| B5 | MX número | F3 | RESUELTO €0 · O3 |
| B6 | MX moneda | F2 | RESUELTO €0 |
| B7 | IT geo (rechazo total) | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| B8 | IT enum | F5 | RESUELTO €0 borde · O2 served |
| B9 | FR geo | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| B10 | FR léxico stock | F6 | RESUELTO €0 |
| B11 | DE geo (PLZ tabla) | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| B12 | DE enum+léxico | F5+F6 | RESUELTO €0 · O2 served |
| B13 | PT geo | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| B14 | PT enum | F5 | RESUELTO €0 borde · O2 served |
| MP1 | currency field | F2 | RESUELTO €0 |
| MP2 | ceiling local-units | F4 | RESUELTO €0 (dep. F2) |
| MP3 | postcode→region | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| MP4 | region validator pack | F1 | RESUELTO-CROSS-STAGE(04) €0 |
| MP5 | fuel/trans engine-applied | F5 | RESUELTO €0 borde · O2 served |
| MP6 | CJK segmentation | F7 | RESUELTO €0 (brand-anchor) · O1 variant |
| MP7 | charset/encoding | F8 | RESUELTO €0 |
| MP8 | number-format invertido | F3 | RESUELTO €0 · O3 |
| MP9 | date per locale | F9 | RESUELTO €0 |
| SH1 | seal sin normalización | F11 | RESUELTO €0 |
| SH2 | seal currency-blind | F11(+F2) | RESUELTO €0 (dep. F2) |
| SH3 | gate aguas abajo invisible | F11(+F1) | RESUELTO €0 (reconciliación) |
| SH4 | fixtures solo ES | F11 | RESUELTO €0 (proceso) |
| SH5 | 641 vs 61 mal atribuido | F11 | **CORREGIDO aquí** |
| SH6 | sellado-pero-vacío | F11 | RESUELTO €0 |

---

## Mejoras a nivel inalcanzable (€0, priorizadas)

1. **`field_map` ejecutable (intérprete mini-DSL)** — el replay normaliza puramente desde el YAML, no re-ejecutando Python; un país/fuente nuevo pasa a 100% pack declarativo. Es el salto que vuelve la receta un activo autosuficiente real. *Effort L · €0.*
2. **Módulo locale único `parse_money/parse_date` + `normalize_vehicle`** — absorbe los parsers EU dispersos y elimina la incoherencia de bounds 5M-vs-1.5M. *Effort M · €0.* (Prerrequisito de F3/F4/F9.)
3. **Canonicalizar fuel/transmission a códigos neutrales por pack** — arregla el eje de búsqueda cross-país que hoy guarda `'Automatico'/'Diesel'` en español. *Effort S · €0.*
4. **Dimensión `currency` en el contrato** — sin ella ninguna corrección de precio cross-país es coherente; habilita el sello currency-aware. *Effort S-M · €0.* (Prerrequisito de F2/F4/SH2.)
5. **Anclaje de `make` por `brand_table` (script-agnóstico)** — mata el acoplamiento Latin-only €0, sin esperar al LLM. *Effort S · €0.*
6. **Cerrar `Parsing.engine` a enum validado en `__post_init__`** — una receta corrupta falla al cargar, no al ejecutar. *Effort S · €0* (con O4: alias-compat para las 61 ES).
7. **Property-based testing (Hypothesis)** del contrato de normalización: invariantes `km>=0 o None`, `parse_money` idempotente, `make` canónico estable — caza el caso de locale raro (CP no-INE, separador mixto) que el golden no cubre. *Effort M · €0.*
8. **Capa-2 IA local con GBNF** (terminales = `brands.yaml` + enums) para `make/model` irreducibles en `css/regex`, gate determinista-primero + piso `make∈brand_table`. Seam pre-cableado €0 con fallback determinista (motor idéntico con o sin modelo). *Effort L · €0 hoy; modelo = lever €>0 (O1).*
9. **Auto-detección de `LocaleProfile` por muestreo** (inferir decimal/miles/divisa de una página) para semilla del pack, revisada por humano. *Effort M · €0* (requiere `parse_money` centralizado primero).

---

## Riesgos / open items

### Riesgos (acoplamientos a vigilar)
- **R1 · Acoplamiento regex+paths**: el widening de `complete.py:89` y de la lectura `:305/:309` deben ir **en el mismo PR**; arreglar uno sin el otro deja una receta de país nuevo **escrita-pero-no-encontrada** (asimetría write/read). Verificar round-trip.
- **R2 · Recompute ES**: centralizar bounds en `normalize_vehicle` puede CAMBIAR valores ya servidos en ES (km que hoy queda en 5M pasaría a 1.5M); el peldaño web sin `parse_money` EU (`recipe_extract_web.py:104`) ya puede estar sirviendo `'24.900'`→24.9. **Auditar el daño existente** antes de declarar 03 sellada en ES.
- **R3 · Capa-2 sin piso**: activar el LLM sin el gate `make∈brand_table` viola Law I (mis-fill > under-fill) y contamina el eje de búsqueda. El piso gramatical es **no-negociable**.
- **R4 · Enum strict vs assets existentes**: cerrar `Parsing.engine` a enum puede romper las **61** recetas ES con engine de texto libre → migración o alias-compat antes del strict.
- **R5 · Sesgo ES disfrazado de motor**: la `brand_table` y los enum-maps grounded en ES **no son universales**; asumir que valen para el país #2 sin re-muestrear su distribución real reintroduce sesgo. El pack se **calibra contra muestra real**, no se hereda.
- **R6 · Paridad golden del intérprete**: el `field_map` ejecutable es un cambio estructural grande; hacerlo sin **paridad byte-idéntica** contra los 5 extractores actuales arriesga regresión silenciosa en el parse de ES.

### Open items (gated — no bloquean el loop; PENDING-OWNER donde aplica)
- **O1 · Capa-2 LLM (free-text make/model/variant)** — *causa*: requiere un modelo local; *gate*: **GASTO €>0** (palanca GPU con caso de uso probado + firma). El seam está pre-cableado €0 con fallback determinista; la recuperación de `make` para ES y la marca CJK ya son €0 vía `brand_table`. **Solo el `variant`/`model` desde descripción libre (incl. CJK) queda diferido.** No es blocker.
- **O2 · Migración de facetas served off-Spanish (fuel/transmission)** — *causa*: la served-of-record filtra hoy por labels españoles; *gate*: **ESCRITURA EN PROD** (dry-run `:5434` → golden → Ferrari → CI antes de `:5433`). Acoplamiento etapa 7/8. La normalización en el borde (03) es €0 e inmediata; la migración del consumo es lo gateado.
- **O3 · Recompute ES de precios/km bajo el módulo locale centralizado** — *causa*: alteraría valores ya servidos y podría falsear deltas `KM_CHANGE/PRICE_CHANGE`; *gate*: **PROD-write/recompute auditado** (no en caliente). Secuenciado, no bloqueado.
- **O4 · Strict enum sobre las 61 recetas ES** — *causa*: assets ya persistidos con engine de texto libre; *gate*: build-order (alias-compat/migración antes del `__post_init__` strict). No es €/legal/prod.
- **O5 · Segmentación/extracción CJK más allá del prefijo de marca** — diferido con O1; el brand-anchor €0 cubre la marca, no el `model/variant` fino en script no-Latin.

> **Sin las tres vías (test verde + intento adversarial fallido + verificación independiente) un mecanismo queda `[ASSUMED]`, no `[VERIFIED]`.** Esta etapa está `NEEDS_REWORK` hasta que la capa semántica del sello + la dimensión moneda + el módulo locale aterricen con fixtures por país verdes. Antes confesar el hueco que vender la coherencia.

---

<a id="indice-subproyectos"></a>

## Sub-proyectos institucionales (360 por faceta)

> **Qué es esta sección.** La etapa Extraer/Normalizar descompuesta en sus **26 átomos de código**, cada uno tratado como un **proyecto institucional independiente a 360°**: deep-spec verificado al átomo (`[VERIFIED path:línea]`) + **costura** ES→genérico + **fix** exacto + **adversarial** concreto (DE/FR/IT/PT/JP/MX/no-UE) + **sellado** multi-vía fail-closed + **herramienta NEXT-LEVEL €0** battle-tested. Es el mismo sistema del §Veredicto, visto por **autoridad-de-código** en vez de por síntoma: las 14 roturas (B) + 9 missing-pack (MP) + 6 sealing-holes (SH) viven distribuidas aquí, ancladas a las 11 familias de causa raíz (F1–F11).
>
> **Cómo leerla (funnel: nadie se pierde).** El cuerpo va en **orden numérico 1→26** (predecible); el [índice por familia](#indice-familias) de abajo es la **lente temática**. Cada faceta usa el **mismo esquema fijo** de [04-identity](04-identity.md)/[05-vehicle](05-vehicle.md): la cita `>` bajo el título es el **estado de batalla** (rotura ligada · familia F# · gate); luego **(a) code_hints** verificados → **(b) mecanismo al átomo** → **(c) costura** → **(d) adversarial** → **(e) sellado** → **(f) herramienta**, y cierra con una **Resolución condensada** accionable. Toda referencia `faceta N` es un enlace; cada faceta cierra con `[⇧ Índice]`.
>
> **Doctrina honrada en cada faceta (del MASTER):** sample-verify-delete (la receta es el activo, cero crudo) · VAM cero-confianza (ningún número sin quórum ≥2 vías ortogonales) · determinista-primero, IA local como residuo con salida por gramática · **€0** de cimiento · dry-run(`:5434`)→golden→Ferrari→CI antes de tocar lo servido · «antes confesar un hueco que vender una mentira». Los **open items se declaran con causa y gate** (O1–O5), nunca se ocultan. Honestidad cruda: lo `[CORREGIDO]`/`[VERIFIED]` manda sobre cualquier narrativa de la Ola-1.

<a id="indice-familias"></a>

### Índice navegable (26 sub-proyectos por familia)

**A · Activo-receta — esquema, selector ejecutable, autosuficiencia, persistencia**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **1** | [Esquema-receta durable y versionado](#faceta-1) | Activo-receta · esquema YA country-agnóstico. |
| **2** | [Motor de selectores ejecutables (`Parsing.engine` enum + `field_map` mini-DSL)](#faceta-2) | F10 · RECIPE no ejecutable. |
| **9** | [Replay / prueba de autosuficiencia (`RecipeRunner.replay`)](#faceta-9) | 2ª vía ortogonal · independencia ilusoria. |
| **23** | [Enrutado de paths por país + round-trip write/read + integridad de persistencia](#faceta-23) | Asimetría write/read (persistencia). |

**B · Plano A · ACQUIRE — transporte, fingerprint, encoding**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **10** | [Plantilla de transporte/paginación capturada + oráculo `declared`](#faceta-10) | Plano A — ACQUIRE. |
| **22** | [Decodificación de charset/encoding de la página fuente](#faceta-22) | F8 · ENCODING non-UTF-8. |

**C · Plano B · LOCATE — registro + familias de selector**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **3** | [Registro y protocolo de extractores enchufables](#faceta-3) | País-agnóstico salvo el registro. |
| **4** | [Familia de selector estructurado Tier-0 (`next_data` / `json_api`)](#faceta-4) | F10 · rung coste-0 estructurado |
| **5** | [Familia enumerate-then-hydrate (autocasion SSR-ref + GraphQL ad)](#faceta-5) | F10 · 2-fase enumerate-then-hydrate |
| **6** | [Rung web genérico de concesionario (JSON-LD/microdata) + descubrimiento de stock](#faceta-6) | F6 · LÉXICON español incrustado |

**D · Plano C · NORMALIZE — orquestador locale → canónico**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **13** | [Orquestador `normalize_vehicle` + objeto `LocaleProfile`](#faceta-13) | Plano C — pieza-llave. |
| **14** | [Motor `parse_money` / formato numérico (rebuild de corrección)](#faceta-14) | F3 · NUMBER parse corruption. |
| **20** | [Parsing de fecha/matriculación por locale (`parse_date`)](#faceta-20) | F9 · DATE format per locale. |
| **16** | [Gates de física km/year + cross-field + de-duplicación de bounds inline](#faceta-16) | Física universal, aplicación divergente. |
| **15** | [Calibración del techo de precio (`PRICE_MAX`) currency-aware](#faceta-15) | F4 · PRICE ceiling EUR-bound. |
| **17** | [Canonicalización de `make` (algoritmo + tabla de marcas + segmentación CJK)](#faceta-17) | F7 · TITLE segmentation Latin-only. |
| **18** | [Canonicalización de enum `fuel` (`fuel_map` locale→código neutral)](#faceta-18) | F5 · ENUM fuel sin normalizar. |
| **19** | [Canonicalización de enum `transmission` (`transmission_map` locale→código neutral)](#faceta-19) | F5 · ENUM transmission. |

**E · Contrato de salida + dimensión moneda**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **11** | [Contrato de salida `CanonicalVehicle` unificado y versionado](#faceta-11) | F2 · CURRENCY absent (contrato). |
| **12** | [Dimensión MONEDA (`currency`) extremo-a-extremo](#faceta-12) | F2 · CURRENCY absent — CRITICAL. |

**F · Geo cross-stage (03↔04)**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **21** | [Emisión postcode→region en extracción + gate INE en ingest](#faceta-21) | F1 · GEO country-blindness — el más grave de la etapa. |

**G · Verificación, sello y cobertura**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **7** | [Ciclo del arnés y pureza del veredicto (EXTRACT→VERIFY→PERSIST→DELETE)](#faceta-7) | Columna country-agnóstica · costura = profundidad de sello. |
| **8** | [Verificación VAM de integridad de conteo (declared/fetched/parsed)](#faceta-8) | F11 · SEAL count-only (raíz). |
| **25** | [Fixtures golden/Ferrari/property-based por país](#faceta-25) | F11 · SEAL. |
| **26** | [Definición del SELLO de la etapa (normalization-aware)](#faceta-26) | F11 · SEAL count-only — meta-faceta. |

**H · Capa-2 IA local (dormante €0)**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **24** | [Seam capa-2 IA local (`NormalizerLLM` dormante €0 + gate GBNF)](#faceta-24) | Capa-2 IA local · seam dormante €0. |

> El cuerpo sigue en orden numérico; el índice de arriba es la lente temática. Mapeo veredicto→faceta: **F1**→21 · **F2**→11/12 · **F3**→14 · **F4**→15 · **F5**→18/19 · **F6**→6 · **F7**→17 · **F8**→22 · **F9**→20 · **F10**→2/1/9 (+3/4/5/10) · **F11**→26/8/25 (+11/12).

---

<a id="faceta-1"></a>

### Faceta 1 — Esquema-receta durable y versionado

> **Activo-receta · esquema YA country-agnóstico.** La costura no es de idioma sino de **gobierno de evolución**: cerrar `engine`/`strategy` a enum + añadir `currency`/`fuel_code` de forma ADITIVA sin romper las 61 recetas flat. **Liga:** F10. **Cross-ref:** facetas [2](#faceta-2)·[10](#faceta-10)·[11](#faceta-11).

#### (a) Code_hints [VERIFIED]
- `pipeline/recipe_schema.py:27` `SCHEMA_VERSION = 2` [VERIFIED].
- `:30-33` vocabulario CERRADO `STATUS_DRAFT/VERIFIED/FAILED` + `_VALID_STATUS = {...}` [VERIFIED].
- Dataclasses: `Transport :36-42`, `Fingerprint :45-50`, `Pagination :53-60`, `Parsing :63-69`, `Evidence :72-93`, `Recipe :96-110` [VERIFIED] (6 dataclasses, coincide con el scope).
- `:112-115` `__post_init__` lanza `ValueError` si `status not in _VALID_STATUS` — OJO: valida SOLO `status`, NO `schema_version` [VERIFIED].
- `:118-140` `to_dict` emite las claves en un ORDEN deliberado fijo (schema_version->source->...->evidence), no confia en el orden de `asdict` [VERIFIED].
- `:142-167` `from_dict`: helper `_sub` (`:149-152`) filtra a los campos validos del dataclass (`valid = {f for f in klass.__dataclass_fields__}`, `{k:v ... if k in valid}`) IGNORANDO claves extra; bloques ausentes -> defaults; `schema_version=d.get('schema_version', SCHEMA_VERSION)` (`:161`) [VERIFIED].

#### (b) Mecanismo al atomo
La `Recipe` es el ASSET YAML durable; la (de)serializacion round-trippa via `to_dict` (orden estable) / `from_dict` (defensivo). El par 'vocabulario cerrado + `__post_init__`' es el guard anti-ambiguedad: una receta jamas vive en estado sin nombre. El ATOMO de la forward-compat es el filtro `_sub`: un fichero MAS nuevo con claves extra NO rompe un loader viejo porque las claves desconocidas se descartan (`if k in valid`); inversamente, un bloque ausente cae a default de dataclass. `schema_version` se LEE pero NO se valida ni migra: un v3 cargaria bajo un loader v2 silenciosamente con los defaults de los campos que el v2 no conoce.

#### (c) Costura ES->generico
El esquema YA es country-agnostico: no hay literales ES en `recipe_schema.py` (los unicos datos ES son `base_url`/`url_template`, y son VALORES por-receta, no forma del dataclass). La costura es el GOBIERNO de evolucion: (1) cerrar `Parsing.engine` (`:67`, hoy `str` libre) y `Pagination.strategy` (`:56`, hoy `str` libre) a enum romperia las 61 recetas flat persistidas con engine texto-libre ('ssr_ref_re + graphql_ad'); (2) anadir `currency`/`fuel_code`/`raw_locale_fields` debe ser ADITIVO (from_dict ya tolera ausencia via defaults; to_dict debe anadirlas al mapa ordenado). La regla 'un pais nuevo NO toca el esquema' se sostiene porque los paises varian solo en DATOS por-receta.

#### (d) Riesgo adversarial concreto
Cerrar `engine`/`strategy` a enum estricto rompe las 61 recetas flat con engine texto-libre -> fallo de CARGA en masa, salvo mapa de alias de compat. Un pais #2 que escriba `schema_version > 2` debe seguir leyendose por el loader ES (hoy `from_dict` lo lee pero NO valida/migra: un cambio estructural en v3 se mis-cargaria bajo defaults v2). Recetas DE/FR/IT que anaden `currency`/`fuel_code` no deben romper recetas ES que carecen de ellos — los defaults de `from_dict` lo cubren [VERIFIED seguro hoy].

#### (e) Sellado + verificacion multi-via
Criterio: (1) round-trip golden `Recipe.from_dict(r.to_dict()) == r` byte-identico para las 61 recetas commiteadas (cero drop de campo, orden de clave estable); (2) forward-compat: un YAML v3 sintetico con claves extra + campos nuevos carga sin raise y sin perder campos conocidos; (3) backward-compat: un YAML v2 (sin currency/fuel_code) carga bajo loader v3 con defaults; (4) enum-closure: cada uno de los 61 strings engine texto-libre mapea via alias a un miembro de enum valido (cero unmapped). Multi-via ortogonal: validacion-de-schema (Frictionless en CI) ⟂ unit round-trip ⟂ integracion load-all-committed-recipes.

#### (f) Herramienta NEXT-LEVEL
Frictionless Framework (frictionless-py, Table Schema), MIT, https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Declara el esquema de receta/pack como CONTRATO de datos versionado y aditivo, validado en el bootstrap ANTES de cargar (la doctrina COUNTRY-PROOF aplicada a la propia forma del asset): tipo + ancho-de-codigo + regex fallan un pack malformado con mensaje claro en vez de un crash tardio de loader/Postgres. Alternativas en biblia: Pandera, JSON Schema + jsonschema, Great Expectations. Adyacente: DVC (Apache-2.0, https://github.com/iterative/dvc, NEXT-LEVEL.md:151) para versionado content-addressed del corpus de recetas commiteado, de modo que un bump de schema sea reconstruible bit-a-bit.

#### Resolución condensada — Faceta 1
- **Costura** · El esquema ya es country-agnostico (cero literales ES; base_url/url_template son valores por-receta). La costura real es de GOBIERNO: Parsing.engine (recipe_schema.py:67) y Pagination.strategy (:56) son str libres hoy; cerrarlos a enum romperia las 61 recetas flat persistidas, y anadir currency/fuel_code/raw_locale_fields debe ser aditivo. schema_version se lee (:161) pero no se valida ni migra.
- **Fix** · En recipe_schema.py: (1) anadir campos opcionales con default (currency:str|None=None en bloque de precio, fuel_code/transmission_code, raw_locale_fields:dict=field(default_factory=dict)) y apendarlos al mapa ordenado de to_dict (:126-139); bump SCHEMA_VERSION 2->3. (2) Al cerrar engine/strategy a enum, anadir _ENGINE_ALIAS={'ssr_ref_re + graphql_ad':'ssr_enumerate_then_gql_hydrate',...} y mapear en from_dict antes de construir Parsing, con fallback que sigue aceptando desconocidos. (3) Branch schema_version-aware en from_dict para cualquier cambio no-aditivo. El filtro defensivo _sub (:149-152) ya es el mecanismo de compat y se conserva.
- **Adversarial** · Cerrar engine/strategy a enum estricto rompe la CARGA en masa de las 61 recetas flat con engine texto-libre si no hay alias de compat. Un pais #2 con schema_version>2 debe seguir leyendose por el loader ES (hoy from_dict lo lee pero NO migra: un v3 estructural se mis-cargaria bajo defaults v2). Recetas DE/FR/IT con currency/fuel_code no deben romper recetas ES sin ellos (defaults lo cubren, VERIFIED seguro hoy).
- **Sellado (multi-vía)** · (1) round-trip golden from_dict(to_dict)==r byte-identico sobre las 61 recetas; (2) forward-compat: YAML v3 con claves extra carga sin raise ni perdida; (3) backward-compat: YAML v2 carga bajo loader v3 con defaults; (4) enum-closure: los 61 engine texto-libre mapean a enum (cero unmapped). Multi-via: validacion-schema Frictionless (CI) ⟂ unit round-trip ⟂ integracion load-all-committed-recipes.
- **Herramienta NEXT-LEVEL (€0)** · Frictionless Framework (frictionless-py, Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Esquema como contrato de datos versionado y aditivo, validado en bootstrap antes de cargar (COUNTRY-PROOF aplicado a la forma del asset). Alt: Pandera, JSON Schema, Great Expectations. Adyacente: DVC (Apache-2.0, https://github.com/iterative/dvc, NEXT-LEVEL.md:151) para versionado content-addressed del corpus de recetas.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-2"></a>

### Faceta 2 — Motor de selectores ejecutables (`Parsing.engine` enum + `field_map` mini-DSL)

> **F10 · RECIPE no ejecutable.** `Parsing.engine` str libre + `field_map` prosa ⇒ la receta es config, no programa; el replay re-corre Python. **Cross-ref:** facetas [1](#faceta-1)·[9](#faceta-9)·[4](#faceta-4)·[5](#faceta-5)·[6](#faceta-6).

#### (a) Verificacion de code_hints contra el codigo real
- [VERIFIED pipeline/recipe_schema.py:67] `engine: str = "next_data"` con comentario `# next_data | jsonld | css | llm_local`: es **texto LIBRE**, no un enum. El comentario enumera valores pero nada los obliga.
- [VERIFIED pipeline/recipe_schema.py:69] `field_map: dict[str, str] = field(default_factory=dict)`: un dict de PROSA, no de path-expressions.
- [VERIFIED pipeline/recipe_schema.py:112-115] `__post_init__` valida **solo** `status` (`if self.status not in _VALID_STATUS: raise ValueError`); `engine`/`strategy` jamas se validan.
- [VERIFIED pipeline/recipe_extractors.py:245] `engine="ssr_ref_re + graphql_ad"`: un string compuesto que **no encaja en ningun enum** existente.
- [VERIFIED pipeline/recipe_extractors.py:129] `"deep_link": "canonical_deep_link(visibleId)"`: una llamada-de-funcion EN PROSA. Idem :63 `"host + listing.url"`, :196 `"transmissionTypeId->map"`, :136 `"image|imageList[0].name"`, :188/:248 `"_PDP_BASE + url"`, :67 `"listing.firstRegistrationDate|tracking.firstRegistration -> YYYY"`.
- [VERIFIED pipeline/recipe_harness.py:228-231] disclaimer: *"a fully field-map-driven interpreter ... is deliberately NOT claimed here — the extractor still owns the parse code."*
- [VERIFIED pipeline/recipe_harness.py:248] `sample = EXTRACTORS[recipe.source]().sample(recipe.dealer_ref, k)`: el replay **re-ejecuta Python**, no interpreta el field_map.

#### (b) El mecanismo al atomo
`Parsing.engine` es un `str` libre cuyo unico "tipado" es un comentario; `field_map` es `dict[str,str]` de descripcion humana. El harness NUNCA interpreta: para reproducir, llama al Python del modulo (`EXTRACTORS[source]().sample`). Atomo: `"canonical_deep_link(visibleId)"` no es un path navegable — es una instruccion que solo un humano (o el Python de la fuente) sabe ejecutar; `"image|imageList[0].name"` codifica un *pick-first + index + attr* que ningun motor generico lee. Consecuencia: la receta es **config descriptiva**, no **programa**; solo existen 5 extractores y cada fuente nueva exige Python nuevo.

#### (c) Costura ES->generico + fix exacto
- **Costura:** engine como texto libre + field_map como prosa => la receta no es autosuficiente; el "interprete" es Python-por-fuente.
- **Fix:** (1) Cerrar `Parsing.engine` a enum `{next_data, json_api, jsonld, microdata, css, regex_hydrate, llm_local}` validado en `__post_init__` (espejo del guard de `status`), con **bump SCHEMA_VERSION 2->3 + alias de compat** (`"ssr_ref_re + graphql_ad"` -> `regex_hydrate`/engine compuesto declarado) para no romper las 61 recetas flat. (2) Definir `Protocol Selector` con `locate(raw: bytes, container_path: str, field_map: dict) -> list[dict]`, una clase por engine. (3) Convertir field_map a **mini-DSL cerrado** que exprese pick-first `a|b`, composicion `host + path`, map-enum `map:transmission`, index `images[0].href`. (4) **Paridad golden byte-identica** contra los 5 parsers antes de cortar.

#### (d) Riesgo adversarial concreto
- Un DSL incompleto que no exprese `a|b` o `images[0].href` fuerza caida a Python => autoscout24.**de** next_data volveria a exigir codigo, rompiendo "pais nuevo = 100% YAML".
- Cerrar el enum sin alias rompe al CARGAR las 61 recetas con engine texto-libre (un loader post-corte que valide engine las rechaza en masa).
- Reescritura sin paridad => regresion **silenciosa** en el parse ES de 2.3M vehiculos (un field_map mal portado altera un precio/km sin test rojo).
- **DE/FR/IT:** `transmissionTypeId` 3/4 no visto en ES cae a `None` silencioso si `map:enum` no declara el caso-no-visto como FAILED.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** enum cerrado y validado en `__post_init__`; los 5 extractores ES reescritos como field_map interpretado producen `Vehicle` byte-identico; un field_map con path inexistente FALLA al CARGAR (validacion de DSL), no al ejecutar.
- **Via 1 (test):** paridad golden byte-identica de los 5 extractores ES.
- **Via 2 (adversarial):** field_map con path-fantasma rechazado en carga, no en runtime.
- **Via 3 (independiente):** `RecipeRunner.replay` en proceso limpio interpreta el YAML y reproduce el sample SIN importar el modulo Python de la fuente (cierra el acople con facet 9).

#### (f) Herramienta NEXT-LEVEL
**parsel** (CSS+XPath+JMESPath+regex) — [VERIFIED NEXT-LEVEL.md:264] https://github.com/scrapy/parsel, **BSD-3-Clause, EUR0=True**. Nucleo de Scrapy (battle-tested). Cada engine del enum mapea a un `Selector.locate(bytes, container_path, field_map)->list[dict]` sobre parsel + jsonpath-ng (JSONPath para next_data/json_api) + selectolax (Lexbor, ~25x BeautifulSoup). CPU puro, pip-install. Convierte "receta como config" en "receta como PROGRAMA".

#### Resolución condensada — Faceta 2
- **Costura** · Parsing.engine es str libre (recipe_schema.py:67, sin guard en __post_init__ que solo valida status:112-115) y field_map es dict[str,str] de PROSA (recipe_extractors.py:129 'canonical_deep_link(visibleId)', :196 'transmissionTypeId->map'); el engine 'ssr_ref_re + graphql_ad' (:245) no encaja en ningun enum. La receta es config descriptiva, no programa: cada fuente nueva exige Python (solo 5 extractores).
- **Fix** · 1) Cerrar Parsing.engine a enum {next_data,json_api,jsonld,microdata,css,regex_hydrate,llm_local} validado en __post_init__ (espejo del guard de status) + bump SCHEMA_VERSION 2->3 con alias de compat para las 61 recetas texto-libre. 2) Protocol Selector.locate(raw:bytes,container_path:str,field_map:dict)->list[dict], una clase por engine. 3) field_map -> mini-DSL cerrado: pick-first a|b, composicion host+path, map:enum, index images[0].href. 4) Paridad golden byte-identica vs los 5 parsers ANTES de cortar.
- **Adversarial** · DSL incompleto (sin a|b, sin images[0].href) fuerza caida a Python => autoscout24.de next_data reexige codigo, rompe 'pais nuevo=100% YAML'. Cerrar enum sin alias rompe la CARGA de las 61 recetas con engine texto-libre. Reescritura sin paridad = regresion silenciosa en 2.3M vehiculos ES. DE/FR/IT: transmissionTypeId 3/4 no-visto cae a None silencioso si map:enum no marca el caso-no-visto FAILED.
- **Sellado (multi-vía)** · Sello: enum cerrado+validado en __post_init__; 5 extractores ES reescritos producen Vehicle byte-identico; field_map con path inexistente FALLA al CARGAR no al ejecutar. Multi-via: (1) paridad golden byte-identica de los 5 ES; (2) adversarial = path-fantasma rechazado en carga; (3) independiente = RecipeRunner.replay en proceso limpio interpreta el YAML sin importar el Python de la fuente.
- **Herramienta NEXT-LEVEL (€0)** · parsel (CSS+XPath+JMESPath+regex) [VERIFIED NEXT-LEVEL.md:264] https://github.com/scrapy/parsel BSD-3-Clause EUR0=True. Nucleo de Scrapy; cada engine -> Selector.locate(bytes,container_path,field_map)->list[dict] sobre parsel+jsonpath-ng+selectolax. CPU puro, pip-install. Convierte receta-config en receta-programa.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-3"></a>

### Faceta 3 — Registro y protocolo de extractores enchufables

> **País-agnóstico salvo el registro.** `EXTRACTORS` dict-módulo global SIN eje país ⇒ el homónimo `autoscout24` ES/DE/IT/FR colisiona en silencio. **Cross-ref:** facetas [2](#faceta-2)·[9](#faceta-9)·[4](#faceta-4)·[5](#faceta-5).

#### (a) Verificacion de code_hints [VERIFIED]
- **EXTRACTORS global** `pipeline/recipe_extractors.py:280-286` [VERIFIED]: dict de modulo keyed por el **nombre desnudo** del source — `{"autoscout24":AutoScout24Extractor, "web_generic":GenericWebExtractor, "coches_com":CochesComExtractor, "coches_net":CochesNetExtractor, "autocasion":AutocasionExtractor}`. **Cero dimension pais** en la clave.
- **Extractor Protocol** `pipeline/recipe_harness.py:65-74` [VERIFIED]: superficie minima = atributo `source:str` + `recipe_template(dealer_ref)->Recipe` + `sample(dealer_ref,k)->Sample`. Es lo UNICO que un source nuevo implementa; el harness (`RecipeHarness.run` :150-194) es source-agnostico.
- **Lookup por recipe.source** `recipe_harness.py:245` [VERIFIED] `if recipe.source not in EXTRACTORS` y `:248 EXTRACTORS[recipe.source]().sample(...)`; idem CLI `_main` :267 `if source not in EXTRACTORS` y :273 `EXTRACTORS[source]()`. La resolucion es por **string desnudo**, jamas por (pais, source).
- **Doctrina reuse-not-2nd-scraper** [VERIFIED]: docstring de modulo `recipe_extractors.py:3-6` ("an extractor is glue, not a second scraper"). Cada `sample()` REUSA la parse fn ya verificada: `as24.parse_listing_vehicle` (:87-88), `ccom.parse_card_vehicle` (:151-152), `ccn.parse_item_vehicle` (:210-211), `ac.parse_ad` (:274).
- **Identidad portadora** `recipe_extractors.py:30-34` [VERIFIED]: `_valid(v)` = `bool(v.vin_ref) and bool(v.deep_link)` — el par dedup/delta. Variantes per-source `_ccom_valid` :95-98, `_ccn_valid` :157-159, `_ac_valid` :216-218 (todas `listing_ref + deep_link`).
- **GenericWebExtractor** cumple el MISMO Protocol `recipe_extract_web.py:117,120,125,139` [VERIFIED] (`source="web_generic"`, `recipe_template`, `sample`).
- **recipe.kind** como tipo-de-superficie `recipe_schema.py:101` [VERIFIED] (`kind="compraventa"` default); fijado por extractor: `compraventa` (as24 :46) / `plataforma` (ccom :115, ccn :174, ac :234).

#### (b) Mecanismo al atomo
El harness instancia `EXTRACTORS[source]()`, llama `recipe_template()` para el DRAFT (transport/pagination/parsing pre-llenos, evidence vacia) y `sample(dealer_ref,k)` para los k coches acotados. `decide_status` (`recipe_harness.py:94-117`) sella; `write_recipe` persiste; `sample.parsed.clear()` borra. El **unico acoplamiento** entre harness y fuente es la clave-string del dict y los dos metodos del Protocol. El par identidad (`deep_link`,`vin_ref`/`listing_ref`) se exige en `sample()` via `_valid` — es el invariante portador que dedup/delta (02-scrape/ingest) usan como llave.

#### (c) Costura ES->generico + fix exacto
**Costura:** `EXTRACTORS` es un **dict-modulo global SIN eje pais** (`recipe_extractors.py:280`). El nombre `"coches_com"` ≡ ES implicitamente; el modulo `import`a en cabecera los 4 conectores ES (`autocasion_wholesale`, `coches_com_wholesale`, `coches_net_wholesale`, `autoscout24` :22-27). **Registrar un source extranjero EXIGE editar este modulo** (nuevo import + nueva entrada global) — viola "registro declarativo, jamas edicion del arnes".

**Fix:**
1. Sustituir el global por un **`ExtractorRegistry` keyed por `(country_code, source)`** (o un registry-objeto por country-pack cargado de `countries/<CC>/extractors/`). Decorador `@register(country, source)` para auto-registro en import, sin tocar `recipe_extractors.py`.
2. `RecipeRunner.replay` (`recipe_harness.py:245`) y `_main` (:267) resuelven por **`(country_of_cdp(recipe.cdp_code), recipe.source)`** — reusa `paths.country_of_cdp` — no por `recipe.source` desnudo.
3. **Protocol intacto** (`recipe_harness.py:65-74`): ya es country-agnostico; solo cambia el keying del registro.
4. Codificar la identidad como metodo requerido del Protocol `identity(v)->bool` (hoy `_valid` libre per-source) para que CADA extractor nuevo declare su par portador (deep_link+source_ref) explicitamente.

#### (d) Riesgo adversarial concreto
- **Homonimo DE/IT/FR (CRITICAL):** `autoscout24` existe en ES/DE/IT/FR/NL... todos comparten el nombre `"autoscout24"` -> una receta DE y una ES mapean al MISMO `EXTRACTORS["autoscout24"]` = el conector ES con `base_url`/`url_template` ES (`/profesionales/` :55). El dealer DE se scrapea contra la superficie ES; colision silenciosa.
- **Mismo-source-distinto-TLD:** una plataforma pan-EU (AutoScout24, mobile.de) bajo `.de` vs `.es` exige dos registros; el dict de nombre-desnudo no puede sostener ambos.
- **2o scraper (drift):** un extractor de pais nuevo que NO reuse la parse fn verificada (escribe su propio parse) se vuelve el "2o scraper" prohibido; diverge del drain vivo y el harness (solo cuenta quorum, [faceta 8](#faceta-8)) no lo detecta.
- **Ruido/overwrite:** un source registrado dos veces (typo, re-import) sobreescribe la entrada del dict (last-write-wins) sin guard.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** (1) registry keyed por `(CC,source)` y `country_of_cdp(cdp)` round-trip al pais registrado; (2) registrar un source foraneo toca CERO lineas de `recipe_harness`/`recipe_extractors` (solo el pack); (3) cada extractor pasa el contrato de identidad (su `sample` emite deep_link+source_ref sobre fixture); (4) guard COUNTRY-PROOF: dos paises con source homonimo resuelven a extractores DISTINTOS.
- **Multi-via:** (via1) unit test de resolucion del registry per-(CC,source); (via2) replay en proceso limpio desde una receta de pack foraneo reproduce SIN el modulo ES en el path; (via3) test adversarial de colision inyectando un homonimo prueba que no hay overwrite silencioso (fail-closed).

#### (f) Herramienta NEXT-LEVEL que la eleva
**executable-field-map-interpreter · parsel** (BSD-3-Clause, https://github.com/scrapy/parsel) [VERIFIED NEXT-LEVEL.md:261-267]. La elevacion mas profunda del registro es **disolver el Python por-fuente**: parsel (+`jsonpath-ng`+`selectolax`) convierte `field_map` en un mini-DSL interpretado desde el YAML, de modo que un source nuevo sobre engine conocido es **100% pack YAML, sin una sola entrada de Python nueva en `EXTRACTORS`** — solo una receta declarativa. Hoy solo **5/42 conectores** implementan el Protocol Extractor (NEXT-LEVEL.md:263 [VERIFIED]); el interprete cierra esa brecha. **Complemento:** Crawl4AI `JsonCssExtractionStrategy.generate_schema` (Apache-2.0, https://github.com/unclecode/crawl4ai) [VERIFIED NEXT-LEVEL.md:237-243] auto-sintetiza el field_map de un source nuevo en 1 disparo, asi registrar la cola-larga de un pais es generacion-una-vez + replay determinista, jamas Python a mano.

#### Resolución condensada — Faceta 3
- **Costura** · EXTRACTORS es un dict-modulo global keyed por nombre-desnudo de source SIN eje pais (recipe_extractors.py:280-286); el modulo importa en cabecera los 4 conectores ES (:22-27). Registrar un source extranjero exige EDITAR el arnes (nuevo import + nueva entrada), violando 'registro declarativo'. La resolucion replay/_main es por recipe.source desnudo (recipe_harness.py:245,248,267,273), no por (pais,source).
- **Fix** · Sustituir el global por ExtractorRegistry keyed por (country_code, source) con decorador @register(country,source) para auto-registro en import (cero edicion del arnes). replay (recipe_harness.py:245) y _main (:267) resuelven por (country_of_cdp(recipe.cdp_code), recipe.source). Protocol intacto (:65-74, ya country-agnostico). Codificar la identidad portadora como metodo requerido identity(v)->bool del Protocol (hoy _valid libre, recipe_extractors.py:30-34) para que cada extractor declare su par deep_link+source_ref.
- **Adversarial** · CRITICAL homonimo: autoscout24 ES/DE/IT/FR comparten clave 'autoscout24' -> receta DE mapea al conector ES con url_template '/profesionales/' ES (recipe_extractors.py:55), colision silenciosa. Mismo-source-distinto-TLD (.de vs .es) no cabe en el dict de nombre-desnudo. Un extractor que NO reuse la parse fn verificada = '2o scraper' prohibido, diverge del drain y el harness (solo cuenta, [faceta 8](#faceta-8)) no lo ve. Re-registro por typo = overwrite last-write-wins sin guard.
- **Sellado (multi-vía)** · Sello: (1) registry keyed por (CC,source), country_of_cdp round-trip; (2) registrar source foraneo toca CERO lineas de recipe_harness/recipe_extractors; (3) cada extractor pasa contrato de identidad (sample emite deep_link+source_ref sobre fixture); (4) guard COUNTRY-PROOF: dos paises homonimos resuelven a extractores distintos. Multi-via: unit test resolucion per-(CC,source) | replay en proceso limpio desde pack foraneo sin el modulo ES en path | test adversarial de colision (fail-closed, no overwrite silencioso).
- **Herramienta NEXT-LEVEL (€0)** · executable-field-map-interpreter · parsel (BSD-3-Clause, https://github.com/scrapy/parsel) [VERIFIED NEXT-LEVEL.md:261-267] — disuelve el Python por-fuente: field_map interpretado desde YAML (parsel+jsonpath-ng+selectolax), source nuevo = 100% pack YAML, cero entrada Python en EXTRACTORS (hoy solo 5/42 conectores implementan el Protocol, NEXT-LEVEL.md:263). Complemento: Crawl4AI generate_schema (Apache-2.0, https://github.com/unclecode/crawl4ai) [VERIFIED NEXT-LEVEL.md:237-243] auto-sintetiza el field_map de un source nuevo en 1 disparo.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-4"></a>

### Faceta 4 — Familia de selector estructurado Tier-0 (`next_data` / `json_api`)

> **F10 · rung coste-0 estructurado** (`next_data`/`json_api`). `field_map` en prosa re-ejecuta Python por fuente. **Cross-ref:** facetas [2](#faceta-2)·[9](#faceta-9)·[11](#faceta-11)·[18](#faceta-18)·[19](#faceta-19).

#### (a) Verificacion de code_hints [VERIFIED]
- **AS24 next_data** — `pipeline/recipe_extractors.py:37-92` [VERIFIED]: `AutoScout24Extractor.source="autoscout24"`; `recipe_template` declara `Parsing(engine="next_data", container_path="listings", field_map={...})` (`:59-73`), `Pagination(declared_path="numberOfResults", strategy="page_param")` (`:53-58`). El `field_map` es **PROSA**, no path: `"deep_link": "host + listing.url"`, `"year": "listing.firstRegistrationDate|tracking.firstRegistration -> YYYY"`, `"price": "listing.prices.public.priceRaw|tracking.price"`, `"photo_url": "listing.images[0]"` (`:62-73`).
- **coches.com next_data** — `recipe_extractors.py:101-154` [VERIFIED]: `engine="next_data"` (`:126`), `container_path="props.pageProps.classifieds.classifiedList"` (`:127`), `declared_path="props.pageProps.classifieds.total"` (`:123`), `_SAMPLE_URL = ccom._SRP_ALL` (`:111`). `field_map` con `"deep_link": "canonical_deep_link(visibleId)"` (`:129`) — una **llamada a funcion Python**, no un path declarativo.
- **coches.net json_api POST** — `recipe_extractors.py:162-213` [VERIFIED]: `engine="json_api"` (`:185`), `strategy="json_post_page"` (`:179`), `declared_path="meta.totalResults"` (`:182`), `container_path="items"` (`:186`). `field_map` con `"transmission": "transmissionTypeId->map"` (`:196`) — referencia a un dict ES interno (`coches_net_wholesale._TRANSMISSION={1:'Manual',2:'Automático'}`, `:130` [VERIFIED]).
- **parse real reusado** — `pipeline/sources/autoscout24.py:172-218 parse_listing_vehicle` [VERIFIED]: extrae `make=v.get("make")` (`:210`), bound km `km>5_000_000` inline (`:179`), year `1900<=year<=2100` inline (`:189`), `fuel=_raw(v.get("fuelCategory")) or v.get("fuel")` (`:215`).
- **enum abierto** — `pipeline/recipe_schema.py:67` [VERIFIED]: `engine: str = "next_data"  # next_data | jsonld | css | llm_local`. **`json_api` NI SIQUIERA aparece en el comentario-vocabulario**: el engine de coches.net es un string libre fuera del enum nominal. El `sample()` re-corre Python por fuente (`recipe_extractors.py:80-92`, `:143-154`, `:204-213`), no interpreta el `field_map`.

#### (b) Mecanismo al atomo
El rung coste-0 estructurado materializa `make/model/year/km/price/fuel/transmission/photo` desde **estructura JSON embebida** (`__NEXT_DATA__` SSR en AS24/coches.com; gateway JSON POST en coches.net), nunca adivinando del titulo. Atomos por fuente: (1) **localizar el contenedor** (`_find_listings` recursivo en AS24 `autoscout24.py:108-121`; `extract_classifieds_any` en coches.com; `data["items"]` en coches.net); (2) **leer el oraculo declared** (`numberOfResults` / `classifieds.total` / `meta.totalResults`) — el tercer camino del quorum VAM; (3) **proyectar k cards** a `Vehicle` via la parse fn ya verificada; (4) **full_dealer gate**: `declared is not None and declared <= fetched` (`:91,:153,:212`) — solo entonces `declared` entra al quorum (un subset deliberado refutaria en falso). El engine estructurado **JAMAS toca la capa-2 IA** porque ya trae `make/model` limpios de la estructura.

#### (c) Costura ES->generico
El `field_map` es **prosa descriptiva** (`"host + listing.url"`, `"firstRegistration -> YYYY"`, `"transmissionTypeId->map"`) interpretada por el Python de cada extractor, no un path ejecutable. Por eso `recipe.sample()` **re-ejecuta codigo** (`as24._find_listings`, `ccom.parse_card_vehicle`, `ccn.parse_item_vehicle`) en vez de INTERPRETAR el YAML. Consecuencia: una fuente extranjera sobre un engine conocido (p.ej. `autoscout24.de` `__NEXT_DATA__`) **exige Python nuevo** para reproducir el sample, rompiendo la tesis "receta = asset autosuficiente". La costura: cerrar `Parsing.engine` a `{next_data, json_api}` ejecutables que implementen `locate(bytes, container_path, field_map) -> list[dict]` interpretando paths JSON deterministas (`props.pageProps.classifieds.classifiedList[*].make.name`), con paridad golden byte-identica contra los 3 parsers actuales antes de cortar.

#### (d) Riesgo adversarial concreto
- **DE (AS24.de)**: `fuelCategory='Benzin'`, `transmissionType='Automatik'`, `firstRegistrationDate` con formato/locale distinto -> el `field_map` ES lee la llave correcta pero el **valor entra crudo no-canonico** (Benzin != Gasolina); la estructura se parsea pero el dato sale sin traducir (hereda a [facetas 18/19](#faceta-18)).
- **coches.net id-no-visto**: `transmissionTypeId` 3/4 nuevo -> `_TRANSMISSION.get(id)` cae a `None` **silencioso** (`coches_net_wholesale.py:130,274`).
- **next_data drift / Imperva**: coches.com devuelve interstitial -> `extract_classifieds_any` vacio -> `Sample(declared=None, fetched=0, parsed=[])` (`recipe_extractors.py:145-146`); honesto pero el declared se pierde.
- **declared inexistente** en una fuente nueva -> el VAM pierde su tercer camino (`full_dealer` nunca arma quorum).

#### (e) Criterio de sellado + verificacion multi-via
- **Sello**: (1) **paridad golden byte-identica** — el `field_map` interpretado produce EXACTAMENTE el mismo `Vehicle` que el Python actual sobre los 3 fixtures ES (cero regresion en 2.3M); (2) `declared` poblado y `full_dealer` correcto cuando el k-slice cubre el inventario; (3) `parse_loss == 0` para los k cards validos.
- **Multi-via**: (i) **test** = fixture `__NEXT_DATA__`/JSON capturado -> Vehicle esperado; (ii) **adversarial** = un `field_map` con path inexistente FALLA al CARGAR (validacion de DSL), no al ejecutar; (iii) **via independiente** = `RecipeRunner.replay` en proceso limpio interpreta el YAML y reproduce el sample SIN importar el modulo Python de la fuente (prueba la autosuficiencia que hoy el diseno solo afirma).

#### (f) Herramienta NEXT-LEVEL
**parsel** (`executable-field-map-interpreter`) convierte el `field_map` de prosa a mini-DSL CERRADO interpretado puramente desde YAML: CSS/XPath + **JMESPath para JSON** + regex; junto a **jsonpath-ng** (JSONPath sobre `next_data`/`json_api`) y **selectolax** (Lexbor ~25x BeautifulSoup). Cada valor del enum (`next_data`,`json_api`,`jsonld`,`microdata`,`css`,`regex_hydrate`) mapea a un `Selector.locate(bytes, container_path, field_map)`. parsel es el nucleo de Scrapy (battle-tested). Adyacente: **extruct** (`deterministic-structured-extraction-upgrade`) sube el recall del rung structured. [VERIFIED NEXT-LEVEL.md:261-267, :285-291]

#### Resolución condensada — Faceta 4
- **Costura** · field_map es PROSA ('host + listing.url', 'firstRegistration -> YYYY', 'transmissionTypeId->map', 'canonical_deep_link(visibleId)') interpretada por Python por-fuente; sample() re-corre codigo (recipe_extractors.py:80-92/143-154/204-213) en vez de interpretar el YAML. Parsing.engine es string libre (recipe_schema.py:67) y 'json_api' ni figura en el comentario-vocabulario -> una fuente extranjera sobre engine conocido exige Python nuevo, rompiendo 'receta=asset autosuficiente'.
- **Fix** · Cerrar Parsing.engine a enum ejecutable {next_data,json_api,...} con Protocol locate(bytes,container_path,field_map)->list[dict]; reescribir el field_map de los 3 extractores estructurados (AS24/coches.com/coches.net) como path-expressions JSON deterministas interpretadas por parsel(JMESPath)+jsonpath-ng; validar el DSL al CARGAR la receta (path inexistente = error de carga); exigir paridad golden byte-identica contra parse_listing_vehicle/parse_card_vehicle/parse_item_vehicle antes de retirar el Python.
- **Adversarial** · DE: AS24.de fuelCategory='Benzin'/transmissionType='Automatik' -> field_map lee la llave pero el valor entra crudo no-canonico. coches.net transmissionTypeId 3/4 -> _TRANSMISSION.get cae a None silencioso (coches_net_wholesale.py:130). next_data drift/Imperva -> sample vacio honesto pero declared perdido. Fuente nueva sin declared_path -> VAM sin tercer camino del quorum.
- **Sellado (multi-vía)** · Sello: paridad golden byte-identica field_map-interpretado vs Python actual sobre los 3 fixtures ES (cero regresion 2.3M) + declared poblado + full_dealer correcto + parse_loss==0. Multi-via: (1) test fixture next_data/JSON->Vehicle esperado; (2) adversarial: field_map con path inexistente FALLA al cargar no al ejecutar; (3) via independiente: RecipeRunner.replay en proceso limpio interpreta YAML y reproduce sample sin el modulo Python de la fuente.
- **Herramienta NEXT-LEVEL (€0)** · parsel (executable-field-map-interpreter) — BSD-3-Clause, EUR0 — https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:264]. Companeros: jsonpath-ng (JSONPath next_data/json_api), selectolax (Lexbor ~25x). Adyacente: extruct (deterministic-structured-extraction-upgrade) BSD-3-Clause https://github.com/scrapinghub/extruct [VERIFIED :288].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-5"></a>

### Faceta 5 — Familia enumerate-then-hydrate (autocasion SSR-ref + GraphQL ad)

> **F10 · 2-fase enumerate-then-hydrate** (SSR-ref + GraphQL). engine open-vocab fuera del enum; `declared=None` deja al VAM sin 3er camino. **Cross-ref:** facetas [2](#faceta-2)·[3](#faceta-3)·[16](#faceta-16)·[8](#faceta-8).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/recipe_extractors.py:221-258` [VERIFIED] `AutocasionExtractor.recipe_template`: `source="autocasion"` (:230), `kind="plataforma"` (:234). La paginacion declara `strategy="ssr_enumerate_then_gql_hydrate"` (:239), `declared_path="ssr id-set stops changing"` (:242, **NO numerico**) y `stop="id_set_stable"` (:243). El parsing declara `engine="ssr_ref_re + graphql_ad"` (:245, **open-vocab, encaja en CERO enum**), `container_path="data.ad"` (:246) y un `field_map` en prosa-path (:247-257): `"deep_link":"_PDP_BASE + url"`, `"make":"brand.name"`, `"model":"family.name"`, `"fuel":"fuel.name"`, `"transmission":"transmission.name"`.
- `pipeline/recipe_extractors.py:260-277` [VERIFIED] `sample()`: 2 fases reales — (1) `fetcher.fetch(ac.SSR_RESULTS, method="GET")` (:264) -> `ac.parse_ssr_refs(html)[:k]` (:265), `fetched=len(refs)` (:266); (2) loop hidratante (:268-276): por cada `(url, ad_id)` hace `fetcher.fetch(ac.GQL_ENDPOINT, method="POST", gql={"query": ac._AD_QUERY % int(ad_id)})` (:269-270), `ad = (json.loads(raw).get("data") or {}).get("ad")` (:271); si `not ad: continue` (:272-273, **perdida**); si no, `v = ac.parse_ad(ad, url)` (:274) y `if _ac_valid(v): parsed.append(asdict(v))` (:275-276). Retorna `Sample(declared=None, fetched=fetched, parsed=parsed, full_dealer=False)` (:277).
- `pipeline/recipe_extractors.py:216-218` [VERIFIED] `_ac_valid(v) = bool(v.listing_ref) and bool(v.deep_link)` — la identidad portadora (par dedup/delta) son los dos campos.
- `pipeline/recipe_extractors.py:280-286` [VERIFIED] `EXTRACTORS` dict-modulo global, `"autocasion": AutocasionExtractor` (:285), keyed por string `source`.
- `pipeline/platform/autocasion_wholesale.py:218-229` [VERIFIED] `parse_ssr_refs(html)` extrae pares `(pdp_url, ad_id)` de UNA pagina SSR, de-dup por `rid` en orden (:224-228); docstring: "Pages past the last clamp to the final page, so the CALLER stops when the id-set stops changing (id-dedup across pages, not page position)" — confirma que el oraculo de parada es el id-set, NO un contador.
- `pipeline/platform/autocasion_wholesale.py:232-269` [VERIFIED] `parse_ad(ad, pdp_url)`: `sanitize_price` en :241, **bounds inline divergentes** `1900 <= year <= 2100` (:244) y `km > 5_000_000` (:247) — el parse emite su propia fisica, NO delega en `sanitize_km` (KM_MAX=1.5M) ni `sanitize_year`; `transmission=(ad.get("transmission") or {}).get("name")` (:267), `fuel=(ad.get("fuel") or {}).get("name")` (:266).

#### (b) El mecanismo al atomo
Es el unico extractor de DOS llamadas-red por item. Fase-A: una pagina SSR de resultados es una lista de `-ref{id}` anchors -> `parse_ssr_refs` los des-duplica conservando orden y devuelve `[:k]`. `fetched` = numero de refs tomados (NO de ads hidratados). Fase-B: cada `ad_id` se inyecta como `int` en `_AD_QUERY % int(ad_id)` (defensa anti-inyeccion via cast int) y se POSTea al `GQL_ENDPOINT`; la respuesta se desenvuelve `data.ad`. Tres bifurcaciones del item: (1) `not ad` -> `continue` (la red/GQL no devolvio el ad: cuenta como perdida porque `fetched` ya lo conto); (2) `ad` valido pero `parse_ad` produce un `Vehicle` sin `listing_ref`/`deep_link` -> `_ac_valid` False -> descartado (tambien perdida); (3) ok -> `asdict(v)` a `parsed`. Como `fetched=len(refs)` y `parsed` solo suma los exitosos, **cualquier ad no-hidratado o no-valido eleva `parse_loss=fetched-parsed>0`**, y `decide_status` ([faceta 7](#faceta-7)) sella FAILED en `loss!=0` — perdida honesta por construccion. `declared=None` y `full_dealer=False`: este engine NO aporta el tercer camino (declared) al quorum VAM; su veredicto se apoya solo en el par cross-family `fetched` (HTTP) vs `parsed` (DB).

#### (c) Costura ES->generico
1. **El engine no encaja en el enum cerrado** que la [faceta 2](#faceta-2) quiere imponer: `"ssr_ref_re + graphql_ad"` es texto libre. La 2-fase (enumerate-then-hydrate) es un patron GENERICO, pero hoy su musculo (`parse_ssr_refs`, `parse_ad`, `_AD_QUERY`, `SSR_RESULTS`, `_PDP_BASE`, `_IMPERSONATE`) vive en Python por-fuente; una fuente extranjera sobre el mismo patron EXIGE Python nuevo -> viola "pais nuevo = solo YAML".
2. **El oraculo `declared` es no-numerico** (`"ssr id-set stops changing"`): el VAM nunca recibe un contador por esta familia; el sello pierde su tercer camino justo donde un pais nuevo de fuente delgada mas lo necesita.
3. **Bounds inline ES-divergentes** (`year<=2100`, `km>5M`) contradicen el gate canonico (1.5M / now+1) — la [faceta 16](#faceta-16) reaparece aqui: `parse_ad` debe emitir crudo y DELEGAR en `normalize_vehicle`.
4. **`EXTRACTORS` es un dict global** keyed por string `source`: dos paises con una fuente homonima (o el mismo source con TLD distinto) colisionan (costura compartida con [faceta 3](#faceta-3)).

#### (d) Riesgo adversarial concreto
- **DE/FR/no-UE con cursor o sin GraphQL**: una fuente que pagina por cursor/sitemap o que no expone un `ad(adId)` GraphQL no encaja en `ssr_enumerate_then_gql_hydrate`; sin `declared` numerico el VAM no puede cruzar `full_dealer` y el sellado se queda con 2 caminos same-cross-family (UNVERIFIED, no TRUSTWORTHY).
- **Fragilidad de hidratacion**: un 429/500 transitorio del GQL hace `not ad -> continue`, inflando `parse_loss` y marcando FAILED una receta que es estructuralmente correcta. Hoy NO se distingue "ad realmente ausente" de "rate-limit transitorio" — ambos caen en el mismo `continue`. A escala multipais esto convierte ruido de red en falsos FAILED.
- **IT/PT labels crudos**: `parse_ad` emite `fuel.name`/`transmission.name` verbatim ([faceta 18/19](#faceta-18)); un autocasion-equivalente IT entregaria 'Benzina'/'Automatico' sin canonicalizar.

#### (e) Criterio de sellado + verificacion multi-via
- **Golden byte-identico**: la 2-fase reescrita como Selector interpretado debe reproducir EXACTAMENTE el `asdict(parse_ad(...))` actual sobre un fixture capturado (SSR html + respuesta GQL json), sin red.
- **Via 1 (unit offline)**: fixture SSR+GQL -> `parsed==k`, `loss==0`.
- **Via 2 (replay en proceso limpio)**: `RecipeRunner.replay` ([faceta 9](#faceta-9)) interpreta el YAML y reproduce el sample sin importar el modulo Python.
- **Via 3 (perdida honesta)**: fixture con 1 ad que no hidrata -> FAILED con la razon exacta `parse loss ... (lost N)`.
- **Via 4 (sellado de robustez, HUECO a cerrar)**: un fixture de error transitorio GQL (429) debe ser DISTINGUIBLE de un parse_loss real (reintento acotado o marca 'transport-degraded', no FAILED silencioso).

#### (f) Herramienta NEXT-LEVEL
`executable-field-map-interpreter` -> **parsel** (BSD-3-Clause) [VERIFIED NEXT-LEVEL.md:261-267] https://github.com/scrapy/parsel — el nucleo de Scrapy (CSS+XPath+JMESPath+regex). Permite expresar la Fase-A (`-ref{id}` regex enumerate) y la Fase-B (JMESPath/jsonpath sobre `data.ad`) como field_map INTERPRETADO desde el YAML, de modo que un `enumerate-then-hydrate` extranjero sea pack-puro, cero Python. Complementos verificados en la misma entrada: **jsonpath-ng** para los paths del payload GQL y **selectolax** (Lexbor, ~25x BeautifulSoup) para HTML. Es la corona de esta faceta porque hoy el parse vive en Python (`recipe_harness.py:228-231` declara el interprete NO reclamado).

#### Resolución condensada — Faceta 5
- **Costura** · engine='ssr_ref_re + graphql_ad' (recipe_extractors.py:245) es open-vocab y no encaja en el enum cerrado; el musculo 2-fase (parse_ssr_refs/parse_ad/_AD_QUERY) vive en Python por-fuente -> una fuente extranjera del mismo patron exige Python nuevo; declared=None + full_dealer=False (recipe_extractors.py:277) deja al VAM sin tercer camino; bounds inline year<=2100/km>5M (autocasion_wholesale.py:244,247) contradicen el gate canonico 1.5M; EXTRACTORS global keyed por string (recipe_extractors.py:280-286) colisiona entre paises.
- **Fix** · Modelar la 2-fase como una clase Selector en el enum cerrado que implemente locate(bytes,container_path,field_map)->list[dict] sobre parsel+jsonpath-ng (Fase-A regex enumerate, Fase-B JMESPath sobre data.ad); convertir field_map de prosa a path-DSL interpretable; mover SSR_RESULTS/_PDP_BASE/_AD_QUERY a datos de receta (ya lo son), y registrar EXTRACTORS por-pais inyectable ([faceta 3](#faceta-3)). parse_ad emite crudo y delega year/km en normalize_vehicle ([faceta 16](#faceta-16)). Anadir reintento acotado/marca transport-degraded para distinguir 429-GQL de parse_loss real. Cierre con paridad golden byte-identica antes de retirar el Python.
- **Adversarial** · Fuente DE/FR/no-UE con paginacion cursor/sitemap o sin GraphQL no encaja en ssr_enumerate_then_gql_hydrate; declared no-numerico deja al VAM sin oraculo (UNVERIFIED en vez de TRUSTWORTHY) justo donde el pais nuevo de fuente delgada lo necesita. Un 429/500 transitorio del GQL (not ad -> continue) infla parse_loss y marca FAILED una receta correcta, convirtiendo ruido de red en falsos FAILED a escala. fuel.name/transmission.name verbatim (IT 'Benzina'/'Automatico') entran sin canonicalizar.
- **Sellado (multi-vía)** · Golden byte-identico del asdict(parse_ad) sobre fixture SSR+GQL capturado (sin red). Via1 unit offline parsed==k loss==0; Via2 replay en proceso limpio interpreta YAML sin el modulo Python; Via3 fixture con ad no-hidratado -> FAILED con razon 'parse loss (lost N)'; Via4 (hueco a cerrar) fixture 429-GQL debe ser distinguible de parse_loss real (reintento acotado o marca transport-degraded, nunca FAILED silencioso).
- **Herramienta NEXT-LEVEL (€0)** · executable-field-map-interpreter -> parsel (BSD-3-Clause) https://github.com/scrapy/parsel [VERIFIED NEXT-LEVEL.md:264] + jsonpath-ng (paths GQL data.ad) + selectolax (Lexbor HTML); expresa la 2-fase como field_map interpretado desde YAML -> enumerate-then-hydrate extranjero pack-puro, cero Python. Corona de la faceta: hoy el interprete esta NO reclamado (recipe_harness.py:228-231).

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-6"></a>

### Faceta 6 — Rung web genérico de concesionario (JSON-LD/microdata) + descubrimiento de stock

> **F6 · LÉXICON español incrustado** (stock/count/marketplace ES) + money roto (`'24.900'`→24.9, `priceCurrency` descartado). B10·B12(parte). **Cross-ref:** facetas [14](#faceta-14)·[12](#faceta-12)·[26](#faceta-26).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/recipe_extract_web.py:27` [VERIFIED] `_VEHICLE_TYPES = ("Car","Vehicle","MotorizedVehicle","Motorcycle","Product")` — el conjunto de @type schema.org que cuenta como vehiculo.
- `:28-30` [VERIFIED] `_STOCK_HINT` es un regex con **lexico ES incrustado**: `coches|vehiculos|veh%C3|stock|ocasion|inventario|segunda-mano|nuestros-coches|vehiculos-ocasion|km0|kilometro-0`. Cero terminos no-ES.
- `:32` [VERIFIED] `_COUNT_HINT = re.compile(r'(\d{1,5})\s*(?:veh[ií]culos|coches)\b', re.I)` — el oraculo `declared` se mina del **texto ES** "N vehiculos/coches".
- `:33-34` [VERIFIED] `_MARKETPLACES = ("paginasamarillas","facebook","instagram","twitter","youtube","wallapop","coches.net","autoscout","milanuncios")` — blocklist con marketplaces **ES** (coches.net, milanuncios, wallapop).
- `:37-50` [VERIFIED] `find_stock_url(home_html, base)` itera `_STOCK_HINT.findall`, descarta hrefs que contienen un marketplace, resuelve relativo/absoluto y devuelve el primero (o `None`).
- `:53-87` [VERIFIED] `vehicles_from_jsonld`: DFS sobre cada bloque `application/ld+json`; nodo cuenta como vehiculo sii `@type ∈ _VEHICLE_TYPES` **Y** `node.get("name")`. En `:76-81` solo extrae `offers.get("price")` — el `priceCurrency` del JSON-LD **se descarta** (no se lee). `:82-83` emite `{name, price, url, type}`.
- `:90-92` [VERIFIED] `_MICRO_ITEM` regex de microdata por `itemtype` Car|Vehicle|Product|MotorizedVehicle.
- `:95-109` [VERIFIED] `vehicles_from_microdata`: `:104` `re.search(r'itemprop="price"[^>]*(?:content="([^"]+)"|>\s*([\d.,]+))', block)`, `:105` `price = (pm.group(1) or pm.group(2))` — el precio se captura como **string crudo** (p.ej. `"24.900"`) **sin parser de locale**; cuando aguas abajo `sanitize_price`→`float("24.900")` da **24.9** (perdida 1000x latente).
- `:112-114` [VERIFIED] `_valid(v)` = `bool(name) and (price is not None or bool(url))` — el piso de validez es solo nombre + (precio O url); **no exige make/model/year/km/fuel/currency**.
- `:117-165` [VERIFIED] `GenericWebExtractor` (`source="web_generic"`): `recipe_template` `:133` fija `declared_path="page text: N vehículos"` (ES) y `:134` `engine` default `"jsonld"`; `sample` `:158-159` deriva `declared` de `_COUNT_HINT`; `:164` `full_dealer = declared is not None and declared <= len(sliced)`.

Conclusion: el rung "universal" es de facto **ES-acoplado en 4 puntos** (stock-hints, count-words, marketplace-blocklist, declared-text) y **money-roto** (microdata sin parse, currency descartada).

#### (b) El mecanismo al atomo
1. `fetch_text(dealer_ref, tier=0)` baja el HOME por el motor antideteccion compartido.
2. `find_stock_url` busca el ancla de inventario con `_STOCK_HINT`; si ninguna casa → `None` → se cae al propio home como pagina de stock (`pages=[stock_url, dealer_ref]`, `:144`).
3. Por cada pagina: `vehicles_from_jsonld`; si vacio, `vehicles_from_microdata` (`engine="microdata"`). Primer hit no vacio gana y rompe (`:156-160`).
4. `declared` se mina del mismo HTML con `_COUNT_HINT`.
5. `sliced = vehicles[:k]`; `parsed = [v for v in sliced if _valid(v)]`; `full_dealer` solo si `declared<=len(sliced)`.
6. Web sin JSON-LD ni microdata → `vehicles=[]` → `Sample(parsed=[])` → el arnes sella **FAILED-con-razon honesto** (no falso exito). Ese es el contrato correcto del peldano €0.

#### (c) La costura ES→generico + fix exacto
La costura es un objeto `LocaleProfile` ([faceta 13](#faceta-13)) inyectado al extractor:
- `_STOCK_HINT` → `pack.stock_hints` (lista de tokens del pais: ES `coches|ocasion`, FR `occasion|vehicules|voitures`, DE `Fahrzeuge|Gebrauchtwagen|Fahrzeugbestand`, IT `usato|veicoli`, PT `usados|viaturas`). El regex se **compila desde el pack**, no se hardcodea.
- `_COUNT_HINT` → `pack.count_words` (ES `vehiculos|coches`, DE `Fahrzeuge`, FR `vehicules`, ...).
- `_MARKETPLACES` → `pack.marketplace_blocklist` (los portales locales del pais: ES coches.net/milanuncios; FR lacentrale.fr/leboncoin; DE mobile.de/autoscout24.de; IT subito.it; PT standvirtual.pt).
- **Fix money (CRITICAL latente):** enrutar TODO precio de microdata/JSON-LD por `parse_money(text, pack)` ([faceta 14](#faceta-14)) y **capturar `priceCurrency`** del JSON-LD en `:79` hacia `CanonicalVehicle.currency` ([faceta 12](#faceta-12)). Hoy `:79` lo descarta y `:104-105` entrega string crudo: `float("24.900")=24.9` ya sirve precios mal **en ES** — dano a auditar antes de declarar ES sellado.
- **Fix recall:** sustituir `vehicles_from_jsonld`/`vehicles_from_microdata` (regex a mano) por un motor multi-sintaxis (extruct) que ademas cubra RDFa/OpenGraph/Microformats — superficie €0 que el codigo a mano no alcanza.

#### (d) Riesgo adversarial concreto
- **FR/DE:** un dealer FR (`occasion`/`vehicules`/`voitures`) o DE (`Fahrzeuge`/`Gebrauchtwagen`) **no matchea NINGUN** `_STOCK_HINT` ES → `find_stock_url=None` → solo se mira el home → si el inventario vive en `/occasion/` el sample sale **vacio** → FAILED: el rung "universal" no encuentra ni el inventario.
- **Blocklist:** `_MARKETPLACES` ES no filtra `mobile.de`/`leboncoin.fr`/`subito.it` → un ancla a un marketplace local del pais se toma por "stock propio" del dealer y contamina el sample.
- **Money 1000x:** microdata IT/DE con `content="24.900"` (24.900 EUR, miles europeos) → sin parse_money → `24.9`; o MX `"1,234.56"` bajo el (futuro) parse EU → ~1000x. La columna `price` queda corrupta y **pasa `sanitize_price`** (sigue siendo float valido).
- **Currency-blind:** JSON-LD JP con `priceCurrency:"JPY"` y `price:3000000` → se guarda `3000000` desnudo, indistinguible de 3M EUR.
- **Ruido:** una pagina de error estilizada con OpenGraph rancio (extruct la leeria) podria producir un "vehiculo" falso si `_valid` solo exige name+price/url → necesita el contrato de fill-rate ([faceta 26](#faceta-26)) para no FALSE-VERIFIED.

#### (e) Criterio de sellado + verificacion multi-via
- **Sellado:** el rung se considera generico cuando (1) `stock_hints`/`count_words`/`marketplace_blocklist` provienen del pack inyectado (cero literal ES en el modulo), (2) todo precio pasa por `parse_money` + `currency` capturada, (3) ES queda **byte-identico** (golden).
- **Via 1 (golden ES):** los fixtures HTML/JSON-LD/microdata ES existentes producen exactamente el mismo `Sample` que hoy (cero regresion sobre 2.3M).
- **Via 2 (adversarial multipais):** fixtures FR/DE/IT con su lexico → `find_stock_url` localiza el inventario; un microdata `"24.900"` se lee como 24900 con currency, no 24.9.
- **Via 3 (cruce ortogonal):** el conteo de vehiculos via extruct se cruza con el `_COUNT_HINT`/`declared` (dos familias: metadato schema.org vs texto visible) — deben concordar o REFUTED; ademas el `priceCurrency` del JSON-LD (metadato) debe concordar con el currency-default del pack (texto) o se marca.

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
- **Primaria — extruct** (deterministic-structured-extraction-upgrade, NEXT-LEVEL.md:285-291 [VERIFIED]): un solo motor battle-tested (scrapinghub) que extrae **JSON-LD + Microdata + RDFa + OpenGraph + Microformats + Dublin Core**, reemplazando `vehicles_from_jsonld`/`vehicles_from_microdata` a mano y subiendo el recall del peldano €0 ANTES de gastar un token de LLM. **BSD-3-Clause, €0 — https://github.com/scrapinghub/extruct** [VERIFIED NEXT-LEVEL.md:288]. Complemento: **trafilatura** (Apache-2.0) para main-content de la cola larga sin schema.org.
- **Acoplada — price-parser** (locale-money-correctness, NEXT-LEVEL.md:213-219 [VERIFIED]): `parse_money` sobre price-parser (extrae monto + simbolo/codigo de divisa, separadores por locale), respaldado por CLDR de Babel; cierra exactamente el bug `:104` `"24.900"`→24.9 y la currency descartada en `:79`. **BSD-3-Clause, €0 — https://github.com/scrapinghub/price-parser** [VERIFIED NEXT-LEVEL.md:216].
- **Corona (cola larga) — Crawl4AI `generate_schema`** (self-healing auto-resynthesis, NEXT-LEVEL.md:237-243 [VERIFIED]): para la web cutre JS-only que hoy queda FAILED, la IA sintetiza el field_map CSS **una vez** y el musculo determinista lo ejecuta a escala €0. **Apache-2.0, €0 — https://github.com/unclecode/crawl4ai** [VERIFIED NEXT-LEVEL.md:240].

#### Resolución condensada — Faceta 6
- **Costura** · 4 hardcodes ES en pipeline/recipe_extract_web.py: _STOCK_HINT (:28-30), _COUNT_HINT (:32), _MARKETPLACES (:33-34) y declared_path='page text: N vehículos' (:133) — mas el bug de dinero: microdata :104-105 entrega precio como string crudo sin parse_money y JSON-LD :79 descarta priceCurrency. Costura = inyectar LocaleProfile.{stock_hints,count_words,marketplace_blocklist} y enrutar todo precio por parse_money+currency.
- **Fix** · Compilar _STOCK_HINT/_COUNT_HINT/_MARKETPLACES desde pack.stock_hints/count_words/marketplace_blocklist (no literal); capturar priceCurrency en vehicles_from_jsonld:79 hacia CanonicalVehicle.currency; enrutar microdata price (:104-105) y jsonld price (:79) por parse_money(text, profile) para matar el latente float('24.900')=24.9. Sustituir vehicles_from_jsonld/microdata a mano por extruct (6 sintaxis) + trafilatura para la cola larga.
- **Adversarial** · FR ('occasion'/'vehicules') y DE ('Fahrzeuge'/'Gebrauchtwagen') no matchean ningun _STOCK_HINT ES -> find_stock_url=None -> sample vacio -> FAILED; el blocklist ES no filtra mobile.de/leboncoin.fr/subito.it; microdata IT/DE '24.900' sin parse -> 24.9 (1000x, ya danino EN ES); JSON-LD JP priceCurrency='JPY' descartado -> 3.000.000 JPY indistinguible de 3M EUR; OpenGraph rancio de pagina de error puede colar un vehiculo falso porque _valid solo exige name+price/url.
- **Sellado (multi-vía)** · Sellado: stock_hints/count_words/marketplace_blocklist desde pack (cero literal ES en el modulo) + todo precio por parse_money con currency + ES byte-identico. Verificacion: (1) golden ES = mismo Sample que hoy; (2) adversarial FR/DE/IT localiza inventario y '24.900'->24900 con currency; (3) cruce ortogonal conteo-extruct vs _COUNT_HINT y priceCurrency-metadato vs currency-default del pack (REFUTED si divergen).
- **Herramienta NEXT-LEVEL (€0)** · PRIMARIA: extruct (deterministic-structured-extraction-upgrade, NEXT-LEVEL.md:285-291) JSON-LD+Microdata+RDFa+OpenGraph+Microformats+DublinCore en un motor — BSD-3-Clause, EUR0 — https://github.com/scrapinghub/extruct [VERIFIED :288] (+ trafilatura Apache-2.0 cola larga). ACOPLADA: price-parser (locale-money-correctness, :213-219) para parse_money/currency, BSD-3-Clause — https://github.com/scrapinghub/price-parser [VERIFIED :216]. CORONA: Crawl4AI generate_schema (auto-resynthesis, :237-243) Apache-2.0 — https://github.com/unclecode/crawl4ai [VERIFIED :240] para la web JS-only que hoy queda FAILED.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-7"></a>

### Faceta 7 — Ciclo del arnés y pureza del veredicto (EXTRACT→VERIFY→PERSIST→DELETE)

> **Columna country-agnóstica · costura = profundidad de sello.** `decide_status` certifica COUNT, jamás normalización/moneda/región. **Liga:** F26. **Cross-ref:** facetas [26](#faceta-26)·[8](#faceta-8)·[9](#faceta-9)·[13](#faceta-13).

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/recipe_harness.py:80-91` `sample_paths`** [VERIFIED]: construye siempre `{"fetched": s.fetched, "parsed": len(s.parsed)}` (:88) y anade `source_declared` SOLO si `s.full_dealer and s.declared is not None` (:89-90). El gate full_dealer es exacto: un subset deliberado no inyecta declared y por tanto no fuerza REFUTED falso.
- **`:94-117` `decide_status`** [VERIFIED]: funcion PURA, firma `(s: Sample, k: int, verdict: str) -> tuple[str,str]`, sin DB ni red ni reloj. `target = s.declared if (s.full_dealer and s.declared is not None) else k` (:105); `loss = s.fetched - parsed_n` (:107); ramas FAILED: empty (:108), loss!=0 (:110-111), under-target `parsed_n < min(target,k) and not full_dealer` (:112-113), `verdict=="REFUTED"` (:114-115); VERIFIED final (:117). Cada salida lleva `reason` explicita: nunca un pase silencioso.
- **`:135-194`** [VERIFIED con MATIZ]: el hint atribuye el rango a "RecipeHarness.run", pero la CLASE `RecipeHarness` empieza en :135 y el metodo `run` real abarca **:150-194**. Correccion menor del hint.
- **`:150-152` sample acotado** [VERIFIED]: `run(self, dealer_ref, k: int = 5, ...)` (:150) y `sample = self._ex.sample(dealer_ref, k)` (:152) — k=5 por defecto acota el unico tiron de bytes.
- **`:189` delete** [VERIFIED exacto]: `sample.parsed.clear()` con comentario "dropping the reference IS the delete. No raw file is written by the harness".
- **`:172-175` Evidence inyectada** [VERIFIED exacto]: `Evidence(verified_at=self._now, sample_k=k, declared=..., fetched=..., parsed=..., vam_verdict=verdict, vam_paths=paths)`.
- **No listado en el hint pero [VERIFIED]**: `__init__` (:144-148) inyecta `now_iso` con comentario explicito ":148 scripts forbid Date.now()-style nondeterminism"; `_offline_verdict` (:196-207) es el espejo local del quorum.

#### (b) El mecanismo al atomo
`RecipeHarness.run` es la columna source/country-agnostica; ejecuta cinco pasos con frontera limpia frente a 02-scrape (drain vivo):
1. **EXTRACT** (:152) — `self._ex.sample(dealer_ref, k)`. Unico punto donde se consumen bytes; k acota a ~5 (jamas drena el dealer entero para verificar la receta).
2. **VERIFY** (:155-163) — `sample_paths(sample)` produce el dict de evidencia; con `conn` viva, `record_count_verdict(subject_type="recipe_sample", tolerance=0.0, claim_kind="count")` (:157-161) sella el quorum en DB; sin conn, `_offline_verdict(paths)` (:163). El offline-verdict (:196-207): `TRUSTWORTHY` si todos los valores coinciden (`len(set(vals))==1`), `REFUTED` si discrepan, `UNVERIFIED` si `<2` paths.
3. **DECIDE** (:165) — `decide_status(sample, k, verdict)` PURO -> `(status, reason)`. VERIFIED sii `fetched>0 ∧ parsed>0 ∧ loss==0 ∧ (parsed>=min(target,k) ∨ full_dealer) ∧ verdict!=REFUTED`.
4. **PERSIST** (:168-184) — arma `Recipe` con su `Evidence` y `write_recipe(...)` YAML; el fallo de persistencia se re-lanza (`raise` :184), nunca se traga.
5. **DELETE** (:189) — `sample.parsed.clear()`. El sample vive solo en memoria local; soltar la referencia ES el delete; no se escribe crudo, no hay nada que fugar.
`now_iso` inyectado (:148, :173) elimina el `Date.now()` no-determinista -> `run` y su `Evidence` son reproducibles y offline-testables.

#### (c) La costura ES->generico y su fix exacto
La columna del arnes ya es **casi** country-proof: no contiene un solo lexico ES, ni tabla, ni ruta. La costura NO es de idioma sino de **profundidad de sello**: `decide_status` certifica sobre **COUNT** (parse_loss + quorum de conteo), nunca sobre normalizacion, moneda o region. Una receta de pais nuevo cuyo extractor devuelva make/fuel/transmission TODO NULL o sin traducir pasa VERIFIED igual (sealing-hole que esta faceta hereda a la 26). Ademas el contrato sample-verify-delete es un contrato implicito: confia en que el extractor NO escriba crudo, pero nada lo enforce.
**Fix exacto (sin introducir ES en la columna):**
1. Mantener `run`/`decide_status`/`_offline_verdict` intactos en su pureza country-agnostica.
2. Anadir a `decide_status` un parametro opcional `fill_gate: FillReport | None` que calcula el orquestador `normalize_vehicle` ([faceta 13](#faceta-13)) con su piso en `LocaleProfile`: si `fill_rate(make|fuel|transmission) < piso` o `currency` ausente -> `STATUS_FAILED, "semantically empty sample"` en vez de VERIFIED. El piso vive en el pack, no en el codigo: cero acoplamiento a ES.
3. Mecanizar el contrato sample-verify-delete: asserto post-`run` de **0 ficheros crudo nuevos** bajo el dir de trabajo (no basta `parsed.clear()`).
4. Forzar `now_iso` inyectado en todo extractor (prohibir `datetime.now()` interno) para que la Evidence de cualquier pais sea reproducible.

#### (d) El riesgo adversarial concreto
- **DE/FR/IT/PT**: un extractor de pais nuevo cuyo `sample()` devuelva make/model/fuel crudo no-canonico ("Benzin"/"Automatik"/"MI") sella **VERIFIED** porque `fetched==parsed`; el ciclo CERTIFICA una receta semanticamente vacia.
- **Ruido**: un extractor que emita k dicts-basura idempotentes (el mismo registro x5) pasa `loss==0` y `parsed>=k` -> VERIFIED. El quorum cuenta filas, no valida contenido.
- **JP/no-UE**: `declared` no-numerico (patron autocasion) deja `source_declared` fuera del quorum -> `_offline_verdict` con solo 2 paths (`fetched==parsed`) da `TRUSTWORTHY` trivial; el tercer camino del quorum se pierde justo donde el pais nuevo mas lo necesita.
- **Determinismo**: si el extractor del pais nuevo ignora la inyeccion de `now_iso` y usa `datetime.now()` interno, reintroduce no-determinismo en su `Evidence` -> el replay ([faceta 9](#faceta-9)) deja de ser byte-identico.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado de la faceta:** (i) `decide_status` permanece 100% PURO — verificable por AST-lint que prohibe `asyncpg`/`datetime`/`open` dentro de la funcion; (ii) el sample NUNCA toca disco — test que corre `run` y asevera 0 ficheros nuevos + referencia liberada; (iii) k-acotado universal — `assert fetched <= k` salvo full_dealer; (iv) `fill_gate` semantico activo.
**Multi-via:** (1) **golden por-ejemplo** — matriz `status x verdict` del `decide_status`; (2) **property-based (Hypothesis)** — genera `Sample` arbitrarios y asevera invariantes: `empty => FAILED`, `loss>0 => FAILED`, `REFUTED => FAILED`, "nunca VERIFIED con `parsed==0`", minimizando al contraejemplo mas simple; (3) **via ortogonal (in-toto)** — la `Evidence`+`verdict` firmados se re-derivan en proceso limpio y deben coincidir, certificando la procedencia sin retener una sola fila cruda.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **Primaria: Hypothesis** (MPL-2.0, €0) — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320]. `decide_status` es PURO, candidato perfecto a property-based fuzzing: convierte "offline-testable" en "exhaustivamente probado" generando `Sample` adversariales (declared None, fetched/parsed dispares, full_dealer x declared) y minimizando el fallo. Es, por construccion, la 2a via adversarial del ritual de cierre.
- **Complemento: in-toto** (Apache-2.0, €0) — https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:312]. Eleva sample-verify-delete de "borro el crudo" a "recibo de procedencia firmado y tamper-evident" (quien/que/cuando + parse_loss + quorum VAM + hash del golden), hash-chained al estilo verdict_audit; cierra el sealing-hole "consistencia interna pero no certificable externamente" con cadena de custodia legal €0, sin guardar una fila de inventario.

#### Resolución condensada — Faceta 7
- **Costura** · La columna run/decide_status/_offline_verdict (recipe_harness.py:150-207) ya es country-agnostica (cero lexico ES); la costura NO es de idioma sino de PROFUNDIDAD DE SELLO: decide_status (:94-117) certifica sobre COUNT (parse_loss + quorum) y nada mas, asi que una receta de pais nuevo con make/fuel/transmission NULL o sin traducir y sin currency/region pasa VERIFIED igual. Ademas el contrato sample-verify-delete (:189 parsed.clear()) confia en que el extractor no escriba crudo, sin asserto mecanico que lo enforce.
- **Fix** · 1) No introducir ES en la columna. 2) decide_status gana un parametro opcional fill_gate (FillReport del normalize_vehicle de [faceta 13](#faceta-13), piso definido en LocaleProfile): si fill_rate(make|fuel|transmission) < piso o currency ausente -> STATUS_FAILED 'semantically empty sample' en vez de VERIFIED; el piso vive en el pack (cero acoplamiento ES). 3) Asserto post-run de 0 ficheros crudo nuevos en el dir de trabajo (mecanizar sample-verify-delete, no solo confiar en parsed.clear()). 4) Forzar now_iso inyectado (:148) en todo extractor, prohibiendo datetime.now() interno.
- **Adversarial** · DE/FR/IT/PT: un extractor de pais nuevo con make/model/fuel crudo no-canonico ('Benzin'/'Automatik'/'MI') sella VERIFIED porque fetched==parsed (el quorum cuenta filas, no contenido). Ruido: k dicts-basura idempotentes (mismo registro x5) pasan loss==0 y parsed>=k -> VERIFIED. JP/no-UE: declared no-numerico saca source_declared del quorum -> _offline_verdict (:196-207) con 2 paths da TRUSTWORTHY trivial, se pierde el tercer camino. Si el extractor ignora la inyeccion de now_iso y usa datetime.now() interno, reintroduce no-determinismo en la Evidence y el replay ([faceta 9](#faceta-9)) deja de ser byte-identico.
- **Sellado (multi-vía)** · (i) decide_status 100% PURO verificado por AST-lint que prohibe asyncpg/datetime/open dentro de la funcion. (ii) Test que corre run() y asevera 0 ficheros nuevos en disco + referencia del sample liberada. (iii) assert fetched<=k salvo full_dealer (k-acotado universal). (iv) fill_gate semantico activo. Multi-via: golden matriz status x verdict + property-based Hypothesis (empty/loss>0/REFUTED nunca VERIFIED, minimiza contraejemplo) + via ortogonal in-toto (re-derivar Evidence+verdict en proceso limpio y que coincidan).
- **Herramienta NEXT-LEVEL (€0)** · Hypothesis (MPL-2.0, €0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320] — property-based fuzzing del decide_status PURO: genera Sample adversariales (declared None, fetched/parsed dispares, full_dealer x declared) y minimiza al contraejemplo, elevando 'offline-testable' a 'exhaustivamente probado'. Complemento in-toto (Apache-2.0, €0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:312] — atestacion firmada y tamper-evident del veredicto+Evidence (parse_loss + quorum VAM + hash golden), cadena de custodia €0 sin retener crudo; cierra el sealing-hole de certificabilidad externa.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-8"></a>

### Faceta 8 — Verificación VAM de integridad de conteo (declared/fetched/parsed)

> **F11 · SEAL count-only (raíz).** El quórum VAM cuenta enteros (fetched/parsed/declared), estructuralmente ciego al contenido. SH1. **Cross-ref:** facetas [26](#faceta-26)·[11](#faceta-11)·[12](#faceta-12)·[21](#faceta-21).

#### (a) Code_hints [VERIFIED]
- `pipeline/recipe_harness.py:80-91` `sample_paths`: construye `{'fetched': s.fetched, 'parsed': len(s.parsed)}` y anade `'source_declared'` SOLO si `s.full_dealer and s.declared is not None` (`:89-90`) [VERIFIED].
- `:94-117` `decide_status`: `target = s.declared if (full_dealer and declared is not None) else k` (`:105`); `loss = s.fetched - parsed_n` (`:107`); FAILED si sample vacio (`:108`), si `loss != 0` (`:110-111`), si bajo target (`:112-113`), si `verdict=='REFUTED'` (`:114-115`); si no VERIFIED (`:116-117`) [VERIFIED].
- `:155-161` `run()` llama `record_count_verdict(subject_type='recipe_sample', ..., tolerance=0.0, claim_kind='count')` [VERIFIED].
- `pipeline/recipe_schema.py:89-93` propiedad `parse_loss = fetched - parsed` [VERIFIED].
- `pipeline/verify.py:53-212` `record_count_verdict`: `paths` es `{name:int}`; `_path_family` (`:31-50`) mapea nombres a familias db/http/source/registral/other; TRUSTWORTHY exige `modal_ok` (>=2 valores identicos) AND `has_independence` (>=2 familias Y >=2 origenes) AND `zero_certifiable` (`:155-159`); el quorum es PURAMENTE sobre conteos enteros [VERIFIED].

#### (b) Mecanismo al atomo
El VAM es un quorum de conteo cero-confianza. `sample_paths` ensambla hasta 3 paths ENTEROS: fetched (familia http), parsed (familia db), source_declared (familia source, solo en full_dealer). `record_count_verdict` calcula un cluster modal: TRUSTWORTHY sii >=2 paths comparten el MISMO entero exacto Y provienen de >=2 familias/origenes distintos Y el modal no es un cero no-observado. `decide_status` luego sella VERIFIED sobre: sample no-vacio, parse_loss==0, >= min(target,k), y no REFUTED. `full_dealer` es el gate portador: declared entra al quorum SOLO si el sample cubre el dealer entero (declared<=k), si no un subset deliberado haria declared!=parsed y forzaria un REFUTED falso (`:86-87`,`:56-57`). El ATOMO del hueco: cada path es `len(list)` o un contador int -> el quorum es estructuralmente ciego al CONTENIDO de cada dict parseado.

#### (c) Costura ES->generico
La logica VAM YA es country-agnostica (datos por pais, logica identica): las claves de `_path_family` ('numberofresults','declared','fetched','db') son vocabulario-de-fuente, no ES. La costura NO es un literal; es el HUECO SEMANTICO: el quorum certifica que fetched==parsed==declared como ENTEROS, jamas que las filas parseadas lleven make valido / precio en la moneda correcta / region valida. Un pais generico hereda esta ceguera intacta. El fix no es cambiar el VAM (su quorum de conteo es correcto para lo que mide) sino ANADIR un gate de contenido ortogonal.

#### (d) Riesgo adversarial concreto
El quorum es ciego al contenido: a escala, un parser que emite N filas con price corrupto 1000x (MX '1,234.56'->1.23456) o region mal-mapeada (FR '75'->Toledo) pasa TRUSTWORTHY porque fetched==parsed. Una receta DE/IT/PT con make/fuel/transmission TODO NULL o sin traducir sella VERIFIED (`decide_status` nunca los inspecciona). Una fuente extranjera con paginacion por cursor y sin declared numerico deja declared=None -> el quorum cae a fetched-vs-parsed (2 paths casi mono-familia) que resuelve UNVERIFIED (no REFUTED) y AUN pasa `decide_status` (UNVERIFIED se acepta en `:100-102`). Resultado: una receta semanticamente vacia certifica verde.

#### (e) Sellado + verificacion multi-via
Criterio: VERIFIED exige (existente) parse_loss==0 + quorum de conteo no-REFUTED, MAS (nuevo) contrato de contenido verde: piso de fill-rate de make (make∈brand_table), currency presente+coherente, region pack-parseable, fuel/transmission ∈ enum neutral. Multi-via: (1) quorum de conteo (declared⟂fetched⟂parsed, verify.py, intacto); (2) contrato de contenido (Great Expectations/Pandera sobre `sample.parsed`); (3) replay (RecipeRunner, [faceta 9](#faceta-9)) reproduce el mismo parsed-count desde el YAML en proceso limpio. Sella solo cuando los tres son verde. Test adversarial: inyectar N filas todas con price 1000x o region='75'-as-ES -> el quorum de conteo pasa pero el contrato de contenido FALLA el sello (prueba el hueco cerrado).

#### (f) Herramienta NEXT-LEVEL
Great Expectations, Apache-2.0, https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Corre un contrato de datos versionado y BLOQUEANTE sobre el sample ANTES del sello: pisos de fill-rate, pertenencia a enum, coherencia de moneda, validez de region — convirtiendo la precondicion semantica oculta en un INVARIANTE ejecutable fail-CLOSED (el framing exacto de la biblia: 'el estrato falla CERRADO, no abierto'). Alternativas: Pandera, Soda Core, dbt tests. Adyacente para el lado dedup-count: ER-Evaluation (AGPL-3.0, https://github.com/OlivierBinette/er-evaluation, NEXT-LEVEL.md:522) para cardinalidad certificada con intervalos de confianza — usar SOLO offline para evitar el copyleft-de-red AGPL en el path servido (biblia:524).

#### Resolución condensada — Faceta 8
- **Costura** · La logica VAM ya es country-agnostica (datos por pais, logica identica; las claves de _path_family son vocabulario-de-fuente, no ES). La costura es el HUECO SEMANTICO: sample_paths/decide_status/record_count_verdict cuentan ENTEROS (fetched/parsed/declared) y son estructuralmente ciegos al contenido de cada dict parseado (make/price-currency/region). Un pais generico hereda la ceguera intacta.
- **Fix** · Mantener record_count_verdict y decide_status como estan (el quorum de conteo es correcto). Anadir un gate de contenido entre los pasos 2 y 3 de run(): computar fill-rate/coherencia sobre sample.parsed ANTES de devolver VERIFIED — make∈brand_table>=piso, price con currency presente y ==LocaleProfile.currency o in-band, region parseable por el pack, fuel/transmission∈enum neutral. Expresarlo como schema Pandera/Great Expectations; un breach -> STATUS_FAILED reason 'content contract breach: <cual>'. Hace el sello normalization-aware (liga a [faceta 26](#faceta-26)) sin debilitar el quorum de conteo.
- **Adversarial** · Ciego al contenido: a escala un parser que emite N filas con price 1000x (MX) o region mal-mapeada (FR '75'->Toledo) pasa TRUSTWORTHY porque fetched==parsed. Una receta DE/IT/PT con make/fuel/transmission NULL o sin traducir sella VERIFIED. Una fuente cursor sin declared numerico deja declared=None -> quorum cae a fetched-vs-parsed -> UNVERIFIED, que decide_status ACEPTA (:100-102) -> receta vacia certifica verde.
- **Sellado (multi-vía)** · VERIFIED = (existente) parse_loss==0 + quorum no-REFUTED + (nuevo) contrato de contenido verde (fill-rate make, currency coherente, region pack-parseable, fuel/transmission enum). Multi-via: (1) quorum de conteo declared⟂fetched⟂parsed (verify.py intacto); (2) contrato de contenido Great Expectations/Pandera sobre sample.parsed; (3) replay RecipeRunner en proceso limpio. Adversarial: N filas con price 1000x o region='75' -> conteo pasa, contenido FALLA el sello.
- **Herramienta NEXT-LEVEL (€0)** · Great Expectations — Apache-2.0 — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Contrato de datos versionado bloqueante PRE-sello (fill-rate, enum, currency-coherente, region valida) = invariante fail-CLOSED. Alt: Pandera, Soda Core, dbt tests. Adyacente: ER-Evaluation (AGPL-3.0, https://github.com/OlivierBinette/er-evaluation, NEXT-LEVEL.md:522) para cardinalidad con CIs, solo offline por el AGPL.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-9"></a>

### Faceta 9 — Replay / prueba de autosuficiencia (`RecipeRunner.replay`)

> **2ª vía ortogonal · independencia ilusoria.** `replay` re-ejecuta `EXTRACTORS[source]().sample` (el mismo Python), no interpreta el YAML. **Cross-ref:** facetas [2](#faceta-2)·[3](#faceta-3).

#### (a) Verificacion de code_hints contra el codigo real
- [VERIFIED pipeline/recipe_harness.py:220-255] clase `RecipeRunner` con `replay(self, recipe_path, k=5) -> ReplayResult`.
- [VERIFIED pipeline/recipe_harness.py:228-231] disclaimer HONESTY: *"a fully field-map-driven interpreter ... is deliberately NOT claimed here — the extractor still owns the parse code."*
- [VERIFIED pipeline/recipe_harness.py:243-244] `recipe = Recipe.from_dict(yaml.safe_load(fh))`: re-hidrata la receta SOLO desde el YAML.
- [VERIFIED pipeline/recipe_harness.py:245-247] `if recipe.source not in EXTRACTORS: return ReplayResult(... False, 0, 0, f"no extractor registered for source {recipe.source!r}")`.
- [VERIFIED pipeline/recipe_harness.py:248] `sample = EXTRACTORS[recipe.source]().sample(recipe.dealer_ref, k)`: re-ejecuta el Python del extractor, **no** interpreta field_map.
- [VERIFIED pipeline/recipe_harness.py:249-250] `loss = sample.fetched - len(sample.parsed); reproduced = len(sample.parsed) > 0 and loss == 0`.

#### (b) El mecanismo al atomo
`replay` es la **2a via**, ortogonal a la que CONSTRUYE (`RecipeHarness`). Tesis: re-extraer SOLO desde el YAML en proceso limpio y exigir `reproduced==True` (`parsed>0 ∧ loss==0`), probando "re-scrape sin crudo retenido". Atomo del defecto: la independencia es **solo de proceso** (memoria limpia, sin crudo), **no de codigo** — :248 re-corre `EXTRACTORS[recipe.source]().sample`, el MISMO Python que construyo la receta. El disclaimer (228-231) lo admite con honestidad: NO hay interprete de field_map.

#### (c) Costura ES->generico + fix exacto
- **Costura:** la 2a via depende de que `EXTRACTORS[recipe.source]` exista en el proceso; si el source no esta registrado, devuelve `reproduced=False "no extractor"` (245-247). Una receta de pais #2 cuyo Python no este desplegado NO puede certificarse por la via ortogonal => la independencia se evapora.
- **Fix:** (1) **Acoplar con facet 2:** cuando `Parsing.engine` sea enum ejecutable, `replay` deja de hacer `EXTRACTORS[source]().sample` y pasa a **interpretar** el field_map puramente desde el YAML via `Selector.locate(bytes, container_path, field_map)`. (2) La rama "no extractor registered" (245-247) **desaparece**: el replay ya solo necesita el engine-interprete generico + el YAML. (3) Mantener el contrato `reproduced = parsed>0 ∧ loss==0` (250) intacto — el criterio no cambia, solo el motor.

#### (d) Riesgo adversarial concreto
- **HOY (DE/FR/IT/PT):** una receta DE byte-perfecta con `source="autoscout24_de"` no registrado en `EXTRACTORS` => `reproduced=False "no extractor"` => la via ortogonal **no puede certificar** el pais nuevo hasta desplegar su Python, anulando su unica razon de ser.
- Replay que re-ejecuta Python pasa en ES (modulo presente) y da **falsa confianza** de "autosuficiencia" que el pais #2 no tiene.
- Si el interprete (facet 2) entra sin paridad, replay puede reportar `reproduced=True` con un `Vehicle` distinto al original (regresion silenciosa enmascarada de "reproducido").

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** replay reproduce el sample **interpretando el field_map del YAML** en proceso limpio, sin importar el modulo Python de la fuente; `reproduced==True` sii `parsed>0 ∧ loss==0`; CUALQUIER pais sobre un engine conocido se certifica sin desplegar Python.
- **Via 1 (test):** replay de una receta ES produce `Vehicle` byte-identico al harness original.
- **Via 2 (adversarial):** receta con engine valido pero field_map roto => `reproduced=False` con razon (no crash).
- **Via 3 (independiente):** la MISMA receta replayed en una maquina SIN `pipeline.sources.<source>` instalado sigue dando `reproduced=True` (prueba la auto-suficiencia real, no de-proceso).

#### (f) Herramienta NEXT-LEVEL
**parsel** (palanca primaria) — [VERIFIED NEXT-LEVEL.md:264] https://github.com/scrapy/parsel, **BSD-3-Clause, EUR0=True**: convierte replay de "re-ejecuta sample() Python" a "interpreta field_map". El propio NEXT-LEVEL.md:267(c) lo cita: *"RecipeRunner.replay en proceso limpio interpreta el YAML y reproduce el sample sin importar el modulo Python de la fuente — prueba la auto-suficiencia que el diseno solo afirmaba."* **Complemento de sellado:** **in-toto** — [VERIFIED NEXT-LEVEL.md:312] https://github.com/in-toto/in-toto, **Apache-2.0, EUR0=True**: firma el veredicto de reproduccion (parse_loss + hash del golden) haciendo la via ortogonal **certificable por un tercero** sin guardar crudo.

#### Resolución condensada — Faceta 9
- **Costura** · La independencia de replay es ilusoria: re-ejecuta EXTRACTORS[recipe.source]().sample (recipe_harness.py:248), el mismo Python que construyo; si el source no esta registrado devuelve reproduced=False 'no extractor' (:245-247). La 2a via depende del DESPLIEGUE del Python de la fuente, no solo del YAML — el disclaimer (228-231) lo admite.
- **Fix** · Acoplar con facet 2: con Parsing.engine como enum ejecutable, replay deja de hacer EXTRACTORS[source]().sample y pasa a interpretar el field_map desde el YAML via Selector.locate(bytes,container_path,field_map). La rama 'no extractor registered' (:245-247) desaparece: replay solo necesita el engine-interprete generico + el YAML. Mantener reproduced = parsed>0 and loss==0 (:250) intacto.
- **Adversarial** · Receta DE byte-perfecta con source 'autoscout24_de' no registrado en EXTRACTORS => reproduced=False 'no extractor': la via ortogonal NO certifica el pais nuevo hasta desplegar su Python, anulando su independencia. Replay que re-ejecuta Python pasa en ES (modulo presente) dando falsa autosuficiencia. Interprete sin paridad => reproduced=True con Vehicle distinto = regresion enmascarada.
- **Sellado (multi-vía)** · Sello: replay reproduce interpretando el field_map del YAML en proceso limpio sin importar el Python de la fuente; reproduced==True sii parsed>0 and loss==0; cualquier pais sobre engine conocido se certifica sin desplegar Python. Multi-via: (1) replay ES => Vehicle byte-identico al harness; (2) adversarial = field_map roto => reproduced=False con razon, no crash; (3) independiente = misma receta en maquina SIN pipeline.sources.<source> sigue reproduced=True.
- **Herramienta NEXT-LEVEL (€0)** · parsel [VERIFIED NEXT-LEVEL.md:264] https://github.com/scrapy/parsel BSD-3-Clause EUR0=True (palanca primaria: replay interpreta el YAML, NEXT-LEVEL.md:267c). Complemento: in-toto [VERIFIED NEXT-LEVEL.md:312] https://github.com/in-toto/in-toto Apache-2.0 EUR0=True firma el veredicto de reproduccion (parse_loss+hash golden) => via ortogonal certificable por tercero sin crudo.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-10"></a>

### Faceta 10 — Plantilla de transporte/paginación capturada + oráculo `declared`

> **Plano A — ACQUIRE.** `strategy` enum rancio + `url_template` ES (`/profesionales/`) + `ja3` declarado-jamás-poblado. **Cross-ref:** facetas [2](#faceta-2)·[8](#faceta-8)·[22](#faceta-22).

#### (a) Verificacion de code_hints [VERIFIED]
- **Pagination** `pipeline/recipe_schema.py:53-61` [VERIFIED]: `strategy` default `"page_param"`, comentario `:56` enumera SOLO `page_param | cursor | sitemap | single_page`. Pero las recetas vivas usan valores **FUERA** del comentario: `ccn strategy="json_post_page"` (`recipe_extractors.py:179`), `ac strategy="ssr_enumerate_then_gql_hydrate"` (:239). -> `strategy` es **vocab abierto de-facto**, el comentario esta rancio. `declared_path` (:59) y `stop` (:60) igualmente strings abiertos.
- **Fingerprint** `recipe_schema.py:45-51` [VERIFIED]: `user_agent` + `ja3` ("Tier-1 only" :50). **GREP CONFIRMA: `ja3` se declara SOLO en `recipe_schema.py:50` y se FIJA en NINGUN extractor** -> las 5 recetas ES dejan `ja3=None` (campo dormante). `as24` fija `Fingerprint(user_agent=as24._UA)` (`recipe_extractors.py:52`); las plataformas `user_agent="engine-managed"` (:118,177,237).
- **Transport** `recipe_schema.py:36-43` [VERIFIED]: `engine`/`base_url`/`impersonate`/`timeout_s`. `base_url` per-source (`as24._BASE` :49, `ccom._SRP_HOST` :116, `ccn.ENDPOINT` :175, `ac.SSR_HOST` :235).
- **declared_path como oraculo** [VERIFIED]: `as24 "numberOfResults"` (:57), `ccom "props.pageProps.classifieds.total"` (:123), `ccn "meta.totalResults"` (:182), `ac "ssr id-set stops changing"` (:242 — **NO numerico**; `sample()` devuelve `declared=None` :277).
- **url_template ES-hardcodeado** `recipe_extractors.py:55` [VERIFIED]: `"/profesionales/{slug}?atype=C&sort=price&desc=1&page={page}"` — `/profesionales/` es segmento de ruta ES.

#### (b) Mecanismo al atomo
La receta carga TODO lo que el replay necesita para **relocalizar+enumerar** la fuente SIN crudo: `Transport` (como se piden los bytes), `Fingerprint` (la identidad TLS/UA), `Pagination` (como enumerar + donde parar + el oraculo declared). `declared_path` alimenta `full_dealer` en el quorum VAM: `sample_paths` anade `source_declared` SOLO si `full_dealer` (`recipe_harness.py:89`). El oraculo es el **TERCER camino** del quorum de conteo (declared vs fetched vs parsed), la unica via de familia-fuente.

#### (c) Costura ES->generico + fix exacto
**Costura:** (1) `pagination.strategy` esta documentado como enum cerrado (`recipe_schema.py:56`) pero es un **string abierto** ya con 2 valores fuera del comentario — misma enfermedad que `parsing.engine`. (2) `url_template` incrusta segmentos ES (`/profesionales/`) -> no porta a `.de`. (3) `declared_path` puede no existir en fuente foranea (autocasion ya es `declared=None`) -> el VAM pierde su tercer camino justo donde el pais nuevo mas lo necesita. (4) `ja3` es campo **declarado-pero-jamas-poblado** -> el pinning Tier-1 esta sin implementar; un pais que necesite huella Firefox-shaped o coherente-por-pais no tiene valor capturado.

**Fix:**
1. **Cerrar `pagination.strategy` Y `parsing.engine`** a `Literal`/enum con el set observado completo `{page_param, cursor, sitemap, single_page, json_post_page, ssr_enumerate_then_gql_hydrate}` + **mapa de alias en `from_dict`** para las 61 recetas flat ya persistidas (compat, gobernanza [faceta 1](#faceta-1)). `__post_init__` validador en `Pagination` espejando `Recipe.status` (`recipe_schema.py:112-115`).
2. **Mover TODO string ES** (segmentos de url_template, accept_language, plantillas de ruta) al country-pack; la receta carga solo el slug per-dealer. `/profesionales/` se vuelve dato del pack ES.
3. `declared_path` PRESENCIA opcional pero con tag `declared_kind` (`numeric_total | id_set_stable | none`) para que el VAM sepa si declared entra al quorum (el `id_set_stable` de autocasion es honestamente `declared=None`, no un oraculo ausente por bug).
4. **Poblar `Fingerprint`** (ua + ja3 + accept_language) desde un generador coherente por-pais en vez de dejar `ja3` dormante y `accept_language` hardcodeado.

#### (d) Riesgo adversarial concreto
- **Cursor/sitemap FR/DE:** una fuente que pagina por token cursor o sitemap.xml no es expresable por el comentario-enum rancio; tras cerrar, requiere ensanchar el enum (y sin interprete, aun exige Python por fuente).
- **declared_path inexistente DE/FR:** fuente sin total declarado -> `declared=None` -> VAM corre sobre 2 caminos de la MISMA familia (fetched/parsed) -> verdict UNVERIFIED, jamas TRUSTWORTHY -> el sello pierde su tercer camino para el pais nuevo.
- **url_template `/profesionales/` es ES:** autoscout24.de usa una ruta de dealer distinta -> la plantilla capturada scrapea la URL equivocada o 404.
- **ja3 dormante:** un WAF .de que perfila TLS Firefox-shaped recibe un JA3 Chrome de curl_cffi con `Accept-Language` es-ES -> tell geo/locale (NEXT-LEVEL CRITICAL #1), interstitials servidos como inventario.
- **Ruido:** un oraculo declared rancio (la fuente cambia la clave `numberOfResults`) -> declared silenciosamente None/erroneo -> quorum degradado sin senal de drift.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** (1) `pagination.strategy ∈ enum cerrado` Y cada receta ES persistida aun carga via mapa de alias (compat [faceta 1](#faceta-1), round-trip byte-identico); (2) `declared_kind` presente y gate `full_dealer` coherente (declared entra al quorum sii `numeric_total ∧ full_dealer`); (3) CERO strings ES en el cuerpo de la receta — guard-grep asevera que `url_template` no lleva literal-pais; (4) `Fingerprint` ja3+accept_language poblado y coherente por pack.
- **Multi-via:** (via1) unit test offline de `sample_paths`/`decide_status` con declared presente vs ausente; (via2) replay reproduce la enumeracion desde el YAML solo, en proceso limpio; (via3) un echo-server captura el `Accept-Language`/JA3 emitido y asevera que iguala el valor declarado del pack, no un literal del engine (patron via-independiente NEXT-LEVEL.md:211/299).

#### (f) Herramienta NEXT-LEVEL que la eleva
**fingerprint-coherence-engine · browserforge** (Apache-2.0, https://github.com/daijro/browserforge) [VERIFIED NEXT-LEVEL.md:205-211]. Genera una huella **coherente por (country,browser,os)** — TLS/JA3 + UA + client-hints + Accept-Language + screen mutuamente consistentes — matando el `es-ES` hardcodeado y poblando el `ja3` dormante; keyed por `pack.accept_language`+`pack.country`. CPU puro (~0.1-0.2 ms/huella), €0, Apache-2.0 limpio. **Complementos:** tls-impersonation-breadth · primp (MIT, https://github.com/deedy5/primp) [VERIFIED NEXT-LEVEL.md:293-299] ensancha `Transport.impersonate` mas alla del pool Chrome de curl_cffi (Safari/Firefox/Edge/Opera JA3/JA4) para un WAF no-Chrome de un pais nuevo antes de escalar a Tier-1; defense-tier-preselect · PyrateLimiter (MIT, https://github.com/vutran1710/PyrateLimiter) [VERIFIED NEXT-LEVEL.md:301-307] liga el pace a `PlatformSpec.defense_tier` con bucket distribuido PG/Redis para gobernar el drain de paginacion multi-proceso.

#### Resolución condensada — Faceta 10
- **Costura** · pagination.strategy documentado como enum cerrado (recipe_schema.py:56) pero es string abierto con 2 valores fuera del comentario (json_post_page recipe_extractors.py:179, ssr_enumerate_then_gql_hydrate :239). url_template incrusta segmentos ES (/profesionales/ :55) -> no porta a .de. declared_path puede no existir en fuente foranea (autocasion declared=None :242,277) -> VAM pierde el 3er camino del quorum. ja3 declarado en recipe_schema.py:50 pero FIJADO en ningun extractor (grep) -> pinning Tier-1 sin implementar.
- **Fix** · Cerrar pagination.strategy Y parsing.engine a Literal/enum con el set observado {page_param,cursor,sitemap,single_page,json_post_page,ssr_enumerate_then_gql_hydrate} + mapa de alias en from_dict para las 61 recetas flat (compat [faceta 1](#faceta-1)) + __post_init__ validador espejando Recipe.status (recipe_schema.py:112-115). Mover todo string ES (url_template, accept_language) al pack; la receta carga solo el slug. Anadir declared_kind (numeric_total|id_set_stable|none) para que el VAM sepa si declared entra al quorum. Poblar Fingerprint(ua+ja3+accept_language) desde generador coherente por-pais.
- **Adversarial** · Cursor/sitemap FR/DE no expresable por el enum rancio. declared_path inexistente DE/FR -> declared=None -> VAM sobre 2 caminos misma-familia -> UNVERIFIED jamas TRUSTWORTHY, sello pierde el 3er camino. url_template '/profesionales/' es ES -> autoscout24.de scrapea URL equivocada/404. ja3 dormante -> WAF .de Firefox-shaped recibe JA3 Chrome + Accept-Language es-ES = tell geo/locale (NEXT-LEVEL CRITICAL #1), interstitials como inventario. Oraculo declared rancio (clave numberOfResults cambia) -> quorum degradado sin senal de drift.
- **Sellado (multi-vía)** · Sello: (1) pagination.strategy en enum cerrado Y cada receta ES carga via alias (round-trip byte-identico, compat [faceta 1](#faceta-1)); (2) declared_kind presente, gate full_dealer coherente (declared entra sii numeric_total ∧ full_dealer); (3) cero strings ES en el cuerpo (guard-grep sobre url_template); (4) Fingerprint ja3+accept_language poblado por pack. Multi-via: unit test offline sample_paths/decide_status con declared presente vs ausente | replay reproduce enumeracion desde YAML en proceso limpio | echo-server captura Accept-Language/JA3 emitido == valor declarado del pack (no literal del engine).
- **Herramienta NEXT-LEVEL (€0)** · fingerprint-coherence-engine · browserforge (Apache-2.0, https://github.com/daijro/browserforge) [VERIFIED NEXT-LEVEL.md:205-211] — huella coherente por (country,browser,os): TLS/JA3+UA+client-hints+Accept-Language+screen, mata el es-ES hardcodeado y puebla el ja3 dormante, keyed por pack.accept_language+pack.country, CPU €0. Complementos: primp (MIT, https://github.com/deedy5/primp) [VERIFIED NEXT-LEVEL.md:293-299] ensancha Transport.impersonate (Safari/Firefox/Edge/Opera JA3/JA4); PyrateLimiter (MIT, https://github.com/vutran1710/PyrateLimiter) [VERIFIED NEXT-LEVEL.md:301-307] pace por defense_tier con bucket distribuido PG/Redis.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-11"></a>

### Faceta 11 — Contrato de salida `CanonicalVehicle` unificado y versionado

> **F2 · CURRENCY absent (contrato).** No existe `CanonicalVehicle`/`CONTRACT_VERSION`; cada conector define su dataclass divergente (`vin_ref`/`listing_ref`/`segment`). MP1. **Cross-ref:** facetas [12](#faceta-12)·[18](#faceta-18)·[19](#faceta-19)·[14](#faceta-14).

#### (a) Verificacion de code_hints [VERIFIED]
- **AS24.Vehicle** — `pipeline/sources/autoscout24.py:40-52` [VERIFIED]: `@dataclass Vehicle{deep_link, vin_ref, title, make, model, year, km, price, fuel, transmission, photo_url}`. **Sin `currency`, sin `*_code`, sin `raw_locale_fields`**; identidad por `vin_ref`.
- **coches.net.Vehicle** — `pipeline/platform/coches_net_wholesale.py:163-177` [VERIFIED]: mismos campos PERO identidad por `listing_ref` (no `vin_ref`) y **campo EXTRA `price_drop: dict | None`** (`:177`).
- **coches.com.Vehicle** — `pipeline/platform/coches_com_wholesale.py:362-425` [VERIFIED]: `parse_card_vehicle` retorna `Vehicle(... price_drop=price_drop, segment=segment, listing_url=surface_listing_url(...))` (`:409-425`) — **DOS campos EXTRA `segment` y `listing_url`** ausentes en AS24.
- **consumo por duck-typing** — `pipeline/ingest.py:96-101` [VERIFIED]: el `INSERT INTO vehicle` lee `v.deep_link, v.title, make_norm, v.model, year_clean, km_clean, price_clean, v.fuel, v.transmission, v.photo_url, v.vin_ref` campo-a-campo via `getattr` implicito. **Ningun tipo comun**: cada conector define su propia dataclass y `ingest` confia en que los campos existan.
- **versionado de receta != contrato de salida** — `recipe_schema.py:27 SCHEMA_VERSION=2` [VERIFIED] versiona la RECETA, NO el `Vehicle` de salida; no existe `CONTRACT_VERSION` para la forma servida (grep 0 hits).

#### (b) Mecanismo al atomo
Aguas abajo (`ingest`/`delta`/`identity`) el sistema asume una forma `Vehicle` **por convencion, no por contrato**: lee `v.deep_link` como clave dedup/delta, `v.vin_ref` como `source_ref`, y `price/km/fuel/transmission` como columnas. El atomo de riesgo: la forma es **implicita y divergente** — `vin_ref` vs `listing_ref`, `price_drop`/`segment`/`listing_url` presentes en unos y ausentes en otros. `ingest` sobrevive porque solo toca el subconjunto comun, pero **nada garantiza** que un conector nuevo emita ese subconjunto ni que lo nombre igual.

#### (c) Costura ES->generico
El duck-typing **oculta divergencias estructurales**: no hay un `CanonicalVehicle{deep_link, source_ref, title, make, model, year, km, price, currency, fuel_code, transmission_code, photo_url, raw_locale_fields}` con `CONTRACT_VERSION`. Falta la **dimension `currency`** (price es `float` pelado en AS24 `:49`), faltan **codigos neutrales** (`fuel`/`transmission` verbatim ES, hereda a [facetas 18/19](#faceta-18)), y falta `raw_locale_fields` para preservar el string original (auditabilidad sin romper sample-verify-delete). Fix: reificar `CanonicalVehicle` como dataclass unica versionada; cada conector emite EXACTAMENTE esa forma; `source_ref` unifica `vin_ref`/`listing_ref`; los extras (`price_drop`/`segment`/`listing_url`) o se promueven al contrato o se mueven a un `extra: dict`.

#### (d) Riesgo adversarial concreto
- **PT/IT/FR conector nuevo** que **omita un campo** (p.ej. no setea `photo_url`) o lo **nombre distinto** (`registration_url` en vez de `listing_url`) -> pasa el harness (que solo cuenta filas) pero **rompe `ingest` a escala** con `AttributeError` o columna NULL silenciosa.
- **currency ausente** (CRITICAL cross-pais): un coche JP `5.000.000 JPY (~30k EUR)` es **indistinguible** de `5M EUR` en la columna `price` desnuda; un MXN `350.000 (~18k EUR)` parece `350k EUR`. El eje de busqueda/orden/ceiling se corrompe en cuanto entra el pais #2.
- **drift de forma invisible**: sin `CONTRACT_VERSION` no hay forma de detectar que coches.com lleva `segment` y AS24 no -> dos paises fragmentan la busqueda cross-pais por dataclasses divergentes.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello**: (1) **un unico `CanonicalVehicle` con `CONTRACT_VERSION`**; (2) TODO conector activo emite la forma exacta (test estructural por conector); (3) `currency` poblado y valido (ISO 4217) en cada fila; (4) `raw_locale_fields` preserva el string original.
- **Multi-via**: (i) **test** = cada conector produce un `CanonicalVehicle` que valida contra el esquema tipado (Pydantic) — campo faltante/mal-nombrado = ROJO; (ii) **adversarial** = inyectar un conector que omite `currency` -> el guard FALLA el build (fail-closed); (iii) **via independiente** = el `currency` capturado por `price-parser` (texto visible) se cruza contra `priceCurrency` del JSON-LD (metadato schema.org) — dos familias deben concordar o REFUTED.

#### (f) Herramienta NEXT-LEVEL
**Pydantic** (`Guard de drift ... como CONTRATO TIPADO en CI`) modela `CanonicalVehicle` como `BaseModel` con validators de coherencia y un test de CI que valida cada emision de conector contra el esquema: un campo omitido o un `currency` invalido es **build ROJO mecanico**, no un `AttributeError` en produccion. Complementos: **pycountry** (autoridad ISO 4217 para validar `currency` + ISO 3166-2; LGPL-2.1, uso build-time) y **price-parser** (poblar `currency` desde el texto crudo en el borde; BSD-3-Clause). [VERIFIED NEXT-LEVEL.md:587 Pydantic; :530 pycountry; :506/:216 price-parser]

#### Resolución condensada — Faceta 11
- **Costura** · No existe CanonicalVehicle ni CONTRACT_VERSION: cada conector define su propia dataclass Vehicle consumida por duck-typing (ingest.py:96-101 lee campo-a-campo). Divergencias reales [VERIFIED]: AS24.Vehicle usa vin_ref (autoscout24.py:40-52, sin currency/codes); coches_net.Vehicle usa listing_ref + price_drop (coches_net_wholesale.py:163-177); coches_com.Vehicle anade segment + listing_url (coches_com_wholesale.py:409-425). Falta la dimension currency (price float pelado) y codigos neutrales (fuel/transmission verbatim).
- **Fix** · Definir un dataclass CanonicalVehicle{deep_link, source_ref, title, make, model, year, km, price, currency, fuel_code, transmission_code, photo_url, raw_locale_fields} con CONTRACT_VERSION; unificar vin_ref/listing_ref en source_ref; mover price_drop/segment/listing_url a un campo extra:dict o promoverlos al contrato; poblar currency con price-parser en el borde y validarlo con pycountry(ISO 4217); preservar el string original en raw_locale_fields; modelar el contrato como Pydantic BaseModel y anadir test CI estructural por conector.
- **Adversarial** · CRITICAL currency ausente: coche JP 5.000.000 JPY (~30k EUR) indistinguible de 5M EUR en columna price desnuda; MXN 350.000 parece 350k EUR -> corrupcion cross-pais total e invisible. Conector PT/IT/FR que omita un campo o lo nombre distinto pasa el harness (cuenta filas) pero rompe ingest a escala. Sin CONTRACT_VERSION no hay deteccion de drift de forma (coches.com.segment vs AS24).
- **Sellado (multi-vía)** · Sello: un CanonicalVehicle unico con CONTRACT_VERSION + todo conector emite la forma exacta + currency ISO 4217 poblado + raw_locale_fields preserva original. Multi-via: (1) test: cada conector valida contra el esquema Pydantic, campo faltante/mal-nombrado = ROJO; (2) adversarial: conector que omite currency FALLA el build (fail-closed); (3) via independiente: currency de price-parser (texto) se cruza contra priceCurrency del JSON-LD (metadato) -> concordancia o REFUTED.
- **Herramienta NEXT-LEVEL (€0)** · Pydantic (Guard de drift como CONTRATO TIPADO en CI) — MIT, EUR0 — https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]. Complementos: pycountry (ISO 4217/3166-2, LGPL-2.1, build-time) https://github.com/pycountry/pycountry [VERIFIED :530]; price-parser (poblar currency en el borde, BSD-3-Clause) https://github.com/scrapinghub/price-parser [VERIFIED :506,:216].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-12"></a>

### Faceta 12 — Dimensión MONEDA (`currency`) extremo-a-extremo

> **F2 · CURRENCY absent — CRITICAL.** `price` float desnudo; la divisa se ve en la fuente y se TIRA. B3·B6·MP1·MP2·SH2. **Cross-ref:** facetas [11](#faceta-11)·[15](#faceta-15)·[14](#faceta-14)·[26](#faceta-26).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/recipe_extract_web.py:76-83` [VERIFIED] `vehicles_from_jsonld`: lee `offers.get("price")` (:79 dict / :81 lista) pero el `out.append({"name":..., "price":price, "url":..., "type":...})` (:82-83) **NO incluye `priceCurrency`** — la divisa del JSON-LD schema.org se DESCARTA en la captura.
- `pipeline/recipe_extract_web.py:104-105` [VERIFIED] rung microdata: `price = (pm.group(1) or pm.group(2))` con regex `[\d.,]+` (:104) — string crudo, SIN parser EU y SIN divisa.
- `pipeline/sources/autoscout24.py:40-52` [VERIFIED] dataclass `Vehicle`: `price: float | None` (:49) — **no existe campo currency** en la forma de salida.
- `pipeline/platform/coches_com_wholesale.py:367-373` [VERIFIED] `parse_card_vehicle` toma solo `price_obj.get("amount")` (:368); el docstring del field_map en `:880` dice literalmente `"price": "card.price.amount (card.price.currency)"` -> **la fuente EXPONE `card.price.currency` y el parser solo coge `amount`**; el `Vehicle` construido (:409-424) no lleva currency.
- `pipeline/platform/coches_net_wholesale.py:268-277` [VERIFIED] `Vehicle` build: `price=price` (:272), sin currency.
- **Matiz del grep [VERIFIED, corrige el hint]**: el hint dice "grep pipeline/ = 0 capturas de priceCurrency/currency". Literalmente NO es cero: `currency` aparece en 36 ficheros — pero TODAS son docstrings/notas de field_map, NUNCA una escritura al dataclass de salida: `oem_audi_wholesale.py:282` (`currencyCode`), `oem_ford_wholesale.py:559` (`currency EUR`), `oem_toyota_lexus_wholesale.py:484` (`currencyCode=EUR`), `oem_volvo_jlr_suzuki_wholesale.py:158` (`currencyCode`), `carandclassic_wholesale.py:15` (`price{value(cents),currency}`), `family_cms_wordpress_dominated__wholesale.py:226,507`. **Conclusion exacta: CERO parsers capturan currency al contrato; varios la VEN en la fuente y la TIRAN.** Esto refuerza la tesis (el dato esta, la capa de captura lo descarta).

#### (b) El mecanismo al atomo
Cada `Vehicle` del proyecto tiene `price: float|None` desnudo. El precio nace en 3 formas: (1) estructurado numerico (`card.price.amount`, `offers.price`), (2) texto microdata (`'24.900'`), (3) campo de OEM con `currencyCode` explicito. En las 3, la divisa o no se lee o se lee y se descarta. Aguas abajo, `ingest.py:100-101` inserta `price_clean` en la columna `vehicle.price` sin columna acompañante de moneda. El resultado: la columna `price` es un escalar adimensional. Toda operacion sobre ella — orden, comparacion `+/-2%` (Signal-B PRICE_CHANGE), techo `PRICE_MAX=5_000_000` ([faceta 15](#faceta-15)) — asume implicitamente EUR. El acoplamiento con la [faceta 15](#faceta-15) es directo: el ceiling es un escalar EUR aplicado a una columna que, en cuanto entra un segundo pais, mezcla unidades.

#### (c) Costura ES->generico
La dimension #1 ausente. El fix es un cambio de CONTRATO, no un dict: (1) anadir `currency_code` (ISO 4217) a `CanonicalVehicle` ([faceta 11](#faceta-11)) con `CONTRACT_VERSION` bump; (2) CAPTURAR la divisa en el borde — `recipe_extract_web.py:79` debe leer `offers.get("priceCurrency")`, y los OEM que ya ven `currencyCode` deben escribirla; (3) default de divisa por pais desde `LocaleProfile.currency` ([faceta 13](#faceta-13)) cuando la fuente no la declara; (4) propagar hasta el almacen con columna `currency` y backfill ES=EUR; (5) la [faceta 15](#faceta-15) (ceiling) y la comparacion Signal-B pasan a currency-aware (misma divisa en la block-key).

#### (d) Riesgo adversarial concreto — CRITICAL
- **JP**: un coche de `5.000.000 JPY` (~30k EUR) es INDISTINGUIBLE de `5M EUR` en la columna compartida; ademas supera `PRICE_MAX` EUR=5M y `sanitize_price` lo NULea (perdida masiva de mercado JP legitimo, acopla [faceta 15](#faceta-15)).
- **MX**: `MXN 350.000` (~18k EUR) aparece como `350k EUR`.
- **UK/GBP**: `8000 GBP ~ 8000 EUR` pasaria el `+/-2%` Signal-B como "sin cambio" -> falso UNCHANGED cross-divisa [VERIFIED NEXT-LEVEL.md:504].
- **Invisibilidad**: ninguno crashea; todos producen floats validos que pasan sanity -> corrupcion cross-pais total y SILENCIOSA.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (golden currency-tagged)**: `parse_money('MX 1,234.56')==1234.56` con `currency='MXN'`; `'JP ¥1,234,000'==1234000` con `currency='JPY'`.
- **Via 2 (invariante de block-key)**: ningun bloque Signal-B mezcla dos divisas -> colision GBP/EUR +/-2% estructuralmente imposible.
- **Via 3 (techo por-divisa)**: un precio JPY normal SOBREVIVE `sanitize_price` bajo el techo JPY, mientras el junk EUR sigue rechazado.
- **Via 4 (cross-check ortogonal)**: el `amount` parseado del texto visible vs el `priceCurrency` del JSON-LD (que `recipe_extract_web.py:79` hoy descarta) — dos familias (texto vs metadato schema.org) deben concordar o se marca REFUTED.
- **Sello DB**: una vez un pais se sella, `currency` NOT NULL es invariante (constraint).

#### (f) Herramienta NEXT-LEVEL
`locale-money-correctness` / `Currency-correct pricing` -> **price-parser** (BSD-3-Clause) [VERIFIED NEXT-LEVEL.md:213-219 y 503-509] https://github.com/scrapinghub/price-parser — extrae monto + simbolo/codigo de divisa IN-BAND del texto crudo, manejando separador miles/decimal por locale. Respaldo: **Babel** (CLDR number/currency/date por locale, BSD-3-Clause), **py-moneyed** (Money+Currency tipado para aritmetica segura), **pycountry** (ISO 4217 authority + default por pais, LGPL-2.1) [VERIFIED NEXT-LEVEL.md:530]. Es la corona porque captura la divisa en el borde (no la atornilla despues) y mata a la vez la corrupcion 1000x ([faceta 14](#faceta-14)) y el ceiling EUR-ciego ([faceta 15](#faceta-15)). €0, CPU puro, CLDR embebido en Babel (sin servicio FX: las comparaciones son intra-divisa por construccion).

#### Resolución condensada — Faceta 12
- **Costura** · price es float desnudo en TODO Vehicle (autoscout24.py:49) y en la columna vehicle.price (ingest.py:100-101), sin dimension de moneda. La divisa existe en la fuente pero se descarta: recipe_extract_web.py:79-83 lee offers.get('price') y NO captura priceCurrency; coches_com:880 documenta card.price.currency pero parse (:368) solo coge amount; los OEM (oem_audi:282, oem_ford:559, oem_toyota:484) ven currencyCode y no lo escriben. CERO parsers capturan currency al contrato.
- **Fix** · Cambio de CONTRATO: anadir currency_code (ISO 4217) a CanonicalVehicle ([faceta 11](#faceta-11)) con CONTRACT_VERSION bump; capturar priceCurrency en recipe_extract_web.py:79 y en los OEM que ya lo ven; default de divisa por pais desde LocaleProfile.currency ([faceta 13](#faceta-13)); propagar a columna currency en almacen con backfill ES=EUR; volver currency-aware el ceiling ([faceta 15](#faceta-15)) y la comparacion Signal-B (misma divisa en la block-key). Enrutar TODO precio-texto (incl. microdata recipe_extract_web.py:104) por price-parser.
- **Adversarial** · CRITICAL: JP 5.000.000 JPY (~30k EUR) indistinguible de 5M EUR en la columna compartida y ademas NULeado por PRICE_MAX EUR=5M (perdida de mercado JP legitimo); MXN 350.000 (~18k EUR) parece 350k EUR; 8000 GBP ~ 8000 EUR pasa el +/-2% Signal-B como UNCHANGED falso. Ninguno crashea: floats validos que pasan sanity -> corrupcion cross-pais total e INVISIBLE.
- **Sellado (multi-vía)** · Via1 golden currency-tagged (parse_money('MX 1,234.56')==1234.56 currency=MXN; '¥1,234,000'==1234000 currency=JPY); Via2 invariante block-key: ningun bloque Signal-B mezcla 2 divisas (colision GBP/EUR imposible); Via3 techo por-divisa: JPY normal sobrevive sanitize_price bajo techo JPY, junk EUR sigue rechazado; Via4 cross-check del amount-texto vs priceCurrency-JSON-LD (hoy descartado en :79) -> concordancia o REFUTED; DB constraint currency NOT NULL una vez sellado el pais.
- **Herramienta NEXT-LEVEL (€0)** · locale-money-correctness/Currency-correct pricing -> price-parser (BSD-3-Clause) https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216,506]; respaldo Babel (CLDR, BSD-3), py-moneyed (Money tipado), pycountry (ISO 4217 + default por pais, LGPL-2.1, NEXT-LEVEL.md:530). Captura divisa in-band en el borde; mata corrupcion 1000x ([faceta 14](#faceta-14)) y ceiling EUR-ciego ([faceta 15](#faceta-15)). €0 CPU, sin servicio FX (comparaciones intra-divisa por construccion).

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-13"></a>

### Faceta 13 — Orquestador `normalize_vehicle` + objeto `LocaleProfile`

> **Plano C — pieza-llave.** Normalización dispersa inline en `ingest.py`; `LocaleProfile` NO existe (grep 0). **Cross-ref:** facetas [14](#faceta-14)·[20](#faceta-20)·[16](#faceta-16)·[15](#faceta-15)·[17](#faceta-17)·[18](#faceta-18)·[19](#faceta-19).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/ingest.py:83-95` [VERIFIED]: la normalizacion vive **dispersa e inline en el bucle** `ingest_dealer`, sin orquestador. `:83` `price_clean = sanitize_price(v.price)`; `:84` `km_clean = sanitize_km(v.km)`; `:85` `year_clean = sanitize_year(v.year)`; `:88` `year_clean, km_clean = sanitize_year_km(...)`; `:95` `make_norm = normalize_make(v.make, v.title)`. Son **5 llamadas sueltas** en el borde; `fuel`/`transmission` se insertan **verbatim** (`:101` `v.fuel, v.transmission`), y **no hay currency** en absoluto.
- `pipeline/recipe.py:6` [VERIFIED] docstring "the country is derived from the cdp_code; **defaults to ES**"; `:20` `AS24_RECIPE` con `field_map` ES.
- `pipeline/identity/make_normalizer.py:9-13` [VERIFIED] `_CANON` "grounded in the **LIVE data** (top ~70 leading tokens ... 2026-06-15)"; `:19-40` tabla **solo latina** (~70 marcas).
- `pipeline/price_sanity.py:49` [VERIFIED] `PRICE_MAX = 5_000_000` — constante de **modulo, implicito-universal**, sin parametro de pais/moneda; aplicada plana en `sanitize_price` `:56-66`.
- **Ausencia confirmada:** grep `LocaleProfile` en `pipeline/` = **0 hits** [VERIFIED] — el objeto-pais NO existe todavia; es el hueco a construir.

#### (b) El mecanismo al atomo
Hoy el "motor" de normalizacion = N funciones independientes invocadas a mano en el borde de ingest:
- `sanitize_price/km/year/year_km` (fisica + sentinelas, `price_sanity.py`) — bounds **universales hardcodeados** (5M / 1.5M / 1900..now+1).
- `normalize_make` (algoritmo canon→titulo→verbatim + `_CANON` ES).
- `fuel`/`transmission` sin tocar.
El borde decide el orden y que se aplica; cada conector que no pase por `ingest.py` (parsers que sanitizan inline, [faceta 16](#faceta-16)) **diverge**. No hay un punto unico ni un objeto que parametrice el pais.

**360 — la pieza-llave del Plano-C:** UNA funcion `normalize_vehicle(raw_fields, profile: LocaleProfile) -> CanonicalVehicle` que concentra TODO (parse_money, parse_date, gates fisicos, make/fuel/transmission canon, postcode→region crudo) y delega en `profile`. `LocaleProfile{decimal_sep, thousand_sep, currency, date_fmt, price_max, stock_hints, count_words, marketplace_blocklist, fuel_map, transmission_map, brand_table, postcode_to_region}` es el **unico objeto-pais**; ES se reifica como `countries/ES/locale.yaml` (pack #1). Los parsers dejan de inlinear y DELEGAN.

#### (c) La costura ES→generico + fix exacto
- **Fix estructural:** crear `pipeline/normalize.py::normalize_vehicle(raw, profile)` y `LocaleProfile` (dataclass versionada). `ingest.py:83-95` pasa de 5 llamadas sueltas a `cv = normalize_vehicle(raw, profile)` con `profile = load_locale(country_of_cdp(code))`.
- **Fix bounds:** `PRICE_MAX` deja de ser constante de modulo y pasa a `profile.price_max` en **unidades de moneda local** ([faceta 15](#faceta-15)); `KM_MAX`/`YEAR_MIN` se mantienen universales pero re-verificados ([faceta 16](#faceta-16)).
- **Fix make:** separar ALGORITMO (motor) de TABLA (`profile.brand_table`); `_CANON` ES se vuelve `countries/ES/brands.yaml`.
- **Reificacion honesta:** al extraer ES a pack hay que **re-muestrear su distribucion**, no copiar las constantes "grounded in LIVE ES" como si fueran universales (riesgo de sesgo ES disfrazado de motor).
- **Migracion downstream:** centralizar bounds **cambia valores ya servidos en ES** → requiere dry-run + recompute auditado para no disparar deltas espurios.

#### (d) Riesgo adversarial concreto
- **Regresion ES por migracion:** un `km` que hoy pasa el gate inline 5M ([faceta 16](#faceta-16)) y manana pasa a `KM_MAX=1.5M` cambia de valor → **KM_CHANGE espurios** en delta si no se migra con dry-run + recompute.
- **Sesgo ES oculto:** reificar `_CANON`/`PRICE_MAX` "LIVE ES" a `locale.yaml` sin re-muestrear reintroduce la distribucion ES como si fuera neutral → el pais #2 hereda umbrales calibrados a otro mercado.
- **DE/FR/IT/PT:** sin `LocaleProfile`, el pais entra como **rama de codigo** (cada gate/tabla parcheado), justo lo que el motor generico prohibe; la incoherencia 5M-EUR-vs-techo-local persiste.
- **currency:** la propia ausencia de `currency` en el contrato ([faceta 12](#faceta-12)) hace que el orquestador, aunque centralice, siga sirviendo `price` desnudo si no se anade la dimension.

#### (e) Criterio de sellado + verificacion multi-via
- **Sellado:** existe `normalize_vehicle` como **unico** punto de normalizacion; `LocaleProfile` carga desde `countries/<CC>/locale.yaml`; ES = pack #1 reificado; cero gate/tabla inline fuera del orquestador ([faceta 16](#faceta-16) absorbida).
- **Via 1 (golden ES byte-identico):** `normalize_vehicle(raw, load_locale("ES"))` produce el MISMO `CanonicalVehicle` que las 5 llamadas sueltas de hoy sobre fixtures ES.
- **Via 2 (dry-run de migracion):** recompute sobre el corpus vivo ES con conteo de deltas inducidos = 0 (o auditados uno a uno) antes de cortar.
- **Via 3 (contrato de pack):** el `locale.yaml` se valida contra un Table Schema (Frictionless) en bootstrap — un pack mal formado (separador faltante, currency invalida ISO 4217) **falla cerrado** antes de cargar.
- **Via 4 (property-based):** Hypothesis genera locales sinteticos y afirma invariantes (`km>=0|None`, `parse_money` idempotente, `make ∈ brand_table∪verbatim`).

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
- **Primaria — Frictionless Framework** (Country-pack como CONTRATO de datos auto-verificado, NEXT-LEVEL.md:334-340 [VERIFIED]): declara `LocaleProfile`/`locale.yaml` como un **Table Schema versionado** (tipos, regex de forma, ancho de codigo, bbox de centroides) validado en CI y bootstrap ANTES de cargar una fila — aplica la doctrina COUNTRY-PROOF ("que la maquina imponga la regla y la pruebe sola") a la ingesta del pack, convirtiendo el objeto-pais en un contrato ejecutable en vez de un dataclass que se confia. **MIT, €0 — https://github.com/frictionlessdata/frictionless-py** [VERIFIED NEXT-LEVEL.md:337].
- **Acoplada — pycountry** (ISO 3166-2 + ISO 4217 authority, NEXT-LEVEL.md:527-533 [VERIFIED]): surte a `LocaleProfile` el **currency default por pais (ISO 4217)** y la **rejilla de subdivisiones (ISO 3166-2)** como DATO autoritativo, retirando los sentinelas ES (cap 52, CHAR(2)); usado en config-time (no hot path) → la LGPL-2.1 es no-issue, o se usa el `iso3166` MIT + iso-codes JSON para estricta-permisiva. **LGPL-2.1, €0 — https://github.com/pycountry/pycountry** [VERIFIED NEXT-LEVEL.md:530].

#### Resolución condensada — Faceta 13
- **Costura** · La normalizacion vive dispersa e inline en pipeline/ingest.py:83-95 (sanitize_price/km/year/year_km + normalize_make sueltos; fuel/transmission verbatim; cero currency), sin orquestador; PRICE_MAX (price_sanity.py:49) es constante de modulo implicito-universal; _CANON (make_normalizer.py:9-13) 'grounded in LIVE ES'; recipe.py:6 'defaults to ES'. LocaleProfile NO existe (grep 0 hits). Costura = UNA funcion normalize_vehicle(raw, LocaleProfile) que concentra todo y un solo objeto-pais.
- **Fix** · Crear pipeline/normalize.py::normalize_vehicle(raw, profile) + dataclass LocaleProfile{decimal_sep,thousand_sep,currency,date_fmt,price_max,stock_hints,count_words,marketplace_blocklist,fuel_map,transmission_map,brand_table,postcode_to_region}; ingest.py:83-95 pasa de 5 llamadas sueltas a cv=normalize_vehicle(raw, load_locale(country_of_cdp(code))); PRICE_MAX->profile.price_max en moneda local; _CANON->countries/ES/brands.yaml; reificar ES re-muestreando su distribucion (no copiar constantes LIVE-ES como universales); migrar con dry-run+recompute auditado.
- **Adversarial** · Centralizar bounds CAMBIA km ya servidos en ES (5M inline -> 1.5M canonico) -> KM_CHANGE espurios en delta sin dry-run; reificar _CANON/PRICE_MAX 'LIVE ES' a pack sin re-muestrear reintroduce sesgo ES disfrazado de motor para el pais #2; sin LocaleProfile el pais entra como rama de codigo (cada gate/tabla parcheado), no como datos; la ausencia de currency ([faceta 12](#faceta-12)) hace que aun centralizado se sirva price desnudo.
- **Sellado (multi-vía)** · Sellado: normalize_vehicle es el UNICO punto de normalizacion; LocaleProfile carga de countries/<CC>/locale.yaml; ES=pack#1; cero gate/tabla inline fuera del orquestador. Verificacion: (1) golden ES byte-identico vs las 5 llamadas de hoy; (2) dry-run de migracion con deltas inducidos=0 o auditados; (3) contrato Frictionless del locale.yaml falla-cerrado en bootstrap; (4) property-based Hypothesis sobre invariantes (km>=0|None, parse_money idempotente, make in brand_table union verbatim).
- **Herramienta NEXT-LEVEL (€0)** · PRIMARIA: Frictionless Framework (Country-pack como CONTRATO auto-verificado, NEXT-LEVEL.md:334-340) — Table Schema versionado que valida LocaleProfile/locale.yaml en CI+bootstrap ANTES del INSERT (doctrina COUNTRY-PROOF), MIT, EUR0 — https://github.com/frictionlessdata/frictionless-py [VERIFIED :337]. ACOPLADA: pycountry (ISO 3166-2 + ISO 4217, :527-533) surte currency-default (4217) y rejilla de subdivisiones (3166-2) como dato autoritativo, retira sentinelas ES; config-time (LGPL-2.1 no-issue) — https://github.com/pycountry/pycountry [VERIFIED :530].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-14"></a>

### Faceta 14 — Motor `parse_money` / formato numérico (rebuild de corrección)

> **F3 · NUMBER parse corruption.** ~31 `_to_float` EU divergentes; `'1,234.56'`→1.23456, `'24.900'`→24.9 (ya sirviéndose en ES). B5·MP8. **Cross-ref:** facetas [12](#faceta-12)·[15](#faceta-15)·[6](#faceta-6).

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/platform/dealerprobe.py:119-134` `_to_float`** [VERIFIED]: `s = re.sub(r"[^\d,.]", "", str(v))` (:124); rama both-present `if "," in s and "." in s: s = s.replace(".", "").replace(",", ".")` con comentario "1.234,56 -> 1234.56 (EU thousands+decimal)" (:127-128); rama solo-coma (:129-130). CONFIRMADO asume convencion EU. **Defecto critico [VERIFIED]**: NO existe rama para dot-only-thousands "24.900" -> cae a `float("24.900")` = **24.9**; y MX/US "1,234.56" (both present) -> `"1,23456"` -> `"1.23456"` = **1.23456** (~1000x infra-lectura, float valido). Cero captura de moneda.
- **`pipeline/recipe_extract_web.py:104-105`** [VERIFIED]: `pm = re.search(r'itemprop="price"[^>]*(?:content="([^"]+)"|>\s*([\d.,]+))', block)` y `price = (pm.group(1) or pm.group(2))` -> el precio se guarda como **STRING crudo** (:108 `out.append({... "price": price ...})`), SIN parser EU en el rung. El hint es exacto. Adicional [VERIFIED [faceta 12](#faceta-12)]: el rung JSON-LD (:79) DESCARTA `priceCurrency`.
- **Dispersion [VERIFIED por grep, PEOR que el hint]**: el hint dice "12 modulos replace + 22 defs". Realidad: **7 ficheros** con la cadena EXACTA `.replace('.','').replace(',','.')` (`subastacar_wholesale`, `dealerprobe`, `oem_seat_cupra_wholesale`, `oem_kia_wholesale`, `group_vo_chains_wholesale`, `oem_seat_cupra_new_stock`, `generic_dealer_site`), y **~31 defs de parser float-money** (`_to_float`/`_num`/`_price_to_float`) repartidas en ~40 modulos `platform/`+`sources/` (mas decenas de `_to_int`). `family_dealerk_wholesale.py:136` y `family_cms_wordpress_dominated__wholesale.py:149` definen su `_price_to_float`; `oem_mercedes_benz_wholesale.py:193` define `_num`. La fragmentacion es estructural.

#### (b) El mecanismo al atomo
text->numero hoy = N implementaciones aisladas; cada conector reinvento la rueda. El "mejor" (`dealerprobe._to_float`) discrimina por presencia de `,` y `.` tras un strip de no-[digito,coma,punto]. Falla en: (1) **dot-only-thousands EU** "24.900" -> 24.9; (2) **convencion invertida MX/US/JP** "1,234.56" -> 1.23456; (3) **espacio/NBSP FR** "1 234,56" (el `\xa0` NBSP puede sobrevivir el strip segun el modulo). El rung web ni siquiera parsea: emite la string cruda (`recipe_extract_web.py:108`) y delega un `float()` ciego aguas abajo, donde Python lee "24.900" como 24.9. **No existe captura de moneda en ningun parser** ([faceta 12](#faceta-12)). Resultado en todos los casos: un float VALIDO que pasa `sanitize_price` sin alerta — corrupcion silenciosa indetectable por los gates actuales.

#### (c) La costura ES->generico y su fix exacto
La costura es triple: (1) convencion numerica EU hardcodeada en ~31 `_to_float` ad-hoc; (2) moneda AUSENTE en todo el pipeline; (3) el rung web/microdata sin parser alguno.
**Fix exacto — UNA `parse_money(text, LocaleProfile) -> (Decimal amount, str currency_code)`:**
- `decimal_sep`/`thousand_sep` vienen del `LocaleProfile` (datos del pack, NO heuristica fragil de "ambos presentes").
- detecta simbolo/codigo de divisa in-band (€/¥/$/£, EUR/JPY/MXN) y si falta usa `LocaleProfile.currency` default.
- enruta TODO precio-texto por ella: `recipe_extract_web.py:104` (microdata) + el rung JSON-LD (capturando el `priceCurrency` que :79 hoy tira) + los conectores, y **borra** las ~31 `_to_float`/`_num`/`_price_to_float` divergentes.
- emite `Decimal` currency-tagged (no `float`) para no reintroducir el error binario.
Es un **REBUILD de correccion data-driven (CLDR)**, no un swap de separador.

#### (d) El riesgo adversarial concreto
- **MX/US "1,234.56"** -> bajo parser EU -> **1.23456** (CRITICAL ~1000x infra-lectura; float valido; pasa PRICE_MAX y sanity sin alerta).
- **ES dot-only "24.900"** -> **24.9** (DANO LATENTE YA SIRVIENDOSE en el rung web ES — auditar antes de declarar ES sellado).
- **FR "1 234,56" / NBSP** -> el espacio/NBSP rompe el strip segun el modulo; resultado None o 1234.56 por azar.
- **JP "¥1,234,000"** -> parser EU (both present) -> `replace('.','')` no-op, `replace(',','.')` -> "1.234.000" -> `float()` falla o ValueError->None; y sin currency, 1.234.000 JPY (~7.5k EUR) entra en la columna `price` desnuda indistinguible de EUR.
- **Ruido** "Consultar"/"-"/"P.O.A." -> cada `_to_float` lo trata distinto (None vs 0 vs crash), divergencia entre conectores.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** (i) existe UNA `parse_money`; `grep` de `_to_float`/`_num`/`_price_to_float` residual fuera del modulo canonico == 0; (ii) toda string-precio (incluidos web/microdata/JSON-LD) pasa por ella; (iii) `currency_code` poblado en el contrato CanonicalVehicle.
**Multi-via:** (1) **golden por locale** — `'MX 1,234.56'==1234.56`, `'ES 1.234,56'==1234.56`, `'ES 24.900'==24900`, `'FR 1 234,56'==1234.56`, `'JP ¥1,234,000'==1234000`, con currency capturada; (2) **adversarial Hypothesis** — separadores mixtos/ambiguos, invariante "parse_money idempotente ∧ nunca off-by-1000"; (3) **via independiente** — monto parseado del texto visible vs `priceCurrency`/`price` del JSON-LD (dos familias: visible vs metadato schema.org) deben concordar o se marca REFUTED.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **Primaria: price-parser** (BSD-3-Clause, €0) — https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216 y :506]. Extrae monto + simbolo/codigo de divisa de texto crudo y maneja separador de miles/decimal por locale.
- **Respaldo: Babel** (CLDR: number/currency/date por pais) y **py-moneyed** (Money+Currency tipado, aritmetica segura) [VERIFIED NEXT-LEVEL.md:217/:507]. CPU puro, offline (CLDR bundled con Babel), licencias BSD/permisivas comercial-limpias. El `LocaleProfile` del pack aporta currency default + overrides; price-parser detecta la divisa in-band y Babel valida el formato. Mata de un golpe la corrupcion 1000x y la dimension-moneda ausente — es cambio de contrato, no un dict.

#### Resolución condensada — Faceta 14
- **Costura** · Triple costura: (1) la convencion numerica EU esta hardcodeada en ~31 _to_float ad-hoc — dealerprobe.py:127-128 hace replace('.','').replace(',','.') asumiendo EU y NO tiene rama para dot-only-thousands; (2) la moneda esta AUSENTE de todo el pipeline (ningun parser captura priceCurrency; recipe_extract_web.py:79 lo DESCARTA); (3) el rung web/microdata (recipe_extract_web.py:104-105) emite la string de precio cruda SIN parser, delegando un float() ciego aguas abajo que lee '24.900' como 24.9.
- **Fix** · UNA parse_money(text, LocaleProfile)->(Decimal amount, str currency_code): decimal_sep/thousand_sep del pack (no heuristica de 'ambos presentes'), divisa detectada in-band con default del LocaleProfile, Decimal currency-tagged (no float). Enrutar TODO precio-texto por ella — incluido recipe_extract_web.py:104 (microdata) y el rung JSON-LD capturando el priceCurrency que :79 hoy tira — y BORRAR las ~31 _to_float/_num/_price_to_float divergentes (7 de ellas con la cadena exacta replace('.','').replace(',','.')). Es un rebuild data-driven CLDR, no un swap de separador.
- **Adversarial** · CRITICAL MX/US '1,234.56' -> bajo parser EU -> 1.23456 (~1000x infra-lectura, float valido, pasa PRICE_MAX y sanity sin alerta). ES dot-only '24.900' -> 24.9, DANO LATENTE ya sirviendose en el rung web ES (auditar antes de declarar ES sellado). FR '1 234,56'/NBSP rompe el strip (None o 1234.56 por azar). JP '¥1,234,000' da None bajo el parser EU y, sin currency, 1.234.000 JPY (~7.5k EUR) es indistinguible de EUR en la columna price desnuda. Ruido 'Consultar'/'-'/'P.O.A.' tratado distinto por cada _to_float (None/0/crash).
- **Sellado (multi-vía)** · (i) Existe UNA parse_money; grep de _to_float/_num/_price_to_float residual fuera del modulo canonico == 0. (ii) Toda string-precio (web/microdata/JSON-LD incluidos) enrutada por ella. (iii) currency_code poblado en el contrato CanonicalVehicle. Multi-via: (a) golden por locale 'MX 1,234.56'==1234.56, 'ES 1.234,56'==1234.56, 'ES 24.900'==24900, 'FR 1 234,56'==1234.56, 'JP ¥1,234,000'==1234000 con currency; (b) Hypothesis 'idempotente ∧ nunca off-by-1000'; (c) cross-check determinista del monto del texto visible contra el priceCurrency/price del JSON-LD (concordancia o REFUTED).
- **Herramienta NEXT-LEVEL (€0)** · price-parser (BSD-3-Clause, €0) https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216 y :506] — extrae monto + simbolo/codigo de divisa de texto crudo, separador de miles/decimal por locale. Respaldo: Babel (CLDR number/currency/date por pais) + py-moneyed (Money+Currency tipado) [VERIFIED NEXT-LEVEL.md:217/:507]. CPU puro, offline (CLDR bundled con Babel), licencias BSD/permisivas comercial-limpias. El LocaleProfile aporta currency default+overrides; price-parser detecta la divisa in-band y Babel valida el formato. Mata la corrupcion 1000x y la dimension-moneda ausente.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-15"></a>

### Faceta 15 — Calibración del techo de precio (`PRICE_MAX`) currency-aware

> **F4 · PRICE ceiling EUR-bound.** `PRICE_MAX=5_000_000` EUR sobre un `price` sin moneda. B2·MP2. **Cross-ref:** facetas [12](#faceta-12)·[14](#faceta-14)·[11](#faceta-11).

#### (a) Code_hints [VERIFIED]
- `pipeline/price_sanity.py:1-42` docstring del modulo: calibrado a escala EUR (Bugatti Chiron ~3.6M EUR; sentinela all-9s 9.99M/10M EUR de Wallapop/ES) [VERIFIED].
- `:47-49` `PRICE_MAX = 5_000_000` (comentario `:47-48`, valor en linea `49`) [VERIFIED].
- `:56-66` `sanitize_price`: devuelve None si price es None, no-float, o `p <= 0 or p > PRICE_MAX` (`:64`); si no, devuelve price sin tocar [VERIFIED].
- `pipeline/ingest.py:83` `price_clean = sanitize_price(v.price)` [VERIFIED].
- `pipeline/sources/autoscout24.py:49` `price: float | None` — `Vehicle` SIN campo currency [VERIFIED]; AS24 NO llama sanitize_price inline (el techo se aplica en ingest.py:83); km inline en `:179`, year en `:189`.
- Hint: tambien llamado inline en coches_net:248, coches_com:373, autocasion:241 [ASSUMED desde hint, no re-leido en esta pasada — consistente con el patron de ingest].

#### (b) Mecanismo al atomo
`sanitize_price` es un gate escalar plano: UNA constante de modulo `PRICE_MAX=5_000_000` comparada contra un `float` price pelado. El float NO lleva moneda. El numero 5.000.000 solo es significativo en EUR (queda por encima del techo hypercar real ~3.6M EUR y por debajo del sentinela 9.99M/10M EUR). El gate corre en ingest.py:83 (y inline en 3 parsers) — el MISMO escalar aplicado a cada fila sin importar pais/moneda. La logica del sentinela 9.99M es un artefacto ES (Wallapop 'all-9s price-on-request').

#### (c) Costura ES->generico
La costura es el ESCALAR currency-acoplado. `PRICE_MAX` es una magnitud EUR pelada viviendo como constante de modulo; price no tiene dimension moneda ([faceta 12](#faceta-12) = currency ausente). Para ir generico: (1) la moneda debe entrar al contrato (price_currency capturado en extraccion, default por LocaleProfile.currency); (2) el techo debe ser per-moneda (LocaleProfile.price_max) o FX-normalizado antes del gate; (3) `sanitize_price` debe tomar la moneda/perfil, no una constante global. El sentinela 9.99M se mueve al pack ES (countries/ES/locale.yaml) como artefacto ES-only, no universal.

#### (d) Riesgo adversarial concreto
CRITICAL en JPY: un SUV/furgon/coche de lujo rutinario supera 5.000.000 JPY (~30k EUR) -> `sanitize_price` NULea una fraccion enorme del mercado JP legitimo; el sentinela 9.99M no existe en JPY. Un swap escalar ingenuo (5M->100M) sin currency-awareness sigue roto porque la columna 'price' mezcla monedas. MXN 350.000 (~18k EUR) leido como 350k EUR pasa el gate pero es semanticamente erroneo ([faceta 12](#faceta-12)). El techo cambia de significado en cuanto una segunda moneda comparte la columna.

#### (e) Sellado + verificacion multi-via
Criterio: cada precio lleva moneda explicita desde captura hasta sello; el techo se evalua en la moneda propia del precio contra un `price_max` pack-calibrado derivado de la distribucion real del mercado de ocasion del pais (no un escalar adivinado). Multi-via: (1) golden per-moneda — un precio JPY normal SOBREVIVE `sanitize_price` bajo el techo JPY (fixture B3 verde) mientras EUR junk (>5M EUR) se sigue NULeando; (2) regresion ES — el techo 5M EUR NULea exactamente las mismas filas que hoy (byte-identico, cero drift en la served-surface); (3) cross-check del monto parseado vs `priceCurrency` de JSON-LD (recipe_extract_web.py:79 hoy lo DESCARTA) — dos familias (texto visible vs metadato schema.org) deben concordar en moneda o REFUTED; (4) propiedad Hypothesis: `sanitize_price` idempotente y nunca NULea un precio legitimo in-band para ninguna (moneda, magnitud) que el pack declare.

#### (f) Herramienta NEXT-LEVEL
price-parser, BSD-3-Clause, https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216 y :506]. Extrae monto + simbolo/codigo de moneda del texto crudo, manejando separadores de miles/decimal por locale; respaldado por Babel (CLDR) para formatos numero/moneda por locale y py-moneyed para aritmetica currency-safe y un PRICE_MAX per-moneda en el CountryProfile. CPU puro, offline (CLDR embebido en Babel), sin servicio FX (las comparaciones son intra-moneda por construccion, moneda en la block-key). Es la frontera currency-aware que hace `PRICE_MAX` self-describing por mercado en vez de una magnitud EUR hardcodeada. Alternativas: Babel, py-moneyed, moneyparser.

#### Resolución condensada — Faceta 15
- **Costura** · El escalar currency-acoplado: PRICE_MAX=5_000_000 (price_sanity.py:49) es una magnitud EUR pelada como constante de modulo, comparada (sanitize_price :64) contra un float price SIN moneda (autoscout24.py:49 price:float|None, sin currency). El sentinela 9.99M es artefacto ES. El mismo escalar corre en ingest.py:83 para toda fila sin importar pais.
- **Fix** · price_sanity.py: cambiar PRICE_MAX de constante de modulo a campo leido de LocaleProfile (profile.price_max). Cambiar sanitize_price(price)->sanitize_price(price, currency, profile): resolver el techo para 'currency' (profile.price_max[currency]) y comparar in-currency. Mover el sentinela 9.99M/all-9s al pack ES como regla ES-only. En ingest.py:83 pasar la currency capturada + profile. Sin FX (comparacion intra-moneda). ES queda byte-identico (techo ES=5M EUR); paises nuevos aportan su price_max calibrado contra su muestra real.
- **Adversarial** · CRITICAL en JPY: SUV/furgon/lujo rutinario supera 5.000.000 JPY (~30k EUR) -> sanitize_price NULea una fraccion enorme del mercado JP legitimo; el 9.99M no existe en JPY. Swap escalar ingenuo (5M->100M) sin currency-awareness sigue roto porque la columna mezcla monedas. MXN 350.000 (~18k EUR) leido como 350k EUR pasa el gate pero es semanticamente erroneo.
- **Sellado (multi-vía)** · Cada precio con moneda explicita captura->sello; techo en la moneda propia contra price_max pack-calibrado de muestra real. Multi-via: (1) golden per-moneda: JPY normal sobrevive bajo techo JPY (fixture B3 verde), EUR>5M se sigue NULeando; (2) regresion ES byte-identica; (3) cross-check monto parseado vs priceCurrency JSON-LD (recipe_extract_web.py:79, hoy descartado) -> concordancia o REFUTED; (4) Hypothesis: sanitize_price idempotente, nunca NULea precio in-band declarado por el pack.
- **Herramienta NEXT-LEVEL (€0)** · price-parser — BSD-3-Clause — https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216 y :506]. Extrae monto+moneda del texto crudo con separadores per-locale; Babel (CLDR) para formatos y py-moneyed para aritmetica currency-safe + PRICE_MAX per-moneda en CountryProfile. CPU puro, offline, sin FX (intra-moneda por construccion). Alt: Babel, py-moneyed, moneyparser.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-16"></a>

### Faceta 16 — Gates de física km/year + cross-field + de-duplicación de bounds inline

> **Física universal, aplicación divergente.** 1 borde canónico (`ingest`) PERO ~30 parsers inlinean física propia (km>5M, year≤2100). **Cross-ref:** facetas [13](#faceta-13)·[14](#faceta-14)·[20](#faceta-20).

#### (a) Verificacion de code_hints contra el codigo real
- [VERIFIED pipeline/price_sanity.py:49] `PRICE_MAX = 5_000_000`; :51 `KM_MAX = 1_500_000`; :53 `YEAR_MIN = 1900`.
- [VERIFIED pipeline/price_sanity.py:69-83] `sanitize_km`: `if k < 0 or k >= KM_MAX: return None` (>= 1.5M nulea el sentinela Wallapop-unset).
- [VERIFIED pipeline/price_sanity.py:86-96] `sanitize_year`: `if y < YEAR_MIN or y > datetime.now().year + 1: return None` (bound **dinamico** now+1, nunca caduca).
- [VERIFIED pipeline/price_sanity.py:99-124] `sanitize_year_km`: `age = datetime.now().year - y; if (age <= 0 and k > 300_000) or (age <= 1 and k > 500_000): return None, None` (NULL-both por ambiguedad price-dependiente, Law-I).
- [VERIFIED pipeline/sources/autoscout24.py:179] INLINE `if km is not None and (km <= 0 or km > 5_000_000): km = None` — **5M, no 1.5M**.
- [VERIFIED pipeline/sources/autoscout24.py:189] INLINE `if year is not None and not (1900 <= year <= 2100): year = None` — **2100 hardcoded, no now+1**.
- [VERIFIED grep] **37 ocurrencias** inline de `1900 <= year <= 2100` en ~30 ficheros parser (carandclassic:251, coches_net:251, autocasion:244, coches_com:396/708, milanuncios:376, motor_es:498, wallapop:352, oem_*...); `sanitize_km|sanitize_year` importado **solo por 4 ficheros** (ingest.py, delta.py, price_sanity.py[def], wallapop_wholesale.py).
- [VERIFIED pipeline/ingest.py:83-88] el UNICO borde canonico: `price_clean=sanitize_price(v.price); km_clean=sanitize_km(v.km); year_clean=sanitize_year(v.year); year_clean,km_clean = sanitize_year_km(year_clean,km_clean)`.

#### (b) El mecanismo al atomo
La fisica universal vive en `price_sanity.py` (KM_MAX=1.5M dinamico-seguro, YEAR now+1 dinamico, cross-field NULL-both conservador) y se aplica en UN sitio: `ingest.py:83-88`. PERO ~30 parsers inlinean ANTES su PROPIA fisica **divergente**: `km>5M` (no 1.5M) y `year 1900..2100` (hardcoded, no now+1), sin llamar `sanitize_*`. Atomo: un `km=3_000_000` sobrevive el gate inline (`3M>5M` es False -> conservado) y luego ingest lo NULea (`3M>=1.5M` -> None). Las ~30 ramas inline son **peso muerto y contradictorio**: codifican una fisica (5M/2100) que el gate canonico (1.5M/now+1) refuta.

#### (c) Costura ES->generico + fix exacto
- **Costura:** ~34 `km>5M` + ~37 `year≤2100` inline, incoherentes con KM_MAX=1.5M / YEAR≤now+1, sin delegar. La fisica es universal pero esta **duplicada y divergente**.
- **Fix:** (1) ELIMINAR las ~30 ramas inline; los parsers emiten km/year **crudo** (int|None). (2) Aplicar la fisica en UN sitio via `normalize_vehicle` (facet 13) que delega a `sanitize_km/sanitize_year/sanitize_year_km`, borrando la contradiccion 5M-vs-1.5M y 2100-vs-(now+1). (3) **Migracion auditada:** centralizar a 1.5M CAMBIA km ya servidos en ES => dry-run + recompute + diff de delta para no disparar `KM_CHANGE` espurios. (4) km/year se HEREDAN universales pero deben **re-verificarse** por pais (ano-matriculacion vs modelo), no asumirse.

#### (d) Riesgo adversarial concreto
- El cross-gate asume `year = ano-CALENDARIO`. Un mercado con ano-matriculacion ≠ modelo (DE *Erstzulassung* vs *Modelljahr*) dispara **NULL-both falsos**: modelo-2026 matriculado-2024 con 400k km legitimos cae en `age<=0 ∧ km>300k` -> NULL-both espurio.
- Centralizar a 1.5M cambia km ES (5M->1.5M); sin migracion auditada, cada row historico >1.5M dispara `KM_CHANGE` en delta = ruido masivo.
- `KM_MAX=1.5M` es el sentinela Wallapop-unset **ESPANOL**; otro pais puede tener un sentinela-unset distinto (0 / 999999 / -1) que el gate no reconoce -> basura entra; o un comercial legitimo a 1.6M km NULeado.
- `YEAR now+1` es universal-fisico (OK), pero una fuente con fecha no-ISO (facet 20) entrega year basura ANTES del gate.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** **cero** ramas inline de fisica en los parsers (`grep km>5_000_000 = 0`, `grep 1900..2100 = 0` fuera de price_sanity); toda fisica km/year/cross aplicada exclusivamente en `normalize_vehicle -> sanitize_*`; migracion ES dry-run con **0 KM_CHANGE espurios** certificado.
- **Via 1 (test):** property-based (Hypothesis): `km>=0 ∨ None`, `year∈[1900,now+1] ∨ None`, el cross-gate nunca deja pasar `age<=0 ∧ km>300k`.
- **Via 2 (adversarial):** Hypothesis MINIMIZA el contraejemplo (el menor year/km que rompe el cross-gate) y bloquea el merge.
- **Via 3 (independiente):** re-ingest de un corpus ES congelado pre/post-centralizacion -> diff de km/year servidos == solo las correcciones esperadas (5M->1.5M), cero drift inesperado.

#### (f) Herramienta NEXT-LEVEL
**Hypothesis** — [VERIFIED NEXT-LEVEL.md:320] https://github.com/HypothesisWorks/hypothesis, **MPL-2.0, EUR0=True**. *property-based-recipe-fuzzing*: genera adversarialmente las invariantes de fisica (`km>=0∨None`, parse idempotente, cross-gate coherente) que los 11 golden ES no ven; MINIMIZA al contraejemplo mas simple y lo CONGELA como regression-fixture determinista. Alternativas: **pandera** (MIT — schema como contrato que auto-deriva estrategias Hypothesis desde el Vehicle), schemathesis, atheris. CPU puro, se integra en el job db-tests/unit existente.

#### Resolución condensada — Faceta 16
- **Costura** · La fisica universal (price_sanity.py: KM_MAX=1.5M dinamico, YEAR now+1, cross-field NULL-both) se aplica en UN borde (ingest.py:83-88), pero ~30 parsers inlinean ANTES su fisica DIVERGENTE: km>5M (autoscout24.py:179) y year 1900..2100 hardcoded (:189), sin llamar sanitize_*. 37 inline year-bounds verificados por grep; sanitize_km/year importado solo por 4 ficheros. Las ramas inline contradicen el gate canonico.
- **Fix** · 1) ELIMINAR las ~30 ramas inline (km>5M, year 1900..2100); los parsers emiten km/year crudo (int|None). 2) Aplicar fisica en UN sitio via normalize_vehicle -> sanitize_km/sanitize_year/sanitize_year_km, borrando la contradiccion 5M-vs-1.5M y 2100-vs-(now+1). 3) Migracion auditada (dry-run + recompute + diff delta) porque 1.5M cambia km ya servidos en ES => evitar KM_CHANGE espurios. 4) km/year se heredan universales pero se re-verifican por pais (ano-matriculacion vs modelo).
- **Adversarial** · Cross-gate asume year=ano-calendario: DE Erstzulassung vs Modelljahr dispara NULL-both falsos (modelo-2026 matriculado-2024, 400k km legitimos -> age<=0 and km>300k). Centralizar a 1.5M cambia km ES historico => KM_CHANGE masivo si no se migra auditado. KM_MAX=1.5M es el sentinela Wallapop-unset ESPANOL; otro pais usa 0/999999/-1 -> basura entra o comercial 1.6M NULeado. Fecha no-ISO (facet 20) entrega year basura antes del gate.
- **Sellado (multi-vía)** · Sello: cero ramas inline de fisica (grep km>5_000_000=0, grep 1900..2100=0 fuera de price_sanity); fisica solo en normalize_vehicle->sanitize_*; migracion ES dry-run con 0 KM_CHANGE espurios. Multi-via: (1) Hypothesis prueba km>=0|None, year in [1900,now+1]|None, cross-gate nunca deja age<=0 and km>300k; (2) adversarial = Hypothesis minimiza el contraejemplo y bloquea merge; (3) independiente = re-ingest corpus ES congelado pre/post => diff == solo correcciones esperadas 5M->1.5M.
- **Herramienta NEXT-LEVEL (€0)** · Hypothesis [VERIFIED NEXT-LEVEL.md:320] https://github.com/HypothesisWorks/hypothesis MPL-2.0 EUR0=True. property-based-recipe-fuzzing: genera las invariantes de fisica que los golden ES no ven, MINIMIZA el contraejemplo y lo congela como regression-fixture. Alternativas: pandera (MIT, auto-deriva estrategias desde el Vehicle), schemathesis, atheris. CPU puro, job db-tests/unit existente.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-17"></a>

### Faceta 17 — Canonicalización de `make` (algoritmo + tabla de marcas + segmentación CJK)

> **F7 · TITLE segmentation Latin-only.** `split()[0]` muere en CJK (`トヨタプリウス`); el diseño lo llamó 'motor puro' — falso. B4·MP6. **Cross-ref:** facetas [13](#faceta-13)·[24](#faceta-24).

#### (a) Verificacion de code_hints [VERIFIED]
- **`_CANON`** `pipeline/identity/make_normalizer.py:19-40` [VERIFIED]: ~70 marcas + alias, TODAS de **escritura latina** (`mercedes-benz`, `volkswagen`, `vw`, `bmw`, ... `rolls-royce`, `mclaren`, `polestar`). Docstring `:9` "grounded in the LIVE data ... 2026-06-15". **CERO claves CJK** (`日産`/`トヨタ`/`ホンダ` ausentes).
- **`make_from_title`** `make_normalizer.py:50-54` [VERIFIED]: `return _CANON.get(title.strip().split()[0].lower())` — **tokenizacion por espacios**, primer token.
- **`normalize_make`** `make_normalizer.py:57-76` [VERIFIED]: algoritmo `canon (`:68`) -> recuperar-del-titulo (`:71-73`) -> preservar-verbatim (Law I under-fill `:74-75` `return make  # ... preserve, do not guess`)`.
- **`canonical_make`** `:43-47` [VERIFIED]: marca CONOCIDA o `None` (HIGH precision).
- **Llamada en ingest** `pipeline/ingest.py:95` [VERIFIED]: `make_norm = normalize_make(v.make, v.title)` en el borde, sobre cada vehiculo nuevo.

#### (b) Mecanismo al atomo
En el borde de ingest, `normalize_make(make,title)`: (1) si `make` es marca conocida (cualquier casing) -> forma canonica via `_CANON`; (2) si no, si el **primer token whitespace** del titulo es marca conocida -> esa marca (recupera make-NULL y model-as-make, p.ej. wallapop `make='Golf'` titulo `'Volkswagen Golf'` -> `'Volkswagen'`); (3) si no, si `make` no vacio -> verbatim (Law I: under-fill > mis-fill, jamas adivina); (4) si no, `None`. El tokenizador `title.strip().split()[0]` ASUME que la marca lidera y que las palabras van separadas por espacio.

#### (c) Costura ES->generico + fix exacto
**Costura:** el diseno vende `normalize_make` como **motor puro** (algoritmo) parametrizado por **tabla** (pack). CIERTO para la TABLA (`_CANON` -> `brand_table` del pack). **FALSO para el ALGORITMO**: la SEGMENTACION (`split()[0]`, brand-leads-first) es ELLA MISMA country-coupled. La tokenizacion por espacios es una asuncion ES/latina; los scripts CJK escriben titulos SIN espacios inter-palabra (`トヨタプリウス`) -> `split()[0]` devuelve la **cadena entera** -> jamas matchea `_CANON` -> recuperacion de marca MUERTA. La costura no es "solo cambiar la tabla": el tokenizador debe volverse estrategia de segmentacion por-locale.

**Fix:**
1. **Tabla -> pack:** mover `_CANON` a `countries/<CC>/brand_table.yaml` (ES = pack #1), cargado por el normalizador; ES byte-identico (golden sobre los 431k cdp_code vivos / la distribucion de make).
2. **Algoritmo -> segmentacion locale-aware:** introducir `segment_title(title, LocaleProfile)->tokens`. Pack latino: `split()` (comportamiento actual preservado). Pack CJK: (a) romanizar via **anyascii** (`トヨタ`->`"toyota"`) ANTES de matchear, y/o (b) una gramatica de titulo determinista (**lark** EBNF, `countries/<CC>/title.lark`) que separa make/model/trim sin depender de espacios.
3. **Invariante:** `make ∈ brand_table` (o verbatim bajo Law I); jamas emitir make fuera de la tabla por adivinanza.
4. **Migracion:** re-correr `normalize_make` bajo el pack sobre la columna make ES viva con dry-run + recompute auditado (cero make-changes espurios), pues centralizar cambia el code path.

#### (d) Riesgo adversarial concreto
- **JP CRITICAL:** titulo `トヨタプリウス` -> `split()[0]` = cadena entera -> miss en `_CANON` -> recuperacion de marca muerta; `_CANON` no tiene `日産`/`トヨタ`/`ホンダ`. El "motor puro" es country-coupled (NEXT-LEVEL.md:279 nombra `make_normalizer.py:54` explicitamente).
- **DE/FR:** mayormente latino, `split` funciona, pero alias divergen y la tabla debe calibrarse a la distribucion REAL de marcas del pais (HIGH precision, jamas adivinar).
- **IT/PT:** latino, marcas locales exoticas (importadores regionales) ausentes de `_CANON` ES -> verbatim (correcto bajo Law I) pero sin canonicalizar.
- **Ruido:** un token-lider no-marca (`stock`/`vendo`/`caravana`) debe seguir dando make `None` (comportamiento actual); medio/full-width CJK (`ﾄﾖﾀ` vs `トヨタ`) debe canonicalizar identico (anyascii maneja half/full-width).

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** (1) `brand_table` es dato del pack; ES golden byte-identico sobre la distribucion viva; (2) un titulo-fixture CJK canonicaliza a la marca correcta donde `split()[0]` fallaba; (3) invariante `make ∈ brand_table∪verbatim` se sostiene bajo property-based fuzzing (Hypothesis, NEXT-LEVEL.md:317) — jamas un make adivinado; (4) migracion dry-run muestra cero make-changes espurios en ES.
- **Multi-via:** (via1) golden por-locale (ES/DE/JP) makes esperados; (via2) cross-check make-de-gramatica vs make-de-estructurado (next_data/json_api ya limpio) — deben concordar, discrepancia escala (NEXT-LEVEL.md:283); (via3) Hypothesis adversarial genera titulos ruidosos/CJK y asevera "nunca emite make fuera de brand_table y nunca crashea (cae a LLM-escala)".

#### (f) Herramienta NEXT-LEVEL que la eleva
**deterministic-grammar-spec-parser · lark** (MIT, https://github.com/lark-parser/lark) [VERIFIED NEXT-LEVEL.md:277-283]. Gramatica EBNF (Earley/LALR) que separa make/model/trim/cilindrada/combustible/potencia **deterministicamente ANTES de cualquier LLM**; arregla explicitamente `make_normalizer.py:54 split()[0]` muriendo en CJK; la gramatica vive como dato del pack `countries/<CC>/title.lark`. €0, CPU puro, sin modelo. **Complemento:** script-aware-transliteration · anyascii (ISC, https://github.com/anyascii/anyascii) [VERIFIED NEXT-LEVEL.md:221-227] romaniza CJK/Cirilico/Griego para que segmentacion + tabla matcheen (`トヨタ`->`"toyota"`); ES ASCII byte-identico; ISC evita la contaminacion GPL de unidecode en el servicio API.

#### Resolución condensada — Faceta 17
- **Costura** · normalize_make se vende como motor-puro parametrizado por tabla. CIERTO para la tabla (_CANON make_normalizer.py:19-40 -> brand_table del pack). FALSO para el algoritmo: la segmentacion title.strip().split()[0] (:54) es country-coupled — asume escritura latina con espacios. CJK sin espacios (トヨタプリウス) -> split()[0] devuelve la cadena entera -> miss en _CANON (que :19-40 no tiene claves CJK) -> recuperacion de marca muerta. La costura no es solo la tabla: el tokenizador debe volverse estrategia de segmentacion por-locale.
- **Fix** · Tabla->pack: _CANON a countries/<CC>/brand_table.yaml (ES pack #1), ES byte-identico (golden sobre 431k cdp_code). Algoritmo->locale-aware: segment_title(title,LocaleProfile)->tokens; pack latino = split() actual; pack CJK = romanizar via anyascii (トヨタ->toyota) antes de matchear y/o gramatica title.lark (lark EBNF) que separa make/model/trim sin espacios. Invariante make ∈ brand_table∪verbatim (Law I, jamas adivinar). Migracion dry-run+recompute auditado sobre la columna make ES (centralizar cambia el code path).
- **Adversarial** · JP CRITICAL: トヨタプリウス -> split()[0] = cadena entera -> miss en _CANON -> recuperacion de marca muerta; _CANON sin 日産/トヨタ/ホンダ; el 'motor puro' es country-coupled (NEXT-LEVEL.md:279 nombra make_normalizer.py:54). DE/FR latino pero alias divergen, tabla a calibrar a la distribucion real. IT/PT marcas locales exoticas ausentes de _CANON ES -> verbatim (correcto Law I) sin canonicalizar. Ruido: token-lider no-marca (stock/vendo) debe dar None; half/full-width CJK (ﾄﾖﾀ vs トヨタ) debe canonicalizar identico (anyascii).
- **Sellado (multi-vía)** · Sello: (1) brand_table dato del pack, ES golden byte-identico sobre la distribucion viva; (2) titulo CJK canonicaliza a la marca correcta donde split()[0] fallaba; (3) invariante make ∈ brand_table∪verbatim bajo Hypothesis (NEXT-LEVEL.md:317), jamas adivinado; (4) migracion dry-run cero make-changes espurios en ES. Multi-via: golden por-locale ES/DE/JP | cross-check make-de-gramatica vs make-de-estructurado (next_data/json_api ya limpio), discrepancia escala (NEXT-LEVEL.md:283) | Hypothesis adversarial sobre titulos ruidosos/CJK (nunca make fuera de brand_table, nunca crashea).
- **Herramienta NEXT-LEVEL (€0)** · deterministic-grammar-spec-parser · lark (MIT, https://github.com/lark-parser/lark) [VERIFIED NEXT-LEVEL.md:277-283] — gramatica EBNF (Earley/LALR) separa make/model/trim/cc/fuel/power deterministicamente ANTES del LLM; arregla make_normalizer.py:54 split()[0] muriendo en CJK; vive como pack data countries/<CC>/title.lark, €0 CPU. Complemento: anyascii (ISC, https://github.com/anyascii/anyascii) [VERIFIED NEXT-LEVEL.md:221-227] romaniza CJK/Cirilico/Griego (トヨタ->toyota) para que segmentacion+tabla matcheen; ES ASCII byte-identico; ISC evita el GPL de unidecode.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-18"></a>

### Faceta 18 — Canonicalización de enum `fuel` (`fuel_map` locale→código neutral)

> **F5 · ENUM fuel sin normalizar.** `fuel` verbatim ES, sin `fuel_map` central (38 ficheros). B8·B12·B14·MP5. **Cross-ref:** facetas [11](#faceta-11)·[13](#faceta-13)·[26](#faceta-26)·[24](#faceta-24).

#### (a) Verificacion de code_hints [VERIFIED]
- **insercion VERBATIM** — `pipeline/ingest.py:96-101` [VERIFIED]: el `INSERT INTO vehicle (... fuel, transmission ...)` pasa `v.fuel, v.transmission` **sin normalizer** (a diferencia de `make`, que pasa por `normalize_make(v.make, v.title)` en `:95`). El fuel entra en la columna tal cual lo emitio el conector.
- **coches.net** — `pipeline/platform/coches_net_wholesale.py:273` [VERIFIED]: `fuel=item.get("fuelType")` con comentario `# already a clean UTF-8 string (Diésel/Eléctrico/...)` — etiqueta ES libre.
- **coches.com** — `pipeline/platform/coches_com_wholesale.py:419` [VERIFIED]: `fuel=_name(card.get("fuel"))` con comentario `# UTF-8: "Híbrido Gasolina", "Diésel"`.
- **RACC set ES** — `pipeline/platform/faciliteacoches_racc_wholesale.py:371` [VERIFIED]: `_RACC_FUELS = {"GASOLINA","DIESEL","DIÉSEL","HÍBRIDO","HIBRIDO","ELÉCTRICO","ELECTRICO",...}` usado en `:419-420` para clasificar por membresia (`if up in _RACC_FUELS`).
- **AS24** — `pipeline/sources/autoscout24.py:215` [VERIFIED]: `fuel=_raw(v.get("fuelCategory")) or v.get("fuel")` — etiqueta de la fuente sin mapear.
- **breadth** [VERIFIED]: **38 ficheros en `pipeline/`** contienen etiquetas fuel ES (`Gasolina/Diésel/Híbrido/Eléctrico/Gasóleo`) — grep `files_with_matches`. **NO existe** simbolo central `fuel_map`/`FUEL_MAP` (grep 0 hits): la canonicalizacion de fuel esta AUSENTE, cada conector emite su label ES.

#### (b) Mecanismo al atomo
A diferencia de `make` (que tiene `normalize_make` con `_CANON`), `fuel` **no tiene canonicalizacion**: el conector lee la etiqueta de la fuente (`fuelType`, `card.fuel`, `fuelCategory`) y la **almacena verbatim en espanol**. El de-facto-canon de la columna `vehicle.fuel` es "lo que coches.net/coches.com/AS24-ES escribieron en ES". La served-surface y los facets filtran sobre esas etiquetas ES literales (`Gasolina`/`Diésel`/...). No hay punto de aplicacion: `ingest.py:101` es donde DEBERIA invocarse un `fuel_map`, y no lo hace.

#### (c) Costura ES->generico
La costura: introducir un **`fuel_map` por `LocaleProfile`** que mapee `label/codigo de la fuente -> codigo neutral` `{PETROL, DIESEL, EV, HYBRID, PHEV, LPG, CNG}`, aplicado **en el borde** como `make` (en `normalize_vehicle`/`ingest`). Es estructuralmente **mas que "un dict"**: incluye (1) el simbolo central que el motor APLICA (no N dicts inline ES-target dispersos en 38 ficheros); (2) la **migracion downstream** de la served-surface/facets que hoy filtran sobre etiquetas ES; (3) la reescritura de `_RACC_FUELS` y similares como datos del pack, no sets hardcodeados ES. Fix exacto: anadir `fuel_code` al `CanonicalVehicle` ([faceta 11](#faceta-11)), poblarlo via `LocaleProfile.fuel_map` en el borde, y migrar la columna/facets de etiquetas ES a codigos neutrales.

#### (d) Riesgo adversarial concreto
- **IT** emite `Benzina`, **DE** `Benzin`, **PT** `Gasóleo`/`Elétrico`, **FR** `Essence` -> **fragmentan la columna** contra el `Gasolina`/`Diésel` ES y **rompen todo filtro de facets** que asume labels ES (HIGH).
- **DE/AS24.de**: `fuelCategory='Benzin'` -> entra verbatim, queda fuera del canon-ES de-facto -> el filtro "Gasolina" no lo encuentra: el coche existe pero es **invisible** al eje de busqueda.
- **ruido/under-fill**: una fuente con fuel ausente o en mayusculas (`DIESEL` vs `Diésel`) ya hoy en ES requiere el set membership de `_RACC_FUELS` con variantes con/sin tilde -> a escala multipais explota combinatoriamente.
- El diseno **minimiza** esto como "solo un dict" cuando es un **cambio estructural** (migrar la served-surface + facets).

#### (e) Criterio de sellado + verificacion multi-via
- **Sello**: (1) **fill-rate** de `fuel_code` por encima de un piso por receta (no NULL masivo); (2) **vocabulario cerrado**: todo `fuel_code` emitido pertenece al enum neutral `{PETROL,DIESEL,EV,HYBRID,PHEV,LPG,CNG}` — cero label ES crudo en la columna canonica; (3) caso `label-no-visto` no cae a `None` silencioso (se marca y escala).
- **Multi-via**: (i) **test** = golden por pais (`Benzina/Benzin/Gasóleo/Essence -> PETROL|DIESEL`); (ii) **adversarial** = un contrato de datos (Pandera/Great Expectations) que FALLA el build si la columna `fuel_code` contiene un valor fuera del enum (vocabulario-coherente, fail-closed); (iii) **via independiente** = la capa-2 LLM con gramatica GBNF emite UNICAMENTE el enum y se cruza contra el `fuel_map` determinista — el determinista gana, el desacuerdo escala.

#### (f) Herramienta NEXT-LEVEL
**outlines** (`grammar-constrained-llm-normalizer`) cablea la capa-2 para el **residuo sucio de fuel** (labels libres irreducibles en rungs `css`/`regex`) con **decodificacion restringida GBNF/JSON-Schema**: el LLM emite `fuel ∈ enum` por construccion — **fisicamente imposible** inventar un fuel fuera del vocabulario del pack. Seam dormante EUR0 con fallback determinista (`fuel_map`) que siempre gana hoy. Para el **gate de vocabulario-coherente** del sello (fail-closed sobre la columna), **Great Expectations/Pandera** expresa "todo `fuel_code` ∈ enum neutral" como contrato ejecutable. [VERIFIED NEXT-LEVEL.md:272 outlines https://github.com/dottxt-ai/outlines Apache-2.0; :167 Great Expectations https://github.com/great-expectations/great_expectations Apache-2.0; :321 pandera]

#### Resolución condensada — Faceta 18
- **Costura** · fuel se inserta VERBATIM en ES sin normalizer (ingest.py:96-101 pasa v.fuel directo, a diferencia de make que usa normalize_make en :95). Fuentes ES emiten labels libres: coches_net_wholesale.py:273 fuel=item.get('fuelType') 'Diésel/Eléctrico'; coches_com_wholesale.py:419 'Híbrido Gasolina'/'Diésel'; faciliteacoches_racc_wholesale.py:371 _RACC_FUELS set ES; autoscout24.py:215 fuelCategory crudo. NO existe simbolo central fuel_map (grep 0 hits); 38 ficheros pipeline/ con etiquetas fuel ES. La served-surface/facets filtran sobre labels ES.
- **Fix** · Anadir fuel_code al CanonicalVehicle y un fuel_map por LocaleProfile que mapee label/codigo de fuente -> {PETROL,DIESEL,EV,HYBRID,PHEV,LPG,CNG}, aplicado en el borde (normalize_vehicle/ingest) como make; reescribir _RACC_FUELS y los dicts inline como datos del pack; MIGRAR downstream la served-surface y los facets de etiquetas ES a codigos neutrales; el caso label-no-visto se marca y escala, nunca None silencioso.
- **Adversarial** · HIGH: IT 'Benzina', DE 'Benzin', PT 'Gasóleo'/'Elétrico', FR 'Essence' fragmentan la columna contra 'Gasolina'/'Diésel' ES y rompen todo filtro de facets que asume labels ES. AS24.de 'Benzin' entra verbatim -> el coche es invisible al filtro 'Gasolina'. Variantes con/sin tilde (DIESEL vs Diésel) ya fuerzan sets membership en ES; a escala multipais explota. El diseno lo minimiza como 'solo un dict' cuando es cambio estructural (migra served-surface+facets).
- **Sellado (multi-vía)** · Sello: fill-rate de fuel_code sobre piso por receta + vocabulario CERRADO (todo fuel_code ∈ enum neutral, cero label ES crudo) + caso label-no-visto marcado, no None silencioso. Multi-via: (1) test golden por pais (Benzina/Benzin/Gasóleo/Essence -> PETROL|DIESEL); (2) adversarial: contrato Pandera/Great Expectations FALLA el build si fuel_code sale del enum (fail-closed); (3) via independiente: capa-2 LLM con GBNF emite solo el enum y se cruza contra el fuel_map determinista (gana el determinista, desacuerdo escala).
- **Herramienta NEXT-LEVEL (€0)** · outlines (grammar-constrained-llm-normalizer) — Apache-2.0, EUR0 — https://github.com/dottxt-ai/outlines [VERIFIED NEXT-LEVEL.md:272]: capa-2 que emite fuel ∈ enum por construccion (GBNF), imposible alucinar fuera del pack; fallback determinista fuel_map gana hoy. Gate de vocabulario-coherente: Great Expectations (Apache-2.0) https://github.com/great-expectations/great_expectations [VERIFIED :167] / Pandera [VERIFIED :321].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-19"></a>

### Faceta 19 — Canonicalización de enum `transmission` (`transmission_map` locale→código neutral)

> **F5 · ENUM transmission.** 3 encodings incompatibles a 1 columna; `.get`→None silencioso. B8·B12·B14. **Cross-ref:** facetas [11](#faceta-11)·[13](#faceta-13)·[26](#faceta-26)·[24](#faceta-24).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/platform/coches_net_wholesale.py:130` [VERIFIED] `_TRANSMISSION = {1: "Manual", 2: "Automático"}` — dict hardcoded con **labels ES**, comentario ":129" confirma "coches.net codes; verified live: only 1/2 seen". Encoding = **ids numericos**.
- `pipeline/platform/coches_net_wholesale.py:274` [VERIFIED] `transmission=_TRANSMISSION.get(item.get("transmissionTypeId"))` — `.get()` devuelve **None silencioso** para cualquier id no-visto (3/4).
- `pipeline/ingest.py:101` [VERIFIED] el INSERT escribe `v.transmission` **VERBATIM** (mismo INSERT lleva `v.fuel` verbatim) — no hay normalizer de transmission en el borde de ingest.
- `pipeline/platform/coches_com_wholesale.py:420` [VERIFIED] `transmission=_name(card.get("transmission"))` con comentario `"Automática" / "Manual"` — encoding = **labels ES libres** (distinto de coches.net).
- `pipeline/platform/dasweltauto_wholesale.py:274-282` [VERIFIED] `_map_gear`: `Gear.NumberType` es **texto libre** ('6 Cambio manual', 'DSG automático'); regex `_AUTO_RE`/`_MANUAL_RE` (:278-281) -> "Automático"/"Manual"; **fallthrough `return txt.strip() or None` (:282)** = el texto crudo no-matcheado entra a la columna sin normalizar. Tercer encoding distinto.

#### (b) El mecanismo al atomo
Tres fuentes, tres encodings INCOMPATIBLES que aterrizan en la MISMA columna `vehicle.transmission`: (1) coches.net mapea id->label ES via dict cerrado pero con `.get` que falla-a-None; (2) coches.com pasa el label ES libre tal cual; (3) dasweltauto regexea texto libre y, si no matchea, escribe el crudo. No existe un simbolo central `transmission_map`; cada conector resolvio su mapeo aislado y el de-facto-canon de la columna es 'Automática'/'Manual' ES. La served-surface/facets filtran sobre esas etiquetas ES. A diferencia de make (que SI se canonicaliza en `normalize_make`), transmission no pasa por ningun normalizador — es el patron gemelo de fuel ([faceta 18](#faceta-18)) pero con encoding de fuente distinto (ids numericos vs labels libres vs texto-gear), por eso se separa.

#### (c) Costura ES->generico
`transmission_map` por `LocaleProfile` que mapee TANTO ids numericos COMO labels libres -> enum neutral CERRADO `{AUTOMATIC, MANUAL, CVT, DCT}`, aplicado en `normalize_vehicle` en el borde (como make), no inline por conector. Requisitos: (1) cubrir el caso id-no-visto SIN caer a None silencioso — emitir una señal `transmission_unmapped` (log/contador) para que la cobertura del mapa sea auditable; (2) eliminar el fallthrough `txt.strip()` de dasweltauto (no escribir crudo); (3) **migracion downstream**: la served-surface y las facets que filtran sobre 'Automática'/'Manual' deben migrar a los codigos neutrales — esto es un cambio ESTRUCTURAL, no "solo un dict" como minimiza el diseno.

#### (d) Riesgo adversarial concreto — HIGH
- **DE**: AS24.de emite `'Automatik'` -> no matchea el target ES.
- **IT**: `'Automatico'`; **PT**: `'Automática'`/`'Manual'` (coincide por azar con ES en PT, pero IT/DE no).
- **id-no-visto**: un `transmissionTypeId` 3/4 (DCT, CVT) cae a None silencioso en coches.net.
- **dasweltauto fallthrough**: un `NumberType` raro ('Tiptronic 8 vel.') ya hoy escribe crudo a la columna.
- **Resultado**: la columna mezcla `'Automática'/'Automatik'/'Automatico'/'DSG automático'` y CUALQUIER filtro cross-pais de facets que asuma labels ES se rompe.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (golden por fuente)**: cada id/label de cada conector mapea al codigo neutral esperado; un id no-visto LEVANTA señal/flag, nunca None silencioso ni crudo.
- **Via 2 (property-fuzz)**: Hypothesis genera ids no-vistos y labels mixtos multi-locale y asevera el invariante `transmission ∈ {AUTOMATIC,MANUAL,CVT,DCT} ∪ explicit-unknown` (nunca verbatim ES, nunca None silencioso).
- **Via 3 (data-contract pre-sello)**: Pandera/Great Expectations asevera que la columna `transmission` de un pais sellado pertenece al enum neutral cerrado -> fail-closed si entra una etiqueta cruda.
- **Via 4 (piso de fill-rate)**: `decide_status` ([faceta 26](#faceta-26)) exige un piso de % transmission no-NULL en el sample antes de sellar VERIFIED.

#### (f) Herramienta NEXT-LEVEL
Primario para el residuo de texto libre irreducible (dasweltauto 'DSG automático'): `grammar-constrained-llm-normalizer` -> **outlines** (Apache-2.0) [VERIFIED NEXT-LEVEL.md:269-275] https://github.com/dottxt-ai/outlines — el LLM local emite UNICAMENTE el enum neutral cerrado por gramatica/JSON-Schema, fisicamente incapaz de inventar fuera del vocabulario; seam €0 dormante con fallback determinista que siempre gana hoy. Soporte: **Snorkel** (Apache-2.0) [VERIFIED NEXT-LEVEL.md:514] https://github.com/snorkel-team/snorkel — weak-supervision para auto-construir el label->code map desde los N dicts inline sin etiquetado manual; **Hypothesis** (MPL-2.0) [VERIFIED NEXT-LEVEL.md:320] para cazar el id-no-visto/None-silencioso; **Great Expectations/Pandera** (Apache-2.0/MIT) [VERIFIED NEXT-LEVEL.md:167] como data-contract de enum cerrado al sello. El dict determinista por LocaleProfile sigue siendo la espina; outlines solo toca el residuo.

#### Resolución condensada — Faceta 19
- **Costura** · Tres encodings incompatibles a la MISMA columna vehicle.transmission sin normalizador central: coches_net_wholesale.py:130 dict id->label ES con .get->None silencioso (:274); coches_com_wholesale.py:420 label ES libre tal cual; dasweltauto_wholesale.py:274-282 texto-gear regex con fallthrough txt.strip() que escribe crudo. ingest.py:101 inserta verbatim. A diferencia de make, transmission no pasa por normalize_vehicle. La served-surface filtra sobre labels ES.
- **Fix** · transmission_map por LocaleProfile que mapee ids numericos Y labels libres -> enum neutral cerrado {AUTOMATIC,MANUAL,CVT,DCT}, aplicado en normalize_vehicle en el borde (como make). Cubrir id-no-visto con señal transmission_unmapped (no None silencioso); eliminar el fallthrough txt.strip() de dasweltauto; migrar downstream la served-surface/facets de labels ES a codigos neutrales (cambio estructural, no 'solo un dict').
- **Adversarial** · HIGH: AS24.de 'Automatik', IT 'Automatico' no matchean el target ES; transmissionTypeId 3/4 (DCT/CVT) cae a None silencioso en coches.net; dasweltauto fallthrough ya escribe crudo ('Tiptronic 8 vel.'). La columna mezcla 'Automática'/'Automatik'/'Automatico'/'DSG automático' y cualquier filtro cross-pais de facets que asuma labels ES se rompe.
- **Sellado (multi-vía)** · Via1 golden por fuente: cada id/label -> codigo neutral esperado, id no-visto levanta flag (nunca None ni crudo); Via2 Hypothesis genera ids no-vistos/labels mixtos y asevera transmission ∈ enum-cerrado ∪ explicit-unknown; Via3 Pandera/Great Expectations pre-sello asevera columna ∈ enum neutral (fail-closed ante etiqueta cruda); Via4 piso de fill-rate transmission no-NULL en decide_status ([faceta 26](#faceta-26)).
- **Herramienta NEXT-LEVEL (€0)** · grammar-constrained-llm-normalizer -> outlines (Apache-2.0) https://github.com/dottxt-ai/outlines [VERIFIED NEXT-LEVEL.md:272] para el residuo de texto libre (emite solo el enum neutral por gramatica, no puede alucinar). Soporte: Snorkel (Apache-2.0, NEXT-LEVEL.md:514) auto-construye el label->code map sin etiquetado; Hypothesis (MPL-2.0, NEXT-LEVEL.md:320) caza id-no-visto/None-silencioso; Great Expectations/Pandera (NEXT-LEVEL.md:167) data-contract de enum cerrado. El dict determinista por LocaleProfile es la espina; outlines solo el residuo.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-20"></a>

### Faceta 20 — Parsing de fecha/matriculación por locale (`parse_date`)

> **F9 · DATE format per locale.** `split('-')[-1]`/`[:4]` acoplados a AS24-ISO; sin `parse_date`. MP9. **Cross-ref:** facetas [13](#faceta-13)·[16](#faceta-16).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/sources/autoscout24.py:131-137` [VERIFIED] `_year_from(reg)`: `if reg and "-" in str(reg): return int(str(reg).split("-")[-1])` — extrae el year tomando el **ultimo segmento tras split('-')**; asume separador `-` y que el year es el ultimo token (formato AS24 `MM-YYYY`).
- `:182-188` [VERIFIED] en `parse_listing_vehicle`: `reg = _raw(v.get("firstRegistrationDate"))`; `if reg and len(str(reg))>=4 and str(reg)[:4].isdigit(): year = int(str(reg)[:4])` (toma los 4 primeros chars de un **ISO `YYYY-MM-DD`**) `else: year = _year_from(tr.get("firstRegistration"))`. `:189` acota `1900 <= year <= 2100`.
- `pipeline/recipe.py:31` [VERIFIED] `field_map["year"] = "listing.tracking.firstRegistration (MM-YYYY -> YYYY)"` — la receta **documenta** la transformacion en prosa, no la ejecuta.
- **Ausencia confirmada:** grep `def parse_date` / `LocaleProfile` en `pipeline/` = **0 hits** [VERIFIED]. `LocaleProfile.date_fmt` esta **propuesto** ([facetas 13/22](#faceta-13)) pero **no hay `parse_date` implementado**. La unica razon de que ES/AS24 funcione es que la fuente entrega **ISO** (`firstRegistrationDate.raw "YYYY-MM-DD"`) y un fallback `MM-YYYY` por `split('-')[-1]`.

#### (b) El mecanismo al atomo
Hoy "parsear fecha" = dos atajos acoplados a la forma de AS24:
1. **ISO-prefix:** `str(reg)[:4]` — funciona porque `firstRegistrationDate.raw` es `YYYY-MM-DD`; los 4 primeros chars son el year.
2. **split('-')[-1]:** para `tracking.firstRegistration = "MM-YYYY"`, el year es el ultimo token tras `-`.
Ambos son **frágiles por construccion**: dependen de (a) separador exactamente `-`, (b) year en posicion fija (primero en ISO, ultimo en MM-YYYY), (c) que la fuente entregue ISO. No hay conversion `text→year` consciente de **formato del pais**; es distinto del **gate** `sanitize_year` ([faceta 16](#faceta-16)), que es un bound sobre un `int` ya extraido.

**360 — `parse_date(text, profile) -> (year, date|None)`** que cubra los formatos de matriculacion del pais via `profile.date_fmt`: ES `dd/mm/aaaa`, DE `dd.mm.yyyy`, ISO `yyyy-mm-dd`, JP `yyyy年mm月dd日`, PT/FR variantes. Alimenta `year` limpio al gate de fisica y preserva la fecha cruda en `raw_locale_fields` (auditabilidad).

#### (c) La costura ES→generico + fix exacto
- **Fix:** crear `parse_date(text, profile)` parametrizado por `profile.date_fmt` (CLDR). El extractor emite el **string crudo de matriculacion**; `normalize_vehicle` ([faceta 13](#faceta-13)) llama `parse_date` y de ahi `sanitize_year`.
- **Reemplazo de `_year_from`/`[:4]`:** sustituir los dos atajos por `parse_date`; AS24 ISO sigue funcionando (es un `date_fmt` mas), pero deja de ser el **unico** camino que no se rompe.
- **Orden mes/dia:** `01/02/2024` es ambiguo (1-feb vs 2-ene) **sin** `date_fmt` del locale; el pack debe declarar el orden para no invertir fechas a escala.
- **CJK:** `yyyy年mm月dd日` necesita un parser consciente de los separadores 年/月/日, no `split('-')`.

#### (d) Riesgo adversarial concreto
- **DE `dd.mm.yyyy`:** una fuente CMS/generic DE con `15.03.2019` → `"-" not in reg` → `_year_from=None`, y `[:4].isdigit()` toma `"15.0"` → no-digit → **year=None**: matriculacion DE perdida en silencio.
- **JP `2019年3月`:** sin parser → year basura o None; `split('-')` no aplica.
- **Ambiguedad mes/dia:** `01/02/2024` sin `date_fmt` → orden invertido a escala (el dia se toma por mes), corrompiendo la distribucion de edad.
- **Separador no-`-`:** `_year_from` asume `-`; un `MM/YYYY` o `MM.YYYY` devuelve `None` aunque el dato exista.
- **Fragilidad heredada:** ES/AS24 sobrevive por casualidad (ISO); cualquier fuente del pais nuevo que NO entregue ISO entra sin parser.

#### (e) Criterio de sellado + verificacion multi-via
- **Sellado:** existe `parse_date(text, profile)`; los dos atajos `_year_from`/`[:4]` quedan subsumidos como un `date_fmt` mas; `year` siempre proviene de `parse_date`→`sanitize_year`; la fecha cruda se preserva en `raw_locale_fields`.
- **Via 1 (golden por pais):** fixtures ES `dd/mm/aaaa`, DE `dd.mm.yyyy`, ISO `yyyy-mm-dd`, JP `yyyy年` → `(make,...,year)` esperado; AS24 ISO **byte-identico** (cero regresion).
- **Via 2 (adversarial/ambiguedad):** `01/02/2024` bajo `date_fmt=ES` da feb; bajo `date_fmt=US` da ene — el mismo input con distinto pack da el resultado del pack, nunca un default oculto.
- **Via 3 (cruce ortogonal):** el `year` de `parse_date` (texto) se cruza con el `year` del campo estructurado `next_data/json_api` (metadato) cuando ambos existen — deben concordar o escala.
- **Via 4 (property-based):** Hypothesis genera fechas ruidosas y afirma "`parse_date` nunca crashea y nunca emite year fuera de `1900..now+1` (cae a None y escala)".

#### (f) Herramienta NEXT-LEVEL que la eleva a nivel inalcanzable
- **Primaria — Babel (CLDR)**: NEXT-LEVEL.md nombra Babel explicitamente como la autoridad de **"number/currency/date formats por locale"** [VERIFIED NEXT-LEVEL.md:217] y "CLDR locale/currency/number data" [VERIFIED NEXT-LEVEL.md:507]. `babel.dates` aporta los patrones de fecha CLDR por locale para implementar `parse_date(text, profile.date_fmt)` con datos CLDR **offline-bundled**, eliminando los atajos `split('-')`/`[:4]` y la ambiguedad mes/dia. Licencia **BSD-3-Clause** [ASSUMED — la biblia nombra Babel como alternativa CLDR pero no fija una linea URL/licencia propia; Babel/Pallets es BSD-3-Clause por registro publico] — https://github.com/python-babel/babel.
- **Acoplada (titulo/spec con fecha embebida) — lark** (deterministic-grammar-spec-parser, NEXT-LEVEL.md:277-283 [VERIFIED]): cuando la fecha/year viene dentro de un titulo libre ("... 2019 ..."), una gramatica EBNF de Lark (Earley/LALR) separa year/spec deterministicamente como **dato del pack** (`countries/<CC>/title.lark`) antes de tocar cualquier LLM — €0, auditable. **MIT, €0 — https://github.com/lark-parser/lark** [VERIFIED NEXT-LEVEL.md:280].
- Nota anti-alucinacion: la biblia no minero un paquete date-dedicado (p.ej. `dateparser`); Babel es la herramienta **de la biblia** para fecha-por-locale, por eso es la primaria. Cualquier sustituto fuera de NEXT-LEVEL.md seria [ASSUMED].

#### Resolución condensada — Faceta 20
- **Costura** · Dos atajos acoplados a AS24 en pipeline/sources/autoscout24.py: _year_from (:131-137) hace split('-')[-1] (asume separador '-' y year ultimo), y parse_listing_vehicle (:182-188) toma str(reg)[:4] de un ISO YYYY-MM-DD; recipe.py:31 documenta 'firstRegistration MM-YYYY -> YYYY' en prosa. No hay parse_date (grep 0 hits); LocaleProfile.date_fmt solo propuesto. ES funciona por casualidad (la fuente da ISO).
- **Fix** · Crear parse_date(text, profile) parametrizado por profile.date_fmt (CLDR): ES dd/mm/aaaa, DE dd.mm.yyyy, ISO yyyy-mm-dd, JP yyyy年mm月dd日; el extractor emite el string crudo de matriculacion y normalize_vehicle ([faceta 13](#faceta-13)) llama parse_date -> sanitize_year; AS24 ISO queda como un date_fmt mas (deja de ser el unico camino que no rompe); el pack declara el orden mes/dia para no invertir 01/02/2024 a escala; preservar la fecha cruda en raw_locale_fields.
- **Adversarial** · DE '15.03.2019' -> '-' not in reg -> _year_from=None y [:4]='15.0' no-digit -> year=None (matriculacion perdida en silencio); JP '2019年3月' sin parser -> basura/None; 01/02/2024 sin date_fmt -> mes/dia invertido a escala; separador no-'-' (MM/YYYY, MM.YYYY) -> _year_from=None aunque el dato exista; ES/AS24 sobrevive solo por ISO, cualquier fuente no-ISO del pais nuevo entra sin parser.
- **Sellado (multi-vía)** · Sellado: existe parse_date(text, profile); _year_from/[:4] subsumidos como un date_fmt mas; year siempre via parse_date->sanitize_year; fecha cruda en raw_locale_fields. Verificacion: (1) golden por pais (ES/DE/ISO/JP) + AS24 ISO byte-identico; (2) adversarial 01/02/2024 da el resultado del pack (ES=feb, US=ene), nunca default oculto; (3) cruce year-texto vs year-estructurado (next_data) concuerda o escala; (4) property-based: parse_date nunca crashea ni emite year fuera de 1900..now+1.
- **Herramienta NEXT-LEVEL (€0)** · PRIMARIA: Babel (CLDR), nombrada en la biblia como autoridad de 'number/currency/date formats por locale' [VERIFIED NEXT-LEVEL.md:217] y 'CLDR locale/currency/number data' [VERIFIED :507]; babel.dates da los patrones de fecha CLDR offline-bundled para parse_date(text, profile.date_fmt). Licencia BSD-3-Clause [ASSUMED — la biblia no fija linea URL/licencia propia de Babel; Babel/Pallets es BSD-3 por registro publico] — https://github.com/python-babel/babel. ACOPLADA: lark (deterministic-grammar-spec-parser, :277-283) EBNF como dato del pack (countries/<CC>/title.lark) para year/fecha embebida en titulo libre, MIT, EUR0 — https://github.com/lark-parser/lark [VERIFIED :280]. Nota: la biblia no minero un paquete date-dedicado; cualquier sustituto fuera de NEXT-LEVEL.md seria [ASSUMED].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-21"></a>

### Faceta 21 — Emisión postcode→region en extracción + gate INE en ingest

> **F1 · GEO country-blindness — el más grave de la etapa.** `zip[:2]` + gate INE `01..52` en 4 parsers Y en `ingest`. B1·B7·B9·B11·B13·MP3·MP4·SH3. **Cross-ref:** facetas [11](#faceta-11)·[26](#faceta-26) · geo-04.

#### (a) Verificacion de code_hints [VERIFIED]
- **`pipeline/sources/autoscout24.py:232`** [VERIFIED exacto]: `prov = str(zip_)[:2] if zip_ and str(zip_)[:2].isdigit() else None`. Los 2 primeros digitos del CP tratados como codigo provincia INE. Adicional [VERIFIED]: `:143` `_slug_from_infopage` usa `re.search(r"/profesionales/([a-z0-9-]+)", href)` — segmento de ruta ES hardcodeado.
- **`pipeline/platform/autocasion_wholesale.py:195-206` `_prov_from_cp`** [VERIFIED]: docstring "Spanish postcode's first two digits ARE the INE province code (01..52)"; `s = re.sub(r"\D", "", str(postcode))` (:200), `p = s[:2]` (:203), `if not ("01" <= p <= "52"): return None` (:204).
- **`pipeline/platform/coches_net_wholesale.py:190-201` `_prov2`** [VERIFIED]: docstring "mainProvinceId IS the INE province code"; `n = int(province_id)` (:196), `if not (1 <= n <= 52): return None` (:199), `return f"{n:02d}"` (:201). (Aqui la fuente ya da un id INE, no un CP; el rango 1..52 sigue siendo ES.)
- **`pipeline/platform/coches_com_wholesale.py:276-282` `_prov2`** [VERIFIED]: `n = _to_int(province_id)` (:279), `if n is None or not (1 <= n <= 52): return None` (:280), `return f"{n:02d}"` (:282).
- **`pipeline/ingest.py:49-50`** [VERIFIED exacto]: `if not (d.province_code.isdigit() and "01" <= d.province_code <= "52"): return {"error": f"province {d.province_code} out of Spain range (bad postcode)", "ingested": 0}`. Adicional :45-46 gate `if d is None or not d.province_code`.

#### (b) El mecanismo al atomo
Dos capas ES-acopladas, ambas en el borde extract/normalize (la resolucion fina pertenece a 06-geo):
1. **EXTRACCION** — cada parser deriva la region DENTRO de si, en dos sub-patrones: (a) **desde CP crudo** -> `zip[:2]` (AS24 :232) o `re.sub(\D,"")[:2]` (autocasion :200-203), explotando la coincidencia de que los 2 primeros digitos del CP español == codigo provincia INE; (b) **desde un id de provincia ya-INE de la fuente** (coches.net `mainProvinceId`, coches.com `currentProvince.id`), validado al rango `1..52`. Ambos emiten un codigo INE de 2 digitos zero-padded.
2. **GATE de ingest** (:49-50) — `province_code.isdigit() ∧ "01" <= code <= "52"` (comparacion lexicografica de strings); rechaza fuera de rango como `"out of Spain range (bad postcode)", ingested:0`.
El parser **no emite region cruda**: ya cocina la regla ES. El gate **replica** el rango ES. La asimetria estructural: lo que el parser acepta y lo que el gate acepta estan ambos hardcodeados a la geografia ES, en 5 sitios.

#### (c) La costura ES->generico y su fix exacto
La costura es que la regla "`zip[:2]` == provincia INE ∧ rango 01..52 ∧ isdigit" vive incrustada en 4+ parsers Y en el gate de ingest. El borde extract/normalize solo debe **EMITIR region cruda**; el mapa lo posee 06-geo.
**Fix exacto:**
1. Cada parser emite `raw_region` (el CP crudo o el id de la fuente) SIN interpretarlo -> campos `postcode_raw` + `source_region_id` en el CanonicalVehicle ([faceta 11](#faceta-11)).
2. El formato + mapa CP->region lo posee el geo-adapter del pack (`LocaleProfile.postcode_to_region` + el backbone del pais).
3. El gate de ingest se vuelve **pack-driven**: en vez de `01<=code<=52 ∧ isdigit`, valida contra `LocaleProfile.subdivision_set` (ISO 3166-2 del pais) -> acepta alfa (IT "MI"/"RM"), anchos distintos (DE 5-dig Kreis, FR "971"-"976"), conteos distintos (FR 101, IT 107, DE 16, JP 47, MX 32).
4. **Mismo PR** borra `zip[:2]`/`01..52`/`isdigit&52` de los 4 parsers y del gate; `xfail`-strict protege ES hasta verde (paridad byte-identica sobre los CP ES). Arreglar uno sin el otro deja "region escrita-pero-no-aceptada".

#### (d) El riesgo adversarial concreto (el mas grave de la etapa)
- **FR "75008"** -> `zip[:2]="75"` validado como provincia ES -> Paris guardado como provincia ES-75 inexistente/equivocada. CRITICAL geo-corruption.
- **DE PLZ "53000"-"99999"** -> "53"-"99" fuera de 01..52 -> **RECHAZADOS** ("out of Spain range, ingested:0"); los <=52 mal-mapeados a provincia ES.
- **IT "MI"/"RM"/"TO"** -> `isdigit()==False` -> TODO dealer IT devuelve "out of Spain range, ingested:0" — **fallo TOTAL disfrazado de "sin inventario"** (invisible al operador).
- **JP 01-47 subset 01-52** -> Tokyo "13" -> Ciudad Real "13". **Corrupcion geo SILENCIOSA**: pasa el gate, mapea a una provincia ES real equivocada — el peor caso (no falla, miente).
- **PT "NNNN-NNN"** -> `re.sub(\D,"")[:2]` coge los 2 primeros del codigo de 7 digitos -> unidad geografica equivocada.
- **Ruido** UK "SW1A 1AA" / CP con espacios o guiones -> `isdigit()==False` -> rechazo.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado:** (i) `grep` de `zip[:2]`/`01..52`/`isdigit&52` en parsers + ingest == 0; (ii) el parser emite region cruda y el pack decide formato+rango+mapa; (iii) el gate valida contra el `subdivision_set` del pais.
**Multi-via:** (1) **golden ES byte-identico** — los CP ES siguen mapeando a la misma provincia INE (0 drift sobre los ~431k cdp_code vivos); (2) **per-country sanity** — `|subdivisions|` DE/FR/IT/MX/JP == 16/101/107/32/47 cruzado contra una segunda fuente (iso3166 / Wikipedia ground-truth); (3) **adversarial** — dataset FR"75008"/IT"MI"/JP"13"/DE"53111": cada uno mapea a su region nacional correcta o se marca honestamente "region desconocida", NUNCA a una provincia ES; (4) **via ortogonal** — region derivada por el geo-adapter vs reverse-geocode point-in-polygon (PostGIS) deben converger.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
- **Primaria: pycountry** (LGPL-2.1, €0) — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]. Empaqueta el dataset Debian iso-codes (ISO 3166-1/-2 + ISO 4217): el conteo y el ancho de las subdivisiones de primer nivel de CADA pais se vuelven DATOS, alimentando un seal-manifest por pais (`geo_unit_level`, `geo_unit_width`, caps derivados del conteo). Reemplaza el gate `01..52 ∧ isdigit` (centinela ES) por validacion contra la autoridad ISO 3166-2 del pais — country-proof y self-pinning. Uso en build/config-time (no hot-path) -> la LGPL no contamina; opcion estricta-permisiva: `iso3166` (MIT) + raw iso-codes JSON.
- **Complementos:** **GeoNames backbone** (CC-BY 4.0, €0) — https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377] para el mapa CP/region OFICIAL por pais (allCountries.zip + hierarchy.zip, aplanado N-niveles->3-slots); y **libpostal** (MIT, €0) [VERIFIED NEXT-LEVEL.md:41/:471] para parsear direcciones multilingues entrenado (no regex curado) cuando el CP no basta para fijar la region.

#### Resolución condensada — Faceta 21
- **Costura** · La regla ES 'postcode[:2] == codigo provincia INE ∧ rango 01..52 ∧ isdigit' esta incrustada DOS veces: en la EXTRACCION (4+ parsers derivan region dentro de si: autoscout24.py:232 zip[:2]; autocasion_wholesale.py:195-206 re.sub(\D,'')[:2]+01..52; coches_net_wholesale.py:190-201 y coches_com_wholesale.py:276-282 id 1..52) Y en el GATE de ingest (ingest.py:49-50 isdigit & '01'<=code<='52'). El parser NO emite region cruda: ya cocina la geografia ES; el gate replica el rango ES y rechaza el resto como 'bad postcode'.
- **Fix** · 1) Cada parser emite raw_region (CP crudo o source_region_id) SIN interpretar -> campos postcode_raw + source_region_id en CanonicalVehicle ([faceta 11](#faceta-11)). 2) El formato+mapa CP->region lo posee el geo-adapter del pack (LocaleProfile.postcode_to_region + backbone). 3) Gate de ingest pack-driven: validar contra LocaleProfile.subdivision_set (ISO 3166-2) en vez de 01..52/isdigit -> acepta alfa (IT 'MI'), anchos (DE 5-dig, FR '971'), conteos (FR 101/IT 107/DE 16/JP 47/MX 32). 4) Mismo PR borra zip[:2]/01..52/isdigit&52 de los 4 parsers y del gate; xfail-strict protege ES (paridad byte-identica) — arreglar uno sin el otro deja la asimetria viva.
- **Adversarial** · CRITICAL multipais: FR '75008' -> zip[:2]='75' validado como provincia ES -> Paris guardado mal. DE PLZ 53000-99999 -> '53'-'99' RECHAZADOS, <=52 mal-mapeados. IT 'MI'/'RM' isdigit()=False -> TODO dealer IT 'out of Spain range, ingested:0' (fallo total disfrazado de 'sin inventario'). JP 01-47 subset 01-52 -> Tokyo '13' -> Ciudad Real '13' (corrupcion SILENCIOSA: pasa el gate, mapea a provincia ES real equivocada). PT 'NNNN-NNN' coge la unidad equivocada. Ruido UK 'SW1A 1AA' isdigit False -> rechazo.
- **Sellado (multi-vía)** · (i) grep de zip[:2]/01..52/isdigit&52 en parsers + ingest == 0. (ii) El parser emite region cruda; el pack decide formato+rango+mapa. (iii) El gate valida contra el subdivision_set del pais. Multi-via: (1) golden ES byte-identico (0 drift sobre ~431k cdp_code); (2) |subdivisions| DE/FR/IT/MX/JP == 16/101/107/32/47 cruzado contra iso3166/Wikipedia; (3) adversarial FR'75008'/IT'MI'/JP'13'/DE'53111' mapea a region nacional correcta o 'desconocida', NUNCA a provincia ES; (4) region del geo-adapter vs reverse-geocode point-in-polygon (PostGIS) convergen.
- **Herramienta NEXT-LEVEL (€0)** · pycountry (LGPL-2.1, €0) https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530] — dataset iso-codes ISO 3166-2: el conteo y ancho de las subdivisiones de cada pais como DATOS -> seal-manifest por pais; reemplaza el gate 01..52 (centinela ES) por la autoridad ISO 3166-2, country-proof y self-pinning; uso build-time (LGPL no contamina; alt estricta iso3166 MIT). Complementos: GeoNames backbone (CC-BY 4.0, €0) https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:377] para el mapa CP->region oficial por pais; libpostal (MIT, €0) [VERIFIED NEXT-LEVEL.md:471] para direcciones multilingues entrenado (no regex curado).

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-22"></a>

### Faceta 22 — Decodificación de charset/encoding de la página fuente

> **F8 · ENCODING non-UTF-8.** `.decode('utf-8')` hardcodeado en fetch; Shift-JIS→mojibake SILENCIOSO (`errors='replace'`). MP7. **Cross-ref:** facetas [10](#faceta-10)·[13](#faceta-13).

#### (a) Code_hints [VERIFIED]
- `pipeline/sources/autoscout24.py:74` `return r.read().decode("utf-8", "replace")` — `fetch_page` decodifica los BYTES de la pagina asumiendo UTF-8 [VERIFIED].
- `autoscout24.py:259` MISMO `.decode("utf-8", "replace")` hardcodeado en `collect_dealer_slugs` [VERIFIED].
- `pipeline/sources/autocasion_census.py:70` mismo decode utf-8 replace hardcodeado [VERIFIED grep].
- `pipeline/util/encoding.py:25-46` `force_utf8_stdout()` reconfigura SOLO el STDOUT (`stream.reconfigure(encoding='utf-8', errors='replace')`) — hoy un util CENTRAL compartido (el docstring `:16` nota que las copias per-file se dejan a proposito) [VERIFIED grep].
- grep: CERO hits de `shift_jis` / `euc-jp` / `apparent_encoding` / `charset_normalizer` / `chardet` en todo `pipeline/` [VERIFIED].
- `pipeline/geo.py:52` y `identity/*` hacen `unicodedata.normalize('NFKD',...).encode('ascii','ignore')` — eso es TRANSLITERACION de un string YA decodificado, NO el decode bytes->text (problema distinto) [VERIFIED grep].

#### (b) Mecanismo al atomo
El path de fetch es bytes -> text en UN paso: `urllib...read().decode('utf-8','replace')`. El codec esta HARDCODEADO a UTF-8 con `errors='replace'`. NO hay inspeccion del charset del header Content-Type, ni sniff de `<meta charset>`, ni fallback `apparent_encoding`. El handler 'replace' implica que una pagina no-UTF-8 NO crashea — cada byte indecodificable se vuelve U+FFFD, corrompiendo SILENCIOSAMENTE titulos/make/model. `force_utf8_stdout` solo arregla el stream de SALIDA (para que la consola imprima UTF-8), jamas el decode de ENTRADA. La unica razon de que ES/AS24 funcione es que las fuentes ES sirven UTF-8 por casualidad.

#### (c) Costura ES->generico
La costura es el codec `'utf-8'` hardcodeado en la frontera de fetch. Las fuentes ES son UTF-8 asi que la asuncion se sostiene por suerte; un mercado que sirve Shift-JIS/EUC-JP (JP) o ISO-8859 legacy (sitios EU viejos) se decodifica como UTF-8-replace -> mojibake. El fix: decodificar usando el charset DECLARADO por la fuente (header Content-Type, luego `<meta charset>`, luego deteccion estadistica) en la frontera de fetch, ANTES de parsear. Mejor via: enrutar el fetch por un cliente HTTP real (primp/curl_cffi) cuyo `.text` honra el charset de la respuesta, o anadir un helper de decode que lea header/meta y caiga a deteccion en vez de un `.decode('utf-8')` pelado.

#### (d) Riesgo adversarial concreto
Una pagina JP en Shift-JIS decodificada como UTF-8-replace -> titulos basura (cada kanji multibyte -> U+FFFD) -> make/model irrecuperables, el rung web generico no encuentra nada, y como `errors='replace'` NO hay crash: el dano es SILENCIOSO (corrompe, nunca lanza). Paginas DE/EU-viejas en ISO-8859-1 mis-decodifican acentos (ä/ö/ü/ß) -> claves canonicas erroneas -> entidades falso-distintas o falso-fundidas aguas abajo. Reconfigurar solo el stdout (el trabajo 'utf-8' actual) no toca el decode de entrada, asi que la corrupcion silenciosa es invisible en logs.

#### (e) Sellado + verificacion multi-via
Criterio: el decode de pagina usa el charset declarado/detectado por la fuente (no un utf-8 hardcodeado), verificado extremo-a-extremo para que titulos/make/fuel lleguen al normalizador como Unicode correcto para cualquier mercado. Multi-via: (1) golden — un fixture Shift-JIS decodifica al titulo kanji correcto (assert cero U+FFFD), un fixture DE ISO-8859-1 decodifica ä/ö/ü/ß bien, y un fixture ES UTF-8 byte-identico a hoy (cero regresion ES); (2) adversarial — una pagina cuyo Content-Type MIENTE (declara utf-8 pero es Shift-JIS) la caza el fallback meta/estadistico; (3) independiente — round-trip: el texto decodificado re-codificado al charset detectado reproduce los bytes originales en una muestra (prueba que la eleccion de codec fue correcta), cross-checkeado contra la confianza de charset-normalizer.

#### (f) Herramienta NEXT-LEVEL
NO existe libreria dedicada de decode de charset en NEXT-LEVEL.md [VERIFIED — grep de la biblia por charset/encoding/chardet/ftfy/mojibake/charset_normalizer devuelve solo DVC, Great Expectations, structured-extraction, transliteracion(anyascii) y Frictionless; ninguna decodifica bytes->text por charset]. anyascii (ISC, biblia:224/329) es TRANSLITERACION de Unicode ya decodificado (CJK->latino), NO decode de byte-charset — no resuelve esta faceta. La palanca IN-BIBLIA mas cercana es el upgrade de transporte de fetch primp (Rust) — MIT — https://github.com/deedy5/primp [VERIFIED NEXT-LEVEL.md:296]: un cliente HTTP real cuyo `response.text` decodifica usando el charset declarado (como requests/httpx), reemplazando el `.decode('utf-8')` hardcodeado de urllib de modo que el charset se honra como efecto colateral del upgrade de breadth Tier-0. La herramienta dedicada canonica para deteccion bytes->text es charset-normalizer (MIT, la que usa `requests`) — [ASSUMED: NO catalogada en NEXT-LEVEL.md], a anadir como el detector explicito de `decode_page`.

#### Resolución condensada — Faceta 22
- **Costura** · El codec 'utf-8' hardcodeado en la frontera de fetch: autoscout24.py:74 y :259, autocasion_census.py:70 hacen r.read().decode('utf-8','replace') sin mirar el charset del header Content-Type ni <meta>. force_utf8_stdout (util/encoding.py:25) solo arregla el STDOUT de salida, no el decode de entrada. Las fuentes ES son UTF-8 por suerte; cero manejo de shift_jis/euc-jp/apparent_encoding en todo pipeline (grep VERIFIED).
- **Fix** · Reemplazar el .decode('utf-8','replace') hardcodeado (autoscout24.py:74,:259; autocasion_census.py:70; y demas decodes urllib crudos) por un decode_page(raw_bytes, content_type_header) central en pipeline/util/encoding.py que: (1) parsee el charset del Content-Type; (2) si falta, sniffee <meta charset>/<meta http-equiv> de los primeros bytes; (3) si sigue desconocido, corra deteccion estadistica (charset-normalizer) y use el mejor guess; (4) decodifique con el codec resuelto, errors='replace' solo como ultimo recurso. Mejor: migrar el transporte Tier-0 a primp/curl_cffi y usar response.text (charset automatico). LocaleProfile puede llevar un page_encoding_hint opcional por mercado (p.ej. JP fallback Shift-JIS). force_utf8_stdout se queda (resuelve el problema de salida, distinto).
- **Adversarial** · Pagina JP Shift-JIS decodificada como UTF-8-replace -> titulos basura (cada kanji -> U+FFFD) -> make/model irrecuperables, el rung web no encuentra nada; como errors='replace' NO crashea: dano SILENCIOSO (corrompe, nunca lanza). DE/EU-viejas en ISO-8859-1 mis-decodifican ä/ö/ü/ß -> claves canonicas erroneas -> entidades falso-distintas/fundidas. Reconfigurar solo stdout no toca el decode de entrada -> invisible en logs.
- **Sellado (multi-vía)** · El decode usa el charset declarado/detectado (no utf-8 hardcodeado), verificado extremo-a-extremo. Multi-via: (1) golden: fixture Shift-JIS -> titulo kanji correcto (assert cero U+FFFD), fixture DE ISO-8859-1 -> ä/ö/ü/ß bien, fixture ES UTF-8 byte-identico (cero regresion ES); (2) adversarial: Content-Type que miente (declara utf-8, es Shift-JIS) cazado por fallback meta/estadistico; (3) independiente round-trip: texto re-codificado al charset detectado reproduce los bytes originales, cross-check vs confianza charset-normalizer.
- **Herramienta NEXT-LEVEL (€0)** · NO hay libreria dedicada de decode de charset en NEXT-LEVEL.md [VERIFIED grep: solo DVC, Great Expectations, structured-extraction, anyascii, Frictionless; ninguna decodifica bytes->text por charset]. anyascii (ISC) es transliteracion de Unicode ya decodificado, NO decode de charset. Palanca in-biblia mas cercana: primp (Rust) — MIT — https://github.com/deedy5/primp [VERIFIED NEXT-LEVEL.md:296], cliente HTTP cuyo response.text honra el charset declarado, reemplazando el .decode('utf-8') de urllib. Canonica dedicada: charset-normalizer (MIT, la de requests) [ASSUMED: no catalogada en la biblia], a anadir como detector de decode_page.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-23"></a>

### Faceta 23 — Enrutado de paths por país + round-trip write/read + integridad de persistencia

> **Asimetría write/read (persistencia).** Escritura per-país pero `complete.py` ES-soldado (`^CDP-ES-`, `countries/ES`) ⇒ G1 6º blocker. **Cross-ref:** facetas [1](#faceta-1)·[7](#faceta-7)·[26](#faceta-26).

#### (a) Verificacion de code_hints contra el codigo real
- [VERIFIED pipeline/paths.py:22] `DEFAULT_COUNTRY = "ES"`.
- [VERIFIED pipeline/paths.py:30] `_CDP_COUNTRY_RE = re.compile(r"^CDP-([A-Z]{2})-")` — **YA generico** (cualquier 2-letras).
- [VERIFIED pipeline/paths.py:33-63] helpers `recipe_root`/`recipes_flat_dir`/`data_root`/`census_dir` todos `country_code: str = DEFAULT_COUNTRY`; `country_of_cdp` (:55-63) fallback a DEFAULT_COUNTRY.
- [VERIFIED pipeline/recipe.py:69] `out_dir = recipes_flat_dir(country_of_cdp(cdp_code), root=ROOT)` — **ESCRIBE por pais**.
- [VERIFIED pipeline/recipe.py:76-79] round-trip self-check: `if yaml.safe_load(body) != recipe: raise ValueError(...)`.
- [VERIFIED pipeline/recipe.py:83-91] clobber-log: compara `old_recipe != recipe` y `log.warning` el sobrescribir.
- [VERIFIED pipeline/complete.py:89] `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — **ES-HARDCODED** (un SEGUNDO regex, distinto del generico de paths.py).
- [VERIFIED pipeline/complete.py:305] `for candidate in (root / "countries" / "ES").glob(f"**/{cdp_code}/recipe.yaml")` — **ES fijo**.
- [VERIFIED pipeline/complete.py:309] `flat = root / "countries" / "ES" / "recipes" / f"{cdp_code}.yaml"` — **ES fijo**.

#### (b) El mecanismo al atomo
**Asimetria write/read.** El lado de ESCRITURA ya es generico: `recipe.py:69` deriva el pais del cdp_code (`country_of_cdp` via el `_CDP_COUNTRY_RE` generico `^CDP-([A-Z]{2})-`) y escribe bajo `countries/<CC>/recipes/`. El lado de LECTURA esta ES-soldado por DUPLICADO: `complete.py` tiene su PROPIO `_CDP_CODE_RE` `^CDP-ES-` (:89) y dos paths con `"ES"` literal (:305 glob, :309 flat). Atomo: una receta DE se escribe correctamente en `countries/DE/recipes/CDP-DE-NN-XXXX.yaml`, pero `complete.py:305/309` SOLO mira `countries/ES/` -> invisible; y aunque se encontrara, `_CDP_CODE_RE:89` `^CDP-ES-` la rechazaria. Resultado: **G1 6o blocker** — ningun dealer no-ES pasa jamas a COMPLETED.

#### (c) Costura ES->generico + fix exacto
- **Costura:** `complete.py` mantiene un regex ES-locked (:89) y dos paths ES-fijos (:305,:309) que DUPLICAN y CONTRADICEN el routing generico de `paths.py`; write=per-country, read=ES-only.
- **Fix (TODO en el MISMO PR — arreglar uno sin el otro deja receta escrita-pero-no-encontrada):** (1) `complete.py:89` -> reusar el regex generico de `paths.py` (`^CDP-([A-Z]{2})-...`), eliminando el duplicado ES. (2) `complete.py:305/309` -> sustituir el literal `"ES"` por `country_of_cdp(cdp_code)` reusando `paths.recipe_root`/`recipes_flat_dir`: `recipe_root(country_of_cdp(cdp_code), root=root).glob(...)` y `recipes_flat_dir(country_of_cdp(cdp_code), root=root)/f"{cdp_code}.yaml"`. (3) **xfail strict** sobre un fixture ES protege la baseline hasta verde (cero regresion en los CDP-ES- existentes). (4) La integridad de `write_recipe` (round-trip self-check :76-79 + clobber log :83-91) ya existe; extender el self-check a "lo escrito en `countries/<CC>/` es localizable por el reader de `<CC>`".

#### (d) Riesgo adversarial concreto
- `complete.py:89` `^CDP-ES-` -> un dealer **DE/FR/IT/PT/JP** nunca matchea -> nunca pasa a COMPLETED (G1 6o blocker): fallo TOTAL del onboarding del pais #2 disfrazado de "identity gap".
- `complete.py:305/309` `"ES"` fijo -> una receta DE escrita en `countries/DE/` es **invisible** al completar, aunque sea byte-perfecta.
- **Desacoplar el fix** REINTRODUCE la asimetria: regex generico + path ES = el dealer DE pasa el regex pero su receta no se encuentra; path generico + regex ES = se encuentra pero el codigo se rechaza.
- **Ruido:** un cdp_code malformado (`CDP-XX-` sin cuerpo Crockford valido) debe caer a DEFAULT_COUNTRY sin crashear (`country_of_cdp` ya lo hace, :62-63), pero al widenear `complete.py:89` hay que PRESERVAR la validacion del cuerpo Crockford `[0-9A-HJKMNP-TV-Z]{8}` (no aflojar el guard al genericar el CC).

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** write y read **simetricos por pais** — toda receta escrita en `countries/<CC>/` es localizable por `complete.py` para ese `<CC>`; `complete.py` NO contiene ningun literal `"ES"` ni regex `^CDP-ES-`; baseline ES byte-identica (xfail strict verde).
- **Via 1 (test):** round-trip: `write_recipe(CDP-DE-NN-XXXX)` -> `complete.py` lo encuentra y valida; idem ES (cero regresion).
- **Via 2 (adversarial):** in-toto: editar el YAML post-escritura -> la verificacion de la cadena DETECTA la manipulacion (persistencia tamper-evident).
- **Via 3 (independiente):** Frictionless valida que el pack `countries/<CC>/` conforma el contrato de estructura (existe `recipes/`, cdp_code shape correcto) ANTES de que el reader lo busque — el "esta-discoverable" deja de ser esperanza y es contrato.

#### (f) Herramienta NEXT-LEVEL
**in-toto** — [VERIFIED NEXT-LEVEL.md:312] https://github.com/in-toto/in-toto, **Apache-2.0, EUR0=True**. *certifiable-recipe-provenance*: eleva la integridad de persistencia de "round-trip self-check en proceso" a "recibo firmado, hash-chained, tamper-evident, verificable por tercero" del par escrito<->leido, sin retener crudo (compatible sample-verify-delete). Verificacion (NEXT-LEVEL.md:315): in-toto-verify ACEPTA atestacion intacta y RECHAZA parse_loss/hash alterado; editar el YAML post-sello -> la cadena DETECTA la manipulacion. **Complemento de routing:** **Frictionless Framework** — [VERIFIED NEXT-LEVEL.md:337] https://github.com/frictionlessdata/frictionless-py, **MIT, EUR0=True**: declara el pack `countries/<CC>/` como contrato de datos auto-verificado, asegurando que la estructura per-pais es valida y discoverable antes del lookup. Ambos CPU puro, pip-install.

#### Resolución condensada — Faceta 23
- **Costura** · Asimetria write/read: la ESCRITURA ya es generica (recipe.py:69 escribe bajo countries/<CC>/ via country_of_cdp + el _CDP_COUNTRY_RE generico '^CDP-([A-Z]{2})-' de paths.py:30), pero la LECTURA esta ES-soldada por DUPLICADO: complete.py tiene su propio _CDP_CODE_RE '^CDP-ES-' (:89) y dos paths 'ES' literal (:305 glob, :309 flat). Una receta DE escrita correctamente es invisible al completar.
- **Fix** · TODO en el MISMO PR (arreglar uno sin el otro deja receta escrita-pero-no-encontrada): 1) complete.py:89 -> reusar el regex generico de paths.py (^CDP-([A-Z]{2})-...), eliminar el duplicado ES, preservando el cuerpo Crockford [0-9A-HJKMNP-TV-Z]{8}. 2) complete.py:305/309 -> reemplazar literal 'ES' por country_of_cdp(cdp_code) reusando paths.recipe_root/recipes_flat_dir. 3) xfail strict sobre fixture ES protege la baseline hasta verde. 4) extender el round-trip self-check de write_recipe (recipe.py:76-79) a 'escrito en countries/<CC>/ == localizable por el reader de <CC>'.
- **Adversarial** · complete.py:89 '^CDP-ES-' => dealer DE/FR/IT/PT/JP nunca matchea, nunca COMPLETED (G1 6o blocker): fallo total del onboarding pais #2 disfrazado de 'identity gap'. complete.py:305/309 'ES' fijo => receta DE en countries/DE/ invisible aunque byte-perfecta. Desacoplar el fix reintroduce la asimetria (regex generico+path ES, o path generico+regex ES). cdp_code malformado debe caer a DEFAULT_COUNTRY sin crashear; al widenear el CC hay que preservar el guard Crockford.
- **Sellado (multi-vía)** · Sello: write/read simetricos por pais — toda receta en countries/<CC>/ localizable por complete.py para ese CC; complete.py sin ningun literal 'ES' ni regex '^CDP-ES-'; baseline ES byte-identica (xfail strict verde). Multi-via: (1) round-trip write_recipe(CDP-DE-NN-XXXX) => complete.py lo encuentra y valida, idem ES; (2) adversarial = in-toto detecta edicion del YAML post-escritura (tamper-evident); (3) independiente = Frictionless valida que el pack countries/<CC>/ conforma el contrato de estructura ANTES del lookup.
- **Herramienta NEXT-LEVEL (€0)** · in-toto [VERIFIED NEXT-LEVEL.md:312] https://github.com/in-toto/in-toto Apache-2.0 EUR0=True (certifiable-recipe-provenance): integridad de persistencia firmada, hash-chained, tamper-evident del par escrito<->leido sin crudo; in-toto-verify rechaza parse_loss/hash alterado (NEXT-LEVEL.md:315). Complemento: Frictionless Framework [VERIFIED NEXT-LEVEL.md:337] https://github.com/frictionlessdata/frictionless-py MIT EUR0=True declara countries/<CC>/ como contrato auto-verificado (discoverable antes del lookup). CPU puro, pip-install.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-24"></a>

### Faceta 24 — Seam capa-2 IA local (`NormalizerLLM` dormante €0 + gate GBNF)

> **Capa-2 IA local · seam dormante €0.** `llm_local` es un nombre sin cuerpo (grep 0 código). **Gate O1 (€>0, PENDING-OWNER).** **Cross-ref:** facetas [17](#faceta-17)·[13](#faceta-13)·[18](#faceta-18)·[19](#faceta-19).

#### (a) Verificacion de code_hints [VERIFIED]
- **`llm_local` solo enum + disclaimer** [VERIFIED via grep `llm_local|grammar|gbnf|gguf|ollama|outlines|NormalizerLLM` en `pipeline/`]: UNICOS hits = `recipe_schema.py:66` (docstring "§4 cost ladder: structured -> css selectors -> llm_local"), `recipe_schema.py:67` (`engine: str = "next_data"  # next_data | jsonld | css | llm_local`), `recipe_harness.py:229` (disclaimer). Los 2 hits "grammar" en `motorflash_wholesale.py:89,97` son URL/sitemap grammar (comentarios), **NO LLM**. **CERO codigo ejecutable**: no `NormalizerLLM`, no `gbnf`, no `gguf`, no `ollama`, no `outlines`, no `llama_cpp`.
- **Disclaimer del replay** `recipe_harness.py:228-231` [VERIFIED]: "a fully field-map-driven interpreter (... incl. the §4 css/llm_local ladder) is deliberately NOT claimed here". El interprete + la capa-2 estan explicitamente NO reclamados.
- **Contrato Law I** `make_normalizer.py:57-76` [VERIFIED]: under-fill > mis-fill (`:74-75` preserve, do not guess) — el contrato que el LLM DEBE respetar (jamas un make adivinado).

#### (b) Mecanismo al atomo
Hoy `'llm_local'` es SOLO un string en el enum `Parsing.engine` (`recipe_schema.py:67`) y una mencion en el disclaimer del replay (`recipe_harness.py:229`). No hay `NormalizerLLM`, ni gramatica, ni runtime. **El seam es un NOMBRE sin cuerpo.** El 360 = pre-cablearlo €0, dormante, sin tocar el motor.

#### (c) Diseno 360 + costura ES->generico + fix exacto
**Diseno del seam (dormante, €0, determinista-primero):**
- **`NormalizerLLM` Protocol** con un metodo `recover(raw_fields, LocaleProfile)->partial CanonicalVehicle` y una impl default **`NullNormalizerLLM`** que devuelve "sin recuperacion" -> el fallback determinista SIEMPRE gana hoy; el motor es identico con o sin modelo.
- **Gate Law-I (determinista-primero):** invocar el seam SII (`make` O `model` NULL tras `normalize_vehicle`) Y rung ∈ `{css, regex}` Y piso `make ∈ brand_table`. JAMAS toca un `next_data`/`json_api` que ya trae make/model limpios.
- **Salida POR GRAMATICA:** GBNF/JSON-Schema cuyos terminales = `brand_table` ∪ enums fuel/transmission del pack -> fisicamente imposible emitir fuera del vocabulario (Outlines compila el schema en un FSM que restringe llama.cpp/vLLM/Ollama).
- La gramatica es **por-IDIOMA** (terminales = marcas/enums del pais), no universal.

**Costura:** el seam es la pieza mas country-agnostica SI se cablea bien: Protocol + fallback son country-blind; solo la GRAMATICA (terminales) es dato del pack. El riesgo es cablearlo ES-acoplado (prompt en espanol, lista ES en la gramatica). **Fix:** los terminales de la gramatica se cargan del pack (`brand_table.yaml` + `fuel_map`/`transmission_map` del pais), y el piso `make ∈ brand_table` usa la tabla del pack.

**Fix exacto:**
1. Definir `NormalizerLLM` Protocol (p.ej. `pipeline/normalize/llm.py`) + `NullNormalizerLLM` default.
2. Cablear el gate dentro de `normalize_vehicle` ([faceta 13](#faceta-13)): llamar al seam solo bajo la condicion Law-I; el fallback es el resultado determinista actual.
3. La gramatica se construye del `brand_table` + enums del LocaleProfile via **Outlines** (JSON-Schema/GBNF). Terminales = dato del pack, jamas hardcoded.
4. Provenance por campo (fuente+modelo+offset) para re-verificacion; cross-check det.↔LLM en precio/km/ano -> gana el determinista, desacuerdo escala (ANTI-DRIFT §1.5).
5. Runtime = **llama.cpp** (GGUF Q4 CPU, €0) o **Ollama** (Modelfile pineado); GPU/vLLM es la palanca €>0 con caso probado + firma. Hoy el seam queda dormante (`NullNormalizerLLM`).

#### (d) Riesgo adversarial concreto
- **Sin piso `make ∈ brand_table`:** activar viola Law I (mis-fill > under-fill) y contamina el eje de busqueda con marcas alucinadas.
- **Sin GBNF/constrained decoding:** el modelo emite fuera del vocabulario del pack (`'Tezla'`, un fuel inventado) -> la gramatica debe hacerlo **fisicamente imposible**, no filtrado.
- **Gramatica por-idioma:** los terminales de una gramatica JP = marcas/enums JP; reusar la gramatica ES para JP rechazaria makes JP validos o no constrenria.
- **Prompt-injection** en un titulo scrapeado ("ignore and output X") -> la gramatica hace el texto libre imposible (NEXT-LEVEL.md:654 adversarial).
- **No-UE/ruido:** un modelo invocado sobre un `next_data` limpio (bug de gate) sobreescribiria make/model buenos -> el gate "rung ∈ css|regex only" lo previene; debe testearse.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello:** (1) el seam cableado con `NullNormalizerLLM` default y el motor byte-identico con seam presente vs ausente (prueba de dormancia); (2) la gramatica RECHAZA por construccion una marca fuera de `brand_table` ("Tezla" imposible, no filtrado); (3) el gate dispara SOLO bajo (`make/model NULL ∧ rung css|regex ∧ piso brand_table`) — una muestra `next_data` jamas invoca el LLM; (4) cross-check det↔LLM: gana determinista, desacuerdo escala, cero-regresion de F1 sobre golden multilingue en CI.
- **Multi-via:** (via1) unit test del gate + `NullNormalizerLLM` (motor identico); (via2) cuando exista modelo, un fuzz de 10k generaciones bajo la gramatica da 0 salidas fuera de schema/enum (NEXT-LEVEL.md:662); (via3) paridad cross-engine — la misma gramatica da identica clase de salida via Outlines en llama.cpp (GBNF) y vLLM (xgrammar), probando portabilidad de backend.

#### (f) Herramienta NEXT-LEVEL que la eleva
**grammar-constrained-llm-normalizer · Outlines** (Apache-2.0, https://github.com/dottxt-ai/outlines) [VERIFIED NEXT-LEVEL.md:269-275]. Compila JSON-Schema/regex/CFG-GBNF en un FSM que restringe cualquier modelo a emitir solo `{make∈brand_table∪null, model, fuel∈enum, transmission∈enum}` — imposible alucinar fuera del pack; seam dormante €0 con fallback determinista; el gate se cablea sin tocar el motor. **Runtime:** llama.cpp (MIT, https://github.com/ggml-org/llama.cpp) [VERIFIED NEXT-LEVEL.md:648-651] GGUF Q4 CPU, GBNF nativo, piso €0; Ollama (MIT, https://github.com/ollama/ollama) [VERIFIED NEXT-LEVEL.md:652] Modelfile pineado reproducible; vLLM (Apache-2.0, https://github.com/vllm-project/vllm) [VERIFIED NEXT-LEVEL.md:652] palanca GPU €>0. **Pre-filtro:** lark (MIT, https://github.com/lark-parser/lark) [VERIFIED NEXT-LEVEL.md:277-283] parsea el titulo por EBNF ANTES del LLM, reduciendo lo que toca IA al residuo irreducible (Law-I, €0). **Gateway opcional:** LiteLLM (MIT, https://github.com/BerriAI/litellm) [VERIFIED NEXT-LEVEL.md:664-670] routing_config[country]+budget caps; RouteLLM (Apache-2.0, https://github.com/lm-sys/RouteLLM) [VERIFIED NEXT-LEVEL.md:672-678] router aprendido barato-vs-fuerte; Instructor (MIT, https://github.com/567-labs/instructor) [VERIFIED NEXT-LEVEL.md:680-686] self-repair lado-aplicacion.

#### Resolución condensada — Faceta 24
- **Costura** · El seam es un NOMBRE sin cuerpo: 'llm_local' existe SOLO como valor de enum (recipe_schema.py:66-67) y mencion en el disclaimer del replay (recipe_harness.py:228-231). Grep confirma CERO codigo ejecutable (no NormalizerLLM/gbnf/gguf/ollama/outlines/llama_cpp en pipeline/). La pieza es country-agnostica SI se cablea bien (Protocol+fallback country-blind); solo la gramatica (terminales) es dato del pack. Riesgo de costura: cablearlo ES-acoplado (prompt espanol, lista ES en la gramatica).
- **Fix** · Definir NormalizerLLM Protocol + NullNormalizerLLM default (pipeline/normalize/llm.py). Cablear el gate dentro de normalize_vehicle ([faceta 13](#faceta-13)): invocar SII (make O model NULL tras normalize) ∧ rung css|regex ∧ piso make∈brand_table; fallback = resultado determinista actual. Gramatica construida del brand_table+enums del LocaleProfile via Outlines (GBNF/JSON-Schema), terminales = pack data, jamas hardcoded. Provenance por campo + cross-check det↔LLM (gana determinista, desacuerdo escala). Runtime llama.cpp GGUF Q4 CPU €0 / Ollama Modelfile; GPU vLLM = palanca €>0. Hoy dormante (NullNormalizerLLM).
- **Adversarial** · Sin piso make∈brand_table: viola Law I (mis-fill>under-fill), contamina el eje con marcas alucinadas. Sin GBNF: emite fuera del vocabulario ('Tezla', fuel inventado) -> la gramatica debe hacerlo fisicamente imposible, no filtrado. Gramatica por-idioma: reusar la ES para JP rechaza makes JP validos. Prompt-injection en titulo scrapeado -> la gramatica hace el texto libre imposible (NEXT-LEVEL.md:654). Bug de gate invocando LLM sobre next_data limpio -> sobreescribe make/model buenos; el gate rung css|regex-only lo previene (testear).
- **Sellado (multi-vía)** · Sello: (1) seam cableado con NullNormalizerLLM default, motor byte-identico con seam presente vs ausente (dormancia); (2) la gramatica RECHAZA por construccion una marca fuera de brand_table ('Tezla' imposible, no filtrado); (3) gate dispara SOLO bajo make/model NULL ∧ rung css|regex ∧ piso brand_table — next_data jamas invoca LLM; (4) cross-check det↔LLM gana determinista, desacuerdo escala, cero-regresion F1 sobre golden multilingue en CI. Multi-via: unit test gate+NullNormalizerLLM (motor identico) | fuzz 10k generaciones bajo gramatica = 0 fuera de schema/enum (NEXT-LEVEL.md:662) | paridad cross-engine Outlines en llama.cpp GBNF vs vLLM xgrammar.
- **Herramienta NEXT-LEVEL (€0)** · grammar-constrained-llm-normalizer · Outlines (Apache-2.0, https://github.com/dottxt-ai/outlines) [VERIFIED NEXT-LEVEL.md:269-275] — compila JSON-Schema/regex/GBNF en FSM, restringe a {make∈brand_table∪null, model, fuel∈enum, transmission∈enum}, imposible alucinar; seam dormante €0 con fallback determinista. Runtime: llama.cpp (MIT, https://github.com/ggml-org/llama.cpp) [VERIFIED NEXT-LEVEL.md:648-651] GGUF Q4 CPU GBNF nativo €0; Ollama (MIT, https://github.com/ollama/ollama) [VERIFIED:652] Modelfile pineado; vLLM (Apache-2.0, https://github.com/vllm-project/vllm) [VERIFIED:652] palanca GPU. Pre-filtro: lark (MIT, https://github.com/lark-parser/lark) [VERIFIED:277-283]. Gateway: LiteLLM (MIT, https://github.com/BerriAI/litellm) [VERIFIED:664-670], RouteLLM (Apache-2.0, https://github.com/lm-sys/RouteLLM) [VERIFIED:672-678], Instructor (MIT, https://github.com/567-labs/instructor) [VERIFIED:680-686].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-25"></a>

### Faceta 25 — Fixtures golden/Ferrari/property-based por país

> **F11 · SEAL.** Los 11 tests son TODOS ES; sin `test_<source>_<CC>` ni property-based. SH4. **Cross-ref:** facetas [26](#faceta-26)·[13](#faceta-13)·[16](#faceta-16).

#### (a) Verificacion de code_hints [VERIFIED]
- **11 ficheros de test, TODOS ES git-tracked** [VERIFIED `git ls-files`]: `tests/test_recipe.py`, `test_recipe_harness.py`, `test_recipe_autocasion.py`, `test_recipe_coches_com.py`, `test_recipe_coches_net.py`, `test_recipe_extract_web.py`, `test_recipe_web_generic.py`, `test_price_sanity.py`, `test_make_normalizer.py`, `test_reshape_recipes.py` (10 recipe/normalizacion + harness).
- **golden ES hardcodeado** — `tests/test_recipe_coches_net.py:21` [VERIFIED]: fixture con `"price": {"amount": 14900}, "fuelType": "Gasolina"` — etiqueta ES literal incrustada. Tests `test_coches_net_is_registered` (`:32`), `test_coches_net_recipe_first_verified` (`:38`), `test_coches_net_empty_is_failed` (`:56`), todos **`monkeypatch`** (sin red, deterministas).
- **aseveran comportamiento ES**: el sello "tests verde" certifica **Espana**, no el pais onboarded. No hay `test_recipe_<source>_<CC>` ni property-based (`grep` Hypothesis/pandera 0 en tests).

#### (b) Mecanismo al atomo
La maquinaria de test actual es **golden por-ejemplo, country-blind**: cada test inyecta un fixture HTML/JSON **ES capturado** (p.ej. `fuelType:"Gasolina"`, precio EUR, CP INE) via `monkeypatch` y asevera el `Vehicle`/veredicto esperado **para ese ejemplo ES**. El atomo: el conjunto de fixtures **enumera casos ES** y nada genera los casos-borde de OTRO locale. "Verde en CI" == "ES parsea bien", no "el contrato de normalizacion se sostiene para todo input que el pack pueda producir".

#### (c) Costura ES->generico
Dos huecos: (1) **fixtures por pais** — falta maquinaria `test_recipe_<source>_<CC>` con HTML/JSON capturado determinista (sin red) espejando los ES, metida en CI `db-tests`/`unit`; (2) **property-based** — falta Hypothesis sobre los **invariantes de normalizacion** (`km>=0|None`, `parse_money idempotente y currency-tagged`, `make canonico ∈ brand_table∪verbatim`, `province valido-por-pais o escala`, `fuel_code ∈ enum`) GENERADOS adversarialmente, no enumerados. Fix exacto: anadir un job que (a) cargue fixtures por `<CC>` y (b) corra estrategias Hypothesis derivadas del esquema `CanonicalVehicle` (Pandera puede auto-derivarlas), congelando cada contraejemplo hallado como regression-fixture golden.

#### (d) Riesgo adversarial concreto
- **Sin fixtures por pais, el pais #2 entra a produccion con CERO cobertura determinista**: los golden ES **no ven** el separador invertido MX (`1,234.56`), el CP alfabetico IT (`MI`/`RM`), el titulo CJK JP (`トヨタプリウス`), el precio JPY sobre el techo EUR, el fuel `Benzin`/`Benzina`.
- **regresion silenciosa**: un cambio en `normalize_vehicle`/`parse_money`/`fuel_map` puede **romper el pais nuevo sin que ningun test rojo lo avise** (los ES siguen verdes).
- **combinatoria inabarcable a mano**: `(separador x divisa x formato-CP x script x techo)` no se cubre enumerando; solo un generador de propiedades lo barre.

#### (e) Criterio de sellado + verificacion multi-via
- **Sello**: (1) cada pais onboarded **trae sus fixtures deterministas** `test_recipe_<source>_<CC>` en CI; (2) las **propiedades de normalizacion verdes** en CI (no solo ejemplos ES); (3) cada contraejemplo de fuzzing **congelado como golden** (el fallo hallado queda probado tambien por ejemplo fijo).
- **Multi-via** (Hypothesis ES por construccion la 2a via adversarial del ritual): (i) **test** = propiedades verdes + fixtures `<CC>` verdes; (ii) **adversarial** = Hypothesis **MINIMIZA** al contraejemplo mas simple (p.ej. el menor precio MX que se corrompe 1000x) y **bloquea el merge**; (iii) **via independiente** = los contraejemplos se congelan como regression-fixtures deterministas, de modo que property-fuzzing y golden-por-ejemplo se corroboran mutuamente.

#### (f) Herramienta NEXT-LEVEL
**Hypothesis** (`property-based-recipe-fuzzing`) sintetiza adversarialmente separadores mixtos, postcodes no-INE (IT alpha, PT `NNNN-NNN`, JP 7-dig), titulos CJK, precios JPY sobre techo EUR — **exactamente los modos CRITICAL/HIGH que los 11 golden ES no ven** — y MINIMIZA al contraejemplo mas simple, bloqueando el merge. **Pandera** expresa el esquema `CanonicalVehicle` como el contrato que el fuzzer ataca y **auto-deriva estrategias Hypothesis**. Corren en el job `db-tests`/`unit` existente, CPU puro, EUR0. [VERIFIED NEXT-LEVEL.md:320 Hypothesis https://github.com/HypothesisWorks/hypothesis MPL-2.0; :321 pandera (integra Hypothesis)]

#### Resolución condensada — Faceta 25
- **Costura** · Los 10-11 ficheros de test son TODOS ES git-tracked (tests/test_recipe*.py, test_price_sanity.py, test_make_normalizer.py, test_reshape_recipes.py). Golden por-ejemplo country-blind: test_recipe_coches_net.py:21 hardcodea fixture ES 'fuelType':'Gasolina' precio EUR, monkeypatched (test_coches_net_is_registered/_recipe_first_verified/_empty_is_failed :32/:38/:56). 'Tests verde' certifica Espana, no el pais onboarded; no hay test_recipe_<source>_<CC> ni property-based (grep Hypothesis/pandera 0).
- **Fix** · Anadir maquinaria de fixtures POR PAIS (HTML/JSON capturado determinista, sin red) test_recipe_<source>_<CC> espejando los ES en CI db-tests/unit; anadir property-based (Hypothesis) sobre invariantes de normalizacion (km>=0|None, parse_money idempotente+currency-tagged, make ∈ brand_table∪verbatim, province valido-por-pais o escala, fuel_code ∈ enum) generados adversarialmente; Pandera auto-deriva estrategias desde el esquema CanonicalVehicle; congelar cada contraejemplo como regression-fixture golden.
- **Adversarial** · Sin fixtures por pais el pais #2 entra a produccion con CERO cobertura determinista: los golden ES no ven el separador invertido MX (1,234.56), el CP alfabetico IT (MI/RM), el titulo CJK JP (トヨタプリウス), el precio JPY sobre techo EUR, el fuel Benzin/Benzina. Un cambio en normalize_vehicle/parse_money/fuel_map rompe el pais nuevo sin test rojo (los ES siguen verdes). La combinatoria (separador x divisa x formato-CP x script x techo) es inabarcable enumerando.
- **Sellado (multi-vía)** · Sello: cada pais onboarded trae fixtures deterministas test_recipe_<source>_<CC> en CI + propiedades de normalizacion verdes (no solo ejemplos ES) + cada contraejemplo de fuzzing congelado como golden. Multi-via (Hypothesis = 2a via adversarial por construccion): (1) test: propiedades + fixtures <CC> verdes; (2) adversarial: Hypothesis minimiza al contraejemplo mas simple (menor precio MX que se corrompe 1000x) y bloquea el merge; (3) via independiente: contraejemplos congelados como regression-fixtures deterministas (property-fuzzing y golden se corroboran).
- **Herramienta NEXT-LEVEL (€0)** · Hypothesis (property-based-recipe-fuzzing) — MPL-2.0, EUR0 — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320]: genera separadores mixtos, postcodes no-INE, titulos CJK, precios JPY sobre techo EUR y minimiza al contraejemplo. Pandera (integra Hypothesis, auto-deriva estrategias del esquema CanonicalVehicle) [VERIFIED :321]. Corren en el job db-tests/unit existente.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-26"></a>

### Faceta 26 — Definición del SELLO de la etapa (normalization-aware)

> **F11 · SEAL count-only — meta-faceta.** Define el '100% del país'; hoy ES-shaped en 3 ejes (normalización/moneda/cross-stage) + evidencia 641-vs-61 mal atribuida. SH1·SH4·SH5·SH6. **Cross-ref:** facetas [8](#faceta-8)·[12](#faceta-12)·[21](#faceta-21)·[25](#faceta-25).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/recipe_harness.py:94-117` [VERIFIED] `decide_status` sella VERIFIED **solo sobre COUNT**: `fetched!=0 ∧ parsed!=0` (:108), `loss==0` (:110-111), `parsed >= min(target,k)` salvo full_dealer (:112-113), `verdict != REFUTED` (:114). **NINGUN chequeo de normalizacion** (make/fuel/transmission/currency). Una receta con esos campos NULL o sin traducir sella VERIFIED.
- `pipeline/recipe_extract_web.py:112-114` [VERIFIED] `_valid(v) = bool(v.get("name")) and (price is not None or url)` — el umbral de validez del rung web exige solo `name` + (price|url), nada semantico.
- `pipeline/ingest.py:49-50` [VERIFIED] gate INE `if not (d.province_code.isdigit() and "01" <= d.province_code <= "52")` vive **AGUAS ABAJO** del sello, invisible a el: una receta sella VERIFIED y luego ingest descarta TODO el inventario de un CP no-ES ("out of Spain range ... ingested:0", [faceta 21](#faceta-21)).
- `pipeline/recipe_harness.py:80-91` [VERIFIED] `sample_paths` solo suma `declared` si `full_dealer` (:89); el VAM es **ciego al contenido** (cuenta filas, no valida divisa ni region).
- **Evidencia de cobertura [VERIFIED por conteo en vivo]**: `git ls-files countries/ES/recipes/*.yaml` = **61** (flat, git-tracked); `git ls-files countries/**/recipe.yaml` = **580**; arbol completo `countries/ES/*` git-tracked = **643**. La narrativa "ls recipes|wc=641" esta **mis-atribuida**: 641≈643 es el ARBOL GEO completo, NO el dir flat de recetas (61). El sello narra una cobertura que el dir flat no tiene.

#### (b) El mecanismo al atomo
`decide_status` es el juez del stage y es puramente cuantitativo: certifica que el parser fue FIEL A LOS BYTES (cero perdida) y que produjo un numero de filas, NO que esas filas sean SEMANTICAMENTE servibles. Tres cegueras se apilan: (1) ceguera de normalizacion — make/fuel/transmission pueden ser NULL o etiqueta cruda; (2) ceguera de moneda — heredada de la [faceta 12](#faceta-12), el precio no lleva divisa y el sello no lo exige; (3) ceguera cross-stage — el gate INE ([faceta 21](#faceta-21)) que decide si la region es valida vive en ingest, despues del sello, asi que el sello no sabe que el pais entero sera descartado. El `_valid` del rung web baja aun mas el piso (name+price/url). Resultado: recetas individualmente count-clean VERIFIED que COLECTIVAMENTE son no-servibles, y nada lo marca. Ademas la propia evidencia de cobertura del sello (641) esta mal atribuida.

#### (c) Costura ES->generico
El sello es el meta-sub-proyecto que define "100% para un pais". Hoy es ES-shaped en 3 ejes. El fix vuelve el sello **normalization-aware y currency-coherent**: (1) pisos de fill-rate make/fuel/transmission en `decide_status` sobre el sample; (2) chequeo de vocabulario canonico (fuel/transmission ∈ enum neutral, [faceta 18/19](#faceta-18)); (3) coherencia de moneda (precio lleva currency, [faceta 12](#faceta-12)); (4) **subir el gate cross-stage AL sello** — region resoluble bajo el pack ([faceta 21](#faceta-21)) verificada antes de VERIFIED, no en ingest; (5) deteccion de "sellado pero semanticamente vacio"; (6) corregir la integridad de evidencia 641-vs-61 en la narrativa del sello y cruzar `git ls-files` en CI; (7) articular el criterio de ROLLBACK para un pais parcialmente onboarded.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT**: un pais acumula recetas VERIFIED individualmente count-clean pero COLECTIVAMENTE no-servibles — fuel/transmission sin traducir ([faceta 18/19](#faceta-18)), currency ausente ([faceta 12](#faceta-12)), region mal mapeada ([faceta 21](#faceta-21)) — y NADA en el sello lo marca.
- **Herencia de ceguera**: el sello hereda la ceguera-de-contenido del VAM ([faceta 8](#faceta-8)) y la invisibilidad del gate INE downstream ([faceta 21](#faceta-21)): el pais sella "verde" y luego ingest devuelve `ingested:0` para todo CP no-ES.
- **Evidencia mis-atribuida**: la cobertura narrada (641) NO es el dir flat de recetas (61) -> el sello afirma una cobertura inexistente; un pais #2 podria heredar la misma narrativa inflada.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (pisos de fill-rate en decide_status)**: make>=X%, fuel>=Y%, transmission>=Z% sobre el sample antes de VERIFIED; un sample todo-NULL FALLA donde hoy pasa.
- **Via 2 (data-contract pre-sello, fail-closed)**: Great Expectations/Pandera asevera fuel/transmission ∈ enum neutral, currency NOT NULL, region resoluble bajo el pack; cualquier breach NIEGA el sello del estrato (espejo del invariante COUNTRY-PROOF: inyectar un source_key/region foraneo FALLA el build).
- **Via 3 (atestacion tamper-evident)**: in-toto liga {git SHA, content-hash de inputs, parse_loss, quorum VAM, fill-rates} -> certificado externamente verificable; alterar una fila post-sello -> la verificacion FALLA.
- **Via 4 (property-fuzz)**: Hypothesis genera el caso de locale raro (separador MX, CP alfabetico IT, titulo CJK JP) que los 11 golden ES no ven y bloquea el merge.
- **Via 5 (evidencia auditada)**: CI cruza `git ls-files countries/<CC>/recipes/*.yaml` contra la cobertura narrada -> el 641-vs-61 no puede repetirse.
- **Baseline ES byte-identica**: ES sigue sellando exactamente igual tras endurecer el sello (cero regresion).

#### (f) Herramienta NEXT-LEVEL
Primario (vuelve el sello normalization-aware): `Contrato de datos PRE-sello` -> **Great Expectations** (Apache-2.0) [VERIFIED NEXT-LEVEL.md:164-170] https://github.com/great-expectations/great_expectations (alt. Pandera) — expectativas ejecutables, versionadas y BLOQUEANTES sobre fill-rate, vocabulario canonico, currency-coherencia y region-resoluble: el estrato falla CERRADO, no abierto. Segundo (vuelve el sello certificable externamente): `Sello criptograficamente reproducible y ATESTIGUADO` / `certifiable-recipe-provenance` -> **in-toto** (Apache-2.0) [VERIFIED NEXT-LEVEL.md:140-146 y 309-315] https://github.com/in-toto/in-toto — atestacion firmada tamper-evident del veredicto + hashes, compatible con sample-verify-delete (firma el veredicto, no el crudo). Adversarial: **Hypothesis** (MPL-2.0) [VERIFIED NEXT-LEVEL.md:317-323] property-fuzz del contrato de normalizacion. Opcional para el sello-como-intervalo: **ER-Evaluation** (AGPL-3.0, usar offline por el copyleft de red) [VERIFIED NEXT-LEVEL.md:522]. Great Expectations + in-toto son la dupla que cierra el sealing-hole heredado de las [facetas 8/12](#faceta-8)/21.

#### Resolución condensada — Faceta 26
- **Costura** · decide_status (recipe_harness.py:94-117) sella VERIFIED solo sobre COUNT (loss==0, parsed>=min(target,k)), sin chequeo de make/fuel/transmission/currency; _valid del rung web (recipe_extract_web.py:112-114) exige solo name+price/url; el gate INE (ingest.py:49-50) que valida region vive AGUAS ABAJO del sello, invisible a el; el VAM (sample_paths:80-91) es ciego al contenido. Evidencia mis-atribuida: cobertura narrada 641 = arbol geo (643 tracked), pero el dir flat de recetas son 61 git-tracked (580 recipe.yaml en total) [VERIFIED por git ls-files].
- **Fix** · Volver el sello normalization-aware y currency-coherent: (1) pisos de fill-rate make/fuel/transmission en decide_status sobre el sample; (2) chequeo de vocabulario canonico (fuel/transmission ∈ enum neutral); (3) coherencia de moneda (precio lleva currency); (4) subir el gate cross-stage region-resoluble AL sello (no en ingest); (5) deteccion de 'sellado pero semanticamente vacio'; (6) corregir la narrativa 641-vs-61 y cruzar git ls-files en CI; (7) criterio de rollback para pais parcialmente onboarded. ES sella byte-identico tras endurecer (cero regresion).
- **Adversarial** · Un pais DE/FR/IT/PT acumula recetas VERIFIED individualmente count-clean pero COLECTIVAMENTE no-servibles (fuel/transmission sin traducir, currency ausente, region mal mapeada) y nada en el sello lo marca; el sello hereda la ceguera-de-contenido del VAM ([faceta 8](#faceta-8)) y la invisibilidad del gate INE downstream ([faceta 21](#faceta-21)) -> el pais sella verde y luego ingest devuelve ingested:0 para CP no-ES. La evidencia de cobertura (641) esta mis-atribuida al dir flat (61) -> el sello narra una cobertura inexistente.
- **Sellado (multi-vía)** · Via1 pisos de fill-rate make/fuel/transmission en decide_status (sample todo-NULL FALLA); Via2 Great Expectations/Pandera pre-sello fail-closed (fuel/transmission ∈ enum, currency NOT NULL, region resoluble; source_key/region foraneo FALLA el build); Via3 in-toto liga {git SHA, hashes inputs, parse_loss, quorum, fill-rates} -> alterar fila post-sello FALLA la verificacion; Via4 Hypothesis genera el caso locale-raro (separador MX, CP alfabetico IT, titulo CJK JP) que los 11 golden ES no ven; Via5 CI cruza git ls-files vs cobertura narrada (mata el 641-vs-61); baseline ES byte-identica.
- **Herramienta NEXT-LEVEL (€0)** · Contrato de datos PRE-sello -> Great Expectations (Apache-2.0) https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167] (alt Pandera): expectativas ejecutables/bloqueantes sobre fill-rate/vocab/currency/region -> estrato falla CERRADO. + Sello atestiguado/certifiable-recipe-provenance -> in-toto (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:143,312]: atestacion tamper-evident del veredicto+hashes (no del crudo). Adversarial: Hypothesis (MPL-2.0, NEXT-LEVEL.md:320). Opcional sello-como-intervalo: ER-Evaluation (AGPL-3.0 offline, NEXT-LEVEL.md:522). Great Expectations + in-toto cierran el sealing-hole heredado de [facetas 8/12](#faceta-8)/21.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

> **Cierre honesto de la sección.** Veredicto del inquisidor: **NEEDS_REWORK** (`holds=false`). Las 14 B + 9 MP + 6 SH, ahora bajadas al átomo en **26 sub-proyectos-360**, tienen **resolución de diseño €0** —módulo locale único (`parse_money`/`parse_date`/`normalize_vehicle`), `LocaleProfile` reificado, enum `Selector` + `field_map` interpretable, dimensión `currency`, brand-anchor script-agnóstico, sello normalization-aware con `Great Expectations`/`Hypothesis`/`in-toto`— **sin re-key de ES ni reescritura del motor**. Cinco abren con causa+gate declarado y **no se cierran en aislamiento de 03**: **O1** (capa-2 LLM, €>0 PENDING-OWNER), **O2** (facetas served off-Spanish, ESCRITURA-PROD), **O3** (recompute ES de precios/km, PROD-write auditado), **O4** (strict enum sobre las 61 recetas ES, build-order), **O5** (CJK más allá del prefijo de marca, difiere con O1). Ninguna rotura se transcribe como sana: la dimensión moneda ausente (Faceta 12), el `'24.900'`→24.9 ya sirviéndose en ES (Faceta 14), el rechazo total de IT y la corrupción silenciosa JP (Faceta 21) y la evidencia 641-vs-61 mal atribuida (Faceta 26) se integran como **defectos reales** y se resuelven corrigiendo el código a la verdad. El motor de extracción **es** genérico; lo que falta es **desincrustar el pack y enhebrar el país por debajo del esquema** — exactamente el hallazgo transversal de la espina dorsal.
