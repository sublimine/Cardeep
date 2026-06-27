# Etapa 7 · Calidad/Sello — Biblia
> Estado adversarial: **NEEDS_REWORK** (`holds=false`). Fuente: Wave 1 (cada afirmación con `path:línea` verificado leyendo la fuente real). Stack vivo **CAÍDO**: toda cifra de DB es **punto-en-el-tiempo**, no re-ejecutable ahora — re-correr `python -m pipeline.exhaustiveness.cli run` contra la DB viva antes de declarar progreso.
>
> Navegación: [Misión](#misión) · [Existe hoy](#lo-que-existe-hoy-verificado) · [Motor](#motor-invariante-reusado-byte-idéntico-por-país) · [Pack](#pack-por-país) · [Costuras](#costuras-es-hardcoded--fix) · [Diseño A→Z](#diseño-genérico-az--la-abstracción-country-proof) · [Onboarding](#onboarding-de-país-nuevo-pasos-de-biblia-para-esta-etapa) · [Sellado+rollback](#sellado--verificación-multi-vía--rollback) · [**Veredicto: roturas→resolución**](#veredicto-adversarial-roturas--resolución) · [**360 por faceta**](#sub-proyectos-institucionales-360-por-faceta) · [Nivel inalcanzable](#mejoras-a-nivel-inalcanzable-eur0-priorizadas) · [Riesgos](#riesgos--open-items)

---

## Misión
Probar, de forma **falsable y defendible**, qué fracción del 100% real de puntos de venta de un país está realmente cubierta. El entregable de esta etapa **no es un dato, es el DENOMINADOR**: un **intervalo certificado** (cota inferior con su margen) construido por captura-recaptura multi-lista (MSE), triangulado contra un censo externo independiente, y sellado **sobre la cota inferior** — nunca sobre el punto-estimado. La doctrina central es **anti-maquillaje**: la masa cuya verdad se desconoce **no se cuenta como cubierta**; antes confesar un hueco que vender una mentira.

El sello es una **fracción** `coverage = numerador / denominador`. Esta etapa posee el **denominador** (cuántos hay de verdad) y debe fijar el **numerador canónico** (qué cuenta como punto de venta). Hoy el denominador está estadísticamente blindado y es casi country-invariante; el numerador es **ambiguo** (tres scopes vivos) y la cadena de sellado es **country-BLIND por debajo del esquema**. Esta biblia documenta lo verificado, separa motor de pack, y cierra —o declara abierta con causa— cada rotura del inquisidor.

---

## Lo que existe HOY (verificado)
El **núcleo numérico MSE** es matemática pura sobre tuplas de captura `0/1`, sin un solo supuesto geográfico:

- **Chapman 2-listas + varianza de Seber + CI bootstrap no-paramétrico** (`n_boot=4000`, `seed=20260620`); confianza forzada a `'low'` porque 2 listas son un **suelo**, jamás una certificación. [VERIFIED `pipeline/exhaustiveness/estimators.py:77-83,109-122`]
- **MSE K-listas log-lineal de Fienberg** (Poisson GLM, `statsmodels` lazy-import), selección voraz de interacciones por BIC; `N_hat = n_obs + exp(intercept)`; CI por método delta; ajuste degenerado cae a conteo observado con `confidence='none'`. [VERIFIED `pipeline/exhaustiveness/estimators.py:138-145` y diseño cap.#2]
- **La cifra anti-maquillaje:** `coverage_lower = n_obs / ci_high` (observado sobre la **cota SUPERIOR** de N̂); el punto-estimado estructuralmente **nunca** certifica. [VERIFIED `pipeline/exhaustiveness/estimators.py:65-71`]
- **Compuerta de identificabilidad `IDENT_CAP = 5.0`:** un estrato solo es "identified" si `N̂ <= 5·n_obs` (piso de cobertura implícito ≥20%) y el CI es finito; si no, se reporta **uncertified, no sellado**. [VERIFIED `pipeline/exhaustiveness/estimators.py:301-318`]
- **Criterio de sellado + roll-up honesto:** `DEFAULT_THRESHOLD=0.95`; un estrato sella sii `identified AND finite(cov_lower) AND cov_lower>=threshold`; el denominador nacional certificado = **suma de N̂ solo sobre estratos identificados**; la masa uncertified se reporta **aparte**, jamás plegada como "100% cubierta". [VERIFIED `pipeline/exhaustiveness/seal.py:27,42-47,84-107`]
- **Taxonomía de 7 listas ortogonales** `GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG`; `MKT/GRAPH/COLLAPSE` excluidas a propósito (sesgo de seed marketplace, dependencia de grafo, resolución-no-observación). [VERIFIED `pipeline/exhaustiveness/lists.py:27-49`]
- **Unidad de captura = entidad RESUELTA** (cross-source deduped, `v_dealer_resolved.resolved_ulid`): un dealer visto en OSM y en autocasion colapsa a **una** fila por lista — el fix del viejo problema `m=10` de solape infra-contado. [VERIFIED `pipeline/exhaustiveness/capture.py:1-9`]
- **Segundo canal R** (`Rcapture::closedpMS.t` + LCMCR bayesiano de clases latentes) vía subprocess `Rscript`; crosscheck marca `distrust` si `|dif rel| > tol=0.25`; ausencia de R **degrada sin fallar**. [VERIFIED `pipeline/exhaustiveness/seal.py:78-81`; diseño cap.#11]
- **Splink probabilístico** (Fellegi-Sunter, DuckDB) sobre `name+muni+phone+website`, **UNIONado** con el dedup determinista para que la unidad de captura **nunca** sea más fina que `v_dealer_resolved`. [VERIFIED `pipeline/exhaustiveness/splink_merge.py:160-211`]
- **Costura de triangulación externa, ya country-paramétrica en la firma:** `load_external_census(path, country_code='ES')` carga `countries/<CC>/census/dirce_cnae451.csv` vía `census_dir(country_code)`; `triangulate()` da banda `0.7-1.4 → consistent/n_hat_high/n_hat_low/no_anchor`. [VERIFIED `pipeline/exhaustiveness/triangulation.py:36-50,66-81`]
- **Esquema de persistencia MSE (migración 0048):** `discovery_list`, `discovery_capture`, `exhaustiveness_estimate` + vista `v_exhaustiveness_seal`. [VERIFIED `migrations/0048_discovery_capture.sql:22-106`]
- **Definición canónica de punto-venta `v_servable_dealer`** (entidad activa que vende coches; NO `particular`/`desguace`; `garaje` solo con inventario) — **definida pero NO CABLEADA**: ningún consumidor la lee aún. [VERIFIED `migrations/0056_v_servable_dealer.sql:26-37`]
- **Sello REGISTRAL legacy paralelo** (mecanismo distinto): `v_province_seal` sirve techo DIRCE para `venta` y censo-vs-DGT para `desguace`; alimentado por `denominator_estimate`. [VERIFIED `scripts/load_denominator_provincia.py:34-78`; diseño cap.#13]

**Cifras vivas (punto-en-el-tiempo, stack caído):**
- Sello MSE último build: `coverage_lower` nacional **~37,7% UNSEALED**, solo **12 de ~208 estratos** sellados, `N̂ ~15.560` no-particular. [ASSUMED — recon, no re-ejecutable]
- Sello registral: `venta` nacional **80,5%** (18.298/22.720), `desguace` **215,6%** (52/52 SELLADO). [ASSUMED — `liveseal.json`, punto-en-el-tiempo]
- `v_servable_dealer`: directorio ~36,3k / con inventario ~18,3k; el viejo 54.587 mezclaba ~35k cascarones + 2,3k desguaces. [VERIFIED `migrations/0056_v_servable_dealer.sql:17-19`]

---

## Motor (invariante, reusado byte-idéntico por país)
Lo que **no cambia nunca** porque es álgebra de captura-recaptura, no geografía:

| Componente | Qué es | Por qué es invariante |
|---|---|---|
| `estimators.py` entero | Chapman+bootstrap, Fienberg log-lineal+BIC, `dependence_robust_bound`, `estimate_stratum`, `IDENT_CAP=5.0`, propiedad `coverage_lower=n_obs/ci_high` | Recibe `{patrón 0/1: frecuencia}`, devuelve `Estimate`. No sabe de España ni lo sabrá. [VERIFIED `estimators.py:65-71,301-318`] |
| `seal.py` (la ley) | Umbral `0.95` sobre `coverage_lower`, split honesto identified/uncertified, roll-up suma-de-estratos con varianzas que suman | Matemática sobre el dict de patrones; cero supuesto de país. [VERIFIED `seal.py:27,42-47,84-107`] |
| `capture.read_patterns` | Agrupar por `(estrato, unidad_resuelta)` en vectores `0/1` sobre buckets ordenados, celda all-zero excluida (es lo que MSE estima) | Genérico una vez el orden de buckets y la clave de estrato son **parámetros**. [VERIFIED `capture.py:1-9`; diseño cap.#3] |
| Doctrina de ortogonalidad | Las 7 clases de mecanismo de captura + la regla "mismo mecanismo colapsa a una lista; seed/grafo/resolución fuera" | Semántica universal; solo cambia **qué fuente** del país cae en cada clase. [VERIFIED `lists.py:1-22,47-49`] |
| `estimators_r.py` + `r/mse.R` | Rcapture + LCMCR, `tol=0.25`, semántica de ausencia-graciosa | Idéntico para todo país; solo cambian las frecuencias de entrada. [VERIFIED `seal.py:78-81`] |
| `splink_merge.py` (mecánica) | Fellegi-Sunter + invariante UNION-con-dedup (captura nunca más fina que resuelto) | Las columnas de comparación son atributos universales de dealer. [VERIFIED `splink_merge.py:198-211`] |
| `triangulate()` (lógica) | Banda `0.7-1.4` y verdict consistent/n_hat_high/n_hat_low/no_anchor | Solo los **valores** del ancla son del país; la comparación no. [VERIFIED `triangulation.py:66-81`] |
| Shapes de almacenamiento (0048) | Estructura de columnas `discovery_list/discovery_capture/exhaustiveness_estimate` y el contrato seal-on-`coverage_lower` | Reusable verbatim — módulo el ensanche de la clave de región (ver Costuras). [VERIFIED `0048:22-74`] |
| **La tesis** | 100% = **intervalo certificado** (cota inferior con margen que encoge), sellado sobre el intervalo, append-only por `build_run_id`, sample-verify-delete | Es la ley que todo país hereda sin cambio. [VERIFIED `0048:12-13`] |

> **Frontera motor/pack:** el motor es invariante **por encima de la línea del esquema**. Por **debajo** (clave de estrato, enhebrado de `country_code`, membresía de listas, taxonomía, censo, constantes de política) hoy es **ES-clavado** — es exactamente lo que rompe el inquisidor y lo que el pack debe aportar.

---

## Pack por país
Lo que **cada país aporta** para esta etapa (declarativo, **cero código de motor**):

1. **Censo ancla externo** — `countries/<CC>/census/external_census.csv` con `(region_code, segment, n_external)` + filas nacionales, **+ `SOURCE.md`** etiquetando cada cifra `[MEDIDO]` (conteo directo) o `[ESTIMADO DECLARADO]` (reparto de un total nacional real). Construido por un mecanismo **DISTINTO** al scrape. (ES: INE DIRCE CNAE-451, FACONAUTO, DGT CAT.) [VERIFIED contrato en `triangulation.py:8-17`]
2. **Mapeo `source_key → bucket ortogonal`** de las fuentes reales del país: qué feeds son GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG. Hoy es un dict Python (`lists._EXACT`); la forma-pack son **filas en `discovery_list`** scoped por país. [VERIFIED `lists.py:27-45`; columna `orthogonality_class` ya existe en `0048:24`]
3. **Taxonomía `kind → segment`** del país (su enum de tipos colapsado a los segmentos de estratificación). (ES: 9 kinds → `{compraventa, concesionario, desguace, otros}`.) [VERIFIED `capture.py:19-42`]
4. **Predicado canónico de punto-venta** — la versión `<CC>` de `v_servable_dealer`: qué kinds cuentan, gate de inventario, exclusiones. Es el **numerador canónico**. [VERIFIED `0056:26-37`]
5. **Partición de regiones** — el vocabulario `region_code` del estrato (ES: 52 provincias INE `char(2)`; genérico: `text`). [VERIFIED `0001_geo.sql:4-9`]
6. **(OPCIONAL) parámetros del techo registral legacy** si el país corre además el sello administrativo: ratio CNAE/registro, totales de asociaciones, splits oficiales por región. Un país **puede saltárselo** y apoyarse solo en MSE + triangulación. [VERIFIED `load_denominator_provincia.py:38`]
7. **Constantes de política calibradas** — `threshold`, `IDENT_CAP`, banda de triangulación, justificadas contra la **calidad de datos local**, no heredadas de ES `0.95/5.0/0.7-1.4` por default. [VERIFIED valores ES en `seal.py:27`, `estimators.py:304`, `triangulation.py:75-80`]
8. **Config de resolución locale-aware** — normalización de nombre + blocking válido para los geo-codes y el **script** del país (latino vs CJK), porque la unidad de captura gobierna `m` y por tanto el CI. [VERIFIED blocking latino-clavado `splink_merge.py:165,170`]

> Cruce con `COVER-NEW-COUNTRY.md` §E: el gate de salida de `KNOW_COUNTRY` **ya exige ≥3 listas ortogonales** identificadas antes de proceder — el insumo #2 de este pack es ese mismo requisito, no negociable.

---

## Costuras ES-hardcoded → fix
La columna vertebral del veredicto: `country_code` se enhebró en el **esquema** (cdp_code `CDP-ES-…`, 0052/0053) y en `paths.py`, pero **NO** en la lógica de la cadena de sellado. Todo lo de abajo es **country-BLIND**.

| location | issue | fix |
|---|---|---|
| `migrations/0048_discovery_capture.sql:39,58` (`province_code char(2)` en `discovery_capture` y `exhaustiveness_estimate`) | **No hay columna `country_code` en NINGUNA tabla de la cadena de sellado.** Dos países colisionan en la misma tabla; `char(2)` no admite códigos no-ES. [VERIFIED] | `ALTER TABLE ... ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES'`; ensanchar `province_code → region_code text`. Enhebrar `country_code` por `capture.read_patterns/build` y `seal.compute/_persist` como **dimensión más externa** del estrato. Backfill `'ES'` = byte-estable. |
| `migrations/0001_geo.sql:4-9,26` (`geo_province.code CHAR(2) PK`, `ccaa_code CHAR(2) NOT NULL`, CHECK `left(code,2)=province_code`) | Rejilla administrativa **single-tenant INE**: `CHAR(2)` trunca AGS alemán (5 díg.), DOM francés (`'971'`); el CHECK de prefijo asume estructura INE. [VERIFIED] | Adaptador geo del país (Etapa 6) provee árbol+códigos; aquí `region_code text` + `country_code`. ES sigue resolviendo `char(2)` por compatibilidad. |
| `migrations/0048:82-88` (`v_exhaustiveness_seal`: `latest = ORDER BY created_at DESC LIMIT 1`) | La vista sirve **UN único build global**; con país #2 el último build de B oculta el sello de A entero. [VERIFIED] | `latest AS (SELECT DISTINCT ON (country_code) country_code, build_run_id ... ORDER BY country_code, created_at DESC)` + join por `country_code`. Endpoint `geo.py` filtra `WHERE country_code=:cc`. |
| `pipeline/exhaustiveness/capture.py:19-42` (`DEALER_KINDS` 9 valores ES; `_SEGMENT` → `{compraventa,concesionario,desguace,otros}`) | Universo de dealers + colapso kind→segment = taxonomía ES clavada en Python. [VERIFIED] | Mover a pack (`countries/<CC>/taxonomy.yaml` o tabla `seg_map(country_code,kind,segment)`); `capture.segment_for(country_code,kind)` la lee. Loader default resuelve ES a los literales actuales. |
| `pipeline/exhaustiveness/lists.py:27-74` (dict `_EXACT`; prefijos `'oem_'/'mercedes'/'oficial'/'_new_stock'`) | Enumera fuentes ES (`aedra/aecs/acevas/dgt_cat/autocasion_census/borme_cnae`); incluye la palabra española `'oficial'` y la marca `mercedes`. Fuente de país nuevo cae a `MKT` y **nunca entra al MSE**. [VERIFIED] | Mapeo data-driven desde `discovery_list` scoped por `country_code` (la columna `orthogonality_class` ya existe). `bucket_for(country_code,source_key)` = lookup de tabla; el dict Python pasa a ser **solo la semilla ES**. |
| `pipeline/exhaustiveness/triangulation.py:27,32-33` (`CENSUS_CSV_NAME='dirce_cnae451.csv'`; `CENSUS_DIR/DEFAULT_CSV` atados a ES en import) | El nombre del fichero **miente la provenance** (es el DIRCE CNAE-451 español) pese a estar declarado "country-agnostic"; `status()` siempre reporta la ruta ES. [VERIFIED `triangulation.py:84-88`] | Renombrar a `external_census.csv` (agnóstico) o parametrizar el nombre por manifiesto de pack; `status(country_code)` resuelve `census_dir(cc)`. La firma del loader **ya** acepta `country_code` — solo restan las constantes de módulo ES. |
| `pipeline/exhaustiveness/capture.py:17` y `migrate.py` (`DSN='postgresql://…localhost:5433/cardeep'` clavado, no env) | El módulo clava el DSN de dev, a diferencia del resto del pipeline que lee `os.environ`. Bloquea correr el sello contra cualquier DB no-default. [VERIFIED] | `DSN = os.environ.get('CARDEEP_DSN', '<dev default>')`, ruteado por `pipeline/config_guard.py`. |
| `migrations/0056_v_servable_dealer.sql:35-37` (`kind NOT IN ('particular','desguace') AND kind<>'garaje'`) | El **numerador canónico** hardcodea literales kind ES; además está **NO CABLEADO** (ningún consumidor lo lee). [VERIFIED] | Cablearlo como ÚNICO numerador de `v_province_seal` + MSE + conteo público; hacer el **predicado** un parámetro de pack. (Ver OPEN ITEM B8/P3.) |
| `scripts/load_denominator_provincia.py:38,64-65,71` (`RATIO_451_45=23085/88621`; `assert len==52`; FK `geo_province`) | Loader registral 100% ES: ratio CNAE-451, hard-assert de 52 provincias, segmento `'venta'`, CSV oficial ES. **Aborta** en otro país. [VERIFIED] | Si se conserva el sello administrativo: parametrizar ratio/segmento/conteo-de-regiones desde el pack y soltar el literal `==52`. **Mejor:** deprecar esta ruta para países nuevos y apoyarse en MSE + triangulación (ya country-paramétrica). |

---

## Diseño genérico A→Z — la abstracción country-proof
La separación **MOTOR/PACK** ya está ~80% latente en el código (`paths.census_dir(country_code)`, `Estimate` puro, doctrina `coverage_lower`). El diseño la completa con la regla de oro `DEFAULT='ES'` **ya probada** en `paths.py:22` (cada helper acepta `country_code` con default `'ES'` y resuelve los literales actuales) — así **España no se toca**.

- **(A) Abstracción central.** El denominador de un país es una función `certify(country_code) → {por_estrato: Estimate, nacional: Estimate, sello: bool, intervalo: [ci_low,ci_high], triangulación: verdict}`. El estrato es la **tripleta `(country_code, region_code, segment)`**; hoy es `(province_code char(2), segment)` y la única cirugía es **anteponer `country_code`** y **ensanchar `region_code` a `text`**.
- **(B) Motor invariante.** `estimators.py` entero es la máquina: recibe `{patrón 0/1: frecuencia}` → `Estimate{N_hat, CI, coverage_lower, identified}`. `seal.py` aplica la ley. `estimators_r.py`+`r/mse.R` son el 2.º canal. `splink_merge.py` aprieta el solape. **Byte-idéntico** para todo país. [VERIFIED `estimators.py:65-71`, `seal.py:42-47`]
- **(C) Interfaces pack.** Los 8 datos declarativos de [§Pack](#pack-por-país). Cero código de motor.
- **(D) Estructura de datos.** `discovery_capture` y `exhaustiveness_estimate` ganan `country_code char(2) NOT NULL` como dimensión externa; `discovery_list` gana `country_code` (o prefijo de `list_key`) para que las membresías no colisionen. `v_exhaustiveness_seal` pasa de "último build global" a `DISTINCT ON (country_code) … ORDER BY created_at DESC`.
- **(E) Cómo se vuelve country-agnóstico sin reescribir ES.** `DEFAULT='ES'` en cada helper (`census_dir`, `segment_for`, `bucket_for`, `certify`): sin argumento resuelve idéntico a hoy; un 2.º país es solo otro valor del parámetro. `lists.py` pasa de dict a semilla-ES de `discovery_list`; `capture._SEGMENT` pasa de dict a lectura de pack; `triangulation` pierde sus constantes de módulo ES. [VERIFIED patrón en `paths.py:20-52`]
- **(F) El denominador vs el numerador.** El sello es una fracción y hoy el **numerador es ambiguo** (tres scopes: ~54,6k stats, geo-verificado, ~18,3k seal). El diseño cablea `v_servable_dealer` como **ÚNICO** numerador y único punto-venta público, con su predicado también parametrizado; entonces `numerador == paginado == scope-certificado` **por construcción**. [VERIFIED tres scopes en `0056:6-9`]
- **(G) Cómo subir `coverage_lower` de 37,7% a 80%+ a coste €0** — cuatro palancas ortogonales, todas ya semi-presentes:
  - **g1 · Alimentar las 7 listas:** la recon dice que solo **4/25 adaptadores** pasaron por `harvest_run` [ASSUMED — recon], así que muchos estratos caen a `K<3` (no identificados) o `K=2` (Chapman, suelo). Subir K estrecha el CI y sube `coverage_lower` **mecánicamente**, sin tocar matemática.
  - **g2 · Activar DORK** vía SearXNG self-host (€0): la 8.ª señal genuinamente ortogonal, hoy dormida; +1 lista en todos los estratos.
  - **g3 · Encender Splink por default** (`unit='splink'`, ya in-tree) y el canal R/LCMCR: Splink recupera solapes que el dedup perdió (`m↑ → CI↓`); LCMCR da N̂ menos sesgado bajo heterogeneidad. [VERIFIED `cli.py:80` ya expone `--unit splink`]
  - **g4 · Convertir el ancla en VINCULANTE:** hoy la triangulación se reporta pero **no acota** N̂ (`seal.py:42-47` ignora `external_ref`). Inyectar el censo como margen-conocido/celda-marginal en el ajuste Fienberg PIN-ea N en estratos no-identificados → traslada masa **uncertified → certified** sin inventar. [VERIFIED `seal.py:42-47`]
- **(H) El 100% como intervalo.** La salida nunca es un entero: es `[coverage_lower, coverage_point]` con margen que encoge build a build. **SELLADO** = `coverage_lower>=0.95` en estratos identificados **Y** triangulación `consistent` **Y** R `agree`. El sistema declara "no queda nada que encontrar" **solo** cuando `coverage_lower` deja de subir entre builds (detector de saturación) — la única definición honesta de exhaustividad.

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)
1. **CENSO ANCLA.** Crear `countries/<CC>/census/external_census.csv` `(region_code,segment,n_external)` + filas nacionales. Cada cifra de fuente €0 oficial por **mecanismo distinto** al scrape. `SOURCE.md` etiqueta cada una `[MEDIDO]`/`[ESTIMADO DECLARADO]` con fórmula y URL. **Prohibido fabricar:** sin censo honesto para un segmento, se omite la fila y el sello reporta `no_anchor`.
2. **TAXONOMÍA DE SEGMENTOS.** Declarar el mapa `kind→segment` del país como filas de pack (o `taxonomy.yaml`). **NO editar `capture.py`.**
3. **MEMBRESÍA DE LISTAS.** Por cada `source_key` real, insertar fila en `discovery_list (country_code, list_key, orthogonality_class)` asignándolo a una de las 7 clases. **Verificar ≥1 fuente real por clase ortogonal, idealmente ≥3 por estrato** para que el log-lineal identifique.
4. **PREDICADO PUNTO-VENTA.** Definir la versión `<CC>` de `v_servable_dealer` y **cablearla** a stats/geo/seal para que `numerador == paginado == scope-certificado`.
5. **REGIONES.** Cargar el set `region_code` del país en la tabla geo. El estrato pasa a `(country_code, region_code, segment)`.
6. **MIGRAR + CONSTRUIR.** Aplicar migraciones MSE (idempotentes) con `country_code`; ejecutar `python -m pipeline.exhaustiveness.cli run --country <CC> --run-id <CC>-<fecha>` (`capture.build` + `seal.compute`). [VERIFIED CLI `cli.py:73-88` — **falta** flag `--country`, ver B2]
7. **VERIFICAR 2.ª VÍA.** Con R, correr `--r-crosscheck` (Rcapture/LCMCR, `tol 0.25`); confirmar verdict de triangulación en `0.7-1.4`. Sin R/Splink, degrada sin fallar. [VERIFIED `cli.py:82`, `seal.py:78-81`]
8. **CONTRATO DE TEST.** Portar `tests/test_exhaustiveness_triangulation_loaded.py` al país (censo presente, ≥N anclas, segmentos en vocabulario, roll-ups consistentes, sin negativos, sin `'otros'` fabricado) y añadir el país al barrido CI.
9. **LÍNEA BASE + LOOP DE CIERRE.** Registrar `coverage_lower` inicial; aplicar las palancas €0 (alimentar listas, DORK/Splink/R, anclar censo) build a build hasta `coverage_lower>=0.95` en identificados **o** hasta saturación. El sello del país es un **INTERVALO certificado, nunca un entero**.

---

## Sellado + verificación multi-vía + rollback
**SELLADO en esta etapa = el sello del DENOMINADOR, no de un dato.** El estrato `(country_code,region_code,segment)` sella sii `estimate.identified` (overlap pin-ea N: `N̂<=IDENT_CAP·n_obs`, CI finito) **Y** `coverage_lower=n_obs/ci_high >= 0.95`. [VERIFIED `seal.py:42-47`] El nacional sella sii `coverage_lower` de la **suma-de-estratos-identificados** ≥0.95. [VERIFIED `seal.py:104-107,138`] La masa uncertified **NO** se cuenta como cubierta; se reporta aparte (regla anti-maquillaje central). [VERIFIED `seal.py:84-95,140-143`] El **punto-estimado JAMÁS certifica.**

**Verificación por 2.ª vía ortogonal** — dos canales realmente independientes ya construidos:
1. **Puente R** (`estimators_r.py`+`r/mse.R`): re-estima cada estrato identificado con `Rcapture::closedpMS.t` + LCMCR; exige `agree` dentro de `tol=0.25` frente al log-lineal Python; divergencia → estrato `distrust`. [VERIFIED `seal.py:78-81`]
2. **Triangulación** (`triangulation.py`): contrasta N̂ contra censo de **mecanismo distinto**; exige ratio `0.7-1.4` (`consistent`). [VERIFIED `triangulation.py:66-81`]

> Un sello creíble necesita **las tres alineadas**: `coverage_lower>=0.95` **+** R `agree` **+** triangulación `consistent`. Si solo cuadra `coverage_lower` pero el ancla dice `n_hat_high`, es señal de **listas correlacionadas no modeladas** o dedup imperfecto y **NO** se debe declarar sellado. (Hoy esto se DETECTA pero no se BLOQUEA automáticamente — ver [H1](#veredicto-adversarial-roturas--resolución).)

**Rollback** — todo es aditivo y reversible:
- Vistas (`v_exhaustiveness_seal`, `v_province_seal`, `v_servable_dealer`) = `DROP VIEW` puro, **cero filas tocadas**. [VERIFIED `0056:45-46`]
- `exhaustiveness_estimate` y `discovery_capture` son **append-only por `build_run_id`**: revertir un build = `DELETE WHERE build_run_id=…`; la serie histórica de `coverage_lower` queda intacta. [VERIFIED `seal.py:172-174` (DELETE por build), `0048:43` (PK incluye build_run_id)]
- `denominator_estimate` (registral) = `DELETE+INSERT` del segmento en transacción, reversible recargando la versión previa.
- Añadir `country_code` = `ALTER TABLE ADD COLUMN DEFAULT 'ES'` (backfill byte-estable) + vistas `CREATE OR REPLACE`.
- **Ninguna operación de esta etapa es irreversible ni de alto coste** → se ejecuta y se reporta **sin gate**, **salvo** el cableado de `v_servable_dealer` al serving público (cambia una cifra de cara al usuario) que pasa por **dry-run(:5434) → golden → Ferrari → CI** antes de exponer. [Gate: ESCRITURA EN SERVING-OF-RECORD, §00-MASTER]
- **Hueco de rollback multi-país** (ver [H4](#veredicto-adversarial-roturas--resolución)): hoy sin `country_code` no hay predicado para `DELETE` limpio de solo-un-país; el fix de la columna lo cierra **en el mismo cambio**.

---

## Veredicto adversarial: roturas → resolución
> `holds=false`, `verdict=NEEDS_REWORK`. **No se oculta ninguna rotura.** Cada break/missing_pack/sealing_hole del inquisidor, con su resolución de diseño (cómo cierra para DE/FR/IT/PT/no-UE) o, si no se puede cerrar ahora, **OPEN ITEM** con causa y gating. El patrón de cierre dominante es el **enhebrado de `country_code` + la regla `DEFAULT='ES'`** ya probada en `paths.py:22`.

### Roturas (breaks)

**B1 · [CRITICAL] Sin dimensión `country` en NINGUNA tabla de la cadena de sellado.**
`geo_province.code CHAR(2) PK` sin country [VERIFIED `0001:4-5`]; `entity.province_code CHAR(2)` [VERIFIED `0002:13`]; `discovery_capture.province_code`/`exhaustiveness_estimate.province_code` `char(2)` sin `country_code` [VERIFIED `0048:39,58`]. `char(2)` trunca códigos no-ES (Kreis AGS=5 díg., DOM `'971'`=3 char); ES `'01'`(Álava) y FR `'01'`(Ain) colisionan en el **mismo** estrato.
→ **RESOLUCIÓN (cierra DE/FR/IT/PT/no-UE):** `ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES'` en `discovery_capture`, `exhaustiveness_estimate` (y `discovery_list`); ensanchar `province_code → region_code text`; enhebrar `country_code` como dimensión más externa del estrato por `capture` y `seal`. Backfill `'ES'` = **byte-estable** (ES no se toca). Es `ALTER` aditivo reversible → se ejecuta sin gate.

**B2 · [CRITICAL] `seal.compute()` nunca enhebra `country_code`; un build alemán triangula contra el censo español.**
Firma sin el parámetro [VERIFIED `seal.py:50-58`]; `external_census = triangulation.load_external_census()` defaultea a `'ES'` [VERIFIED `seal.py:68-69` + `paths.py:22`]; `cli.py` invoca `compute()` **sin** `external_census` [VERIFIED `cli.py:36-37`]. La parametricidad del loader (`census_dir(cc)`) está **muerta al llegar desde la orquestación**. Contradice la capability #8 del propio diseño.
→ **RESOLUCIÓN:** añadir `country_code` a `compute(country_code, …)` y a `cli` (flag `--country`), pasarlo a `load_external_census(country_code=cc)` y a `capture.read_patterns`. `DEFAULT='ES'` mantiene ES idéntico. Cambio mecánico, reversible.

**B3 · [CRITICAL] 5 de 7 listas ortogonales son fuentes ES sin análogo automático.**
`DGT(dgt_cat)`, `CENSUS(autocasion_census)`, `ASSOC(aedra/aecs/acevas)`, `REG(borme_cnae)`, `DORK(dork_municipal)` son ES [VERIFIED `lists.py:27-49`]; solo `GEO(OSM/Overture)` y `OEM` cruzan fronteras. Alemania no tiene DGT(→KBA), ni BORME(→Handelsregister), ni AEDRA(→ZDK); su census-marketplace sería mobile.de/AutoScout24 que el motor **excluye** como `MKT`. Con solo GEO+OEM, `K→2` → Chapman floor, `confidence='low'`, casi nada sella.
→ **RESOLUCIÓN PARCIAL + OPEN ITEM.** El motor `K>=3 → log-linear → sellable` es invariante; lo que falta es **alimentarlo**. El pack DEBE aportar **≥3 listas locales genuinamente ortogonales** (insumo #2). **Gating:** el gate de `KNOW_COUNTRY` ya **exige ≥3 listas ortogonales** antes de proceder [VERIFIED `COVER-NEW-COUNTRY.md:55`]. **OPEN ITEM honesto:** si un país **carece** de 3 fuentes €0 ortogonales, es **estructuralmente no-sellable por encima del suelo Chapman** — no es bug, es límite real que se declara con causa (no se finge cobertura). Palanca €0 g2 (activar DORK universal vía SearXNG) recupera 1 lista cross-border en cualquier país.

**B4 · [HIGH] El denominador registral legacy es 100% ES y ABORTA en otro país.**
`raise SystemExit` si no hay **exactamente 52 provincias** [VERIFIED `load_denominator_provincia.py:64-65`]; `RATIO_451_45=23085/88621` es CNAE-451 español [VERIFIED `:38`]; `v_province_seal` referencia kind ES y `source_key='dgt_cat'`. DE=401 Kreise, FR=101 départements, JP=47 prefecturas no caben.
→ **RESOLUCIÓN (recomendada: deprecar para países nuevos).** El sello MSE+triangulación **ya es la ruta country-paramétrica**; el registral es solo contraste. Para país nuevo: **declararlo legacy-ES fuera del sello genérico**. Si se quiere conservar, parametrizar `ratio/segment/region-count` desde el pack y soltar el literal `==52` por `len(region_set)`. (Cruce P8.)

**B5 · [HIGH] Ontología de tipos de dealer y mapa de segmentos = enum ES.**
`DEALER_KINDS` (9 valores) y `_SEGMENT → {compraventa,concesionario,desguace,otros}` [VERIFIED `capture.py:19-42`]; reforzado por `CHECK kind IN (…)` con 6 literales ES [VERIFIED `0002:7-8`]. El split franquiciado/independiente y `desguace` como segmento sellado de 1.ª clase son regulatorios ES (DGT CAT).
→ **RESOLUCIÓN:** mover `DEALER_KINDS` y `kind→segment` al pack (`taxonomy.yaml` o tabla `seg_map(country_code,kind,segment)`); `capture.segment_for(country_code,kind)` lo lee; loader default resuelve ES a los literales actuales. La rejilla `(region × segment)` queda escrita en ontología del país.

**B6 · [HIGH] `v_exhaustiveness_seal` sirve UN build global; con país #2 el sello del país #1 desaparece.**
`latest = ORDER BY created_at DESC LIMIT 1` [VERIFIED `0048:82-88`]; `report.py` lee sin filtro de país. Correr ES y luego DE muestra **solo DE**.
→ **RESOLUCIÓN:** `latest AS (SELECT DISTINCT ON (country_code) … ORDER BY country_code, created_at DESC)`; endpoint filtra `WHERE country_code=:cc`. Depende de B1 (la columna). `CREATE OR REPLACE VIEW` reversible. **Debe migrarse en el MISMO cambio que B1** o rompe silenciosamente al entrar el 2.º país.

**B7 · [HIGH] La resolución de entidad asume normalización latina y geo-codes ES.**
`block_on('municipality_code','name_prefix')` + `JaroWinklerAtThresholds('name', …)` [VERIFIED `splink_merge.py:165,170`]. JaroWinkler+prefix sobre kanji/kana es casi inútil; nombres compuestos alemanes y diacríticos franceses necesitan normalización locale-aware. **Degrada en silencio** (recall↓ → m↓ → CI más ancho → más difícil sellar) sin lanzar fallo.
→ **RESOLUCIÓN:** la unidad de captura gobierna `m` y por tanto el CI → el pack aporta **config de resolución locale-aware** (insumo #8): normalización de nombre por script, blocking válido para los geo-codes del país (latino vs CJK). Para JP/no-latino: blocking por código geo + comparador de n-gramas/ICU en vez de JaroWinkler-prefix. **Mitigación inmediata:** el invariante UNION-con-dedup [VERIFIED `splink_merge.py:198-211`] impide que la unidad sea **más fina** que el resuelto, así que el peor caso es CI ancho (conservador), nunca sello inflado.

**B8 · [MEDIUM] `v_servable_dealer` (numerador canónico) hardcodea literales kind ES y está NO CABLEADO.**
`kind NOT IN ('particular','desguace') AND kind<>'garaje'` [VERIFIED `0056:35-37`]; ningún consumidor lo lee [VERIFIED diseño cap.#15]. Se ofrece como el fix canónico pero no puede servir a un país nuevo sin recodificar su taxonomía.
→ **RESOLUCIÓN + OPEN ITEM (el núcleo genuinamente sin cerrar de esta etapa).** Hacer el **predicado** un parámetro de pack (qué kinds cuentan, gate de inventario). **OPEN ITEM:** cablearlo como ÚNICO numerador de stats/geo/seal **cambia una cifra de cara al usuario** → **gated** en ESCRITURA-EN-SERVING-OF-RECORD: pasa por dry-run→golden→Ferrari→CI antes de exponer. Hasta cablearlo, **toda fracción de cobertura es denominador-honesta pero numerador-ambigua** (tres scopes ~54,6k/geo/~18,3k vivos).

**B9 · [MEDIUM] Constantes de política ES presentadas como universales del motor.**
Banda `0.7-1.4` [VERIFIED `triangulation.py:75-80`]; `IDENT_CAP=5.0` [VERIFIED `estimators.py:304`]; `threshold 0.95` [VERIFIED `seal.py:27`]. En un país con ecosistema más delgado la mayoría de estratos fallan `IDENT_CAP` → `uncertified`, el roll-up honesto certifica ~0%, y `0.95` es inalcanzable **sin señal** de que CAP/threshold necesitan recalibración.
→ **RESOLUCIÓN:** mover `threshold/IDENT_CAP/banda` al pack (insumo #7) con default ES `0.95/5.0/0.7-1.4`, **justificados contra la calidad de datos local**. La auto-señal de "necesita recalibración" se cierra con H3 (gate de K<3).

**B10 · [MEDIUM] `CENSUS_CSV_NAME='dirce_cnae451.csv'` declarado agnóstico pero nombra el DIRCE CNAE-451 español; el vocabulario de segmentos del CSV es ES.**
[VERIFIED `triangulation.py:27`]; el esquema fija `segment ∈ {compraventa,concesionario,desguace,otros}` (vocabulario ES). [VERIFIED contrato en diseño cap.#16-17]
→ **RESOLUCIÓN:** renombrar a `external_census.csv` (agnóstico) o nombrarlo por manifiesto de pack; el vocabulario de segmentos del CSV se alinea al país vía insumo #3 (taxonomía). `status(country_code)` deja de mentir la ruta.

### Pack faltante (missing_pack)

**P1 · Geografía administrativa del país + columna `country_code` enhebrada de geo→entity→capture→estimate.** → Cubierto por B1 (columna) + adaptador geo de Etapa 6 (árbol/códigos). Sin esto el sello **ni siquiera puede keyear sus estratos**. **Resoluble**, es el primer paso del onboarding.

**P2 · ≥3 listas MSE ortogonales locales con mapeo `source_key→bucket`, cada una €0 y probadamente independiente.** → Ver B3: **el pack DEBE PROBAR ortogonalidad, no asumirla**. Gated en `KNOW_COUNTRY`. **OPEN ITEM** si el país no las tiene (límite real declarado).

**P3 · Ontología kind + segmento + predicado canónico de punto-venta en kinds locales.** → Cubierto por B5 (taxonomía) + B8 (predicado parametrizado). **Resoluble**; el cableado del numerador queda gated (B8).

**P4 · Censo externo independiente con su propia provenance `[MEDIDO]/[ESTIMADO]`, base por-segmento propia, fichero bien nombrado, vocabulario alineado.** → Cubierto por B10 + insumo #1. **Resoluble**; **prohibido fabricar** — sin censo honesto, `no_anchor` declarado.

**P5 · Constantes de política calibradas por país.** → Cubierto por B9. **Resoluble** (mover a pack).

**P6 · Config de resolución de entidad locale-aware.** → Cubierto por B7. **Resoluble**; crítico para CJK.

**P7 · Partición de serving por país (`latest` por país).** → Cubierto por B6. **Resoluble**; exige la columna de B1.

**P8 · Reconstrucción o retiro explícito del sello registral legacy por país.** → Cubierto por B4. **Resolución recomendada:** declararlo **legacy-ES fuera del sello genérico**; el país nuevo se sella por MSE+triangulación.

### Huecos de sellado (sealing_holes)

**H1 · El ancla de triangulación es NO VINCULANTE.**
`seal.py:42-47` sella por **auto-consistencia interna** (`coverage_lower>=0.95`) e **ignora** `external_ref`; el objetivo Fase-4 "no se puede sellar si `n_obs < threshold·n_external`" está **sin implementar** [VERIFIED `seal.py:42-47` vs `:179,195` (ancla solo se almacena)]. En un país con 2-3 listas ruidosas el MSE puede ser internamente consistente pero **muy sesgado**, y declarar SELLADO sobre un denominador que el censo rechazaría.
→ **OPEN ITEM con mitigación.** **Causa:** el fix correcto (inyectar `n_external` como **margen-conocido/celda-marginal** en el ajuste Fienberg, estilo población parcialmente conocida) es un refinamiento estadístico de esfuerzo **L** (ver Nivel Inalcanzable #1), no un parche. **Mitigación viva:** los dos canales (R crosscheck `tol=0.25` + verdict de triangulación `0.7-1.4`) **DETECTAN** el sesgo y marcan `distrust`/`n_hat_high`; la doctrina exige las tres vías alineadas antes de declarar sellado [VERIFIED `seal.py:78-81`, `triangulation.py:66-81`]. **Gating:** hasta implementar el margen-conocido, el sello con `n_hat_high` **no se declara** (regla operativa), aunque el código no lo bloquee. No se oculta: es el hueco #1 declarado.

**H2 · Sin `country_code` en el veredicto: el roll-up nacional suma a través de países.**
`seal.py:84-107` suma "estratos identificados" **sin filtro de país**; en DB compartida sumaría un N̂ global sin sentido. [VERIFIED `seal.py:91-96`]
→ **RESOLUCIÓN:** cubierto por B1+B2 — con `country_code` enhebrado, el roll-up agrupa por país y `certify(country_code)` aísla. Reversible. **Debe entrar con B1** o el primer build multi-país corrompe el nacional.

**H3 · `IDENT_CAP`/`threshold` no dan señal de "necesita calibración de país".**
Cuando un país nuevo sella ~0% (fuentes delgadas, `K<3`) la salida es **indistinguible** de "país genuinamente 0% cubierto". [VERIFIED lógica `estimators.py:307-318`, `seal.py:42-47`]
→ **RESOLUCIÓN:** añadir un **gate de pre-vuelo** que cuente listas ortogonales con datos por estrato y emita `insufficient_lists` (causa explícita) cuando `K<3` domina — distingue "no observado por falta de listas" de "no cubierto". Es diagnóstico aditivo, reversible. Cruza con B9 (constantes al pack) y la palanca g1.

**H4 · Rollback solo por-vista; sin rollback para matriz de captura mal-keyada multi-país.**
Si un build DE escribe códigos Kreis truncados a `char(2)` junto a filas ES en `discovery_capture`, **no hay predicado country** para `DELETE` limpio de solo-DE, y el serving global-latest se voltea igual. [VERIFIED ausencia de `country_code` en `0048:36-44`]
→ **RESOLUCIÓN:** cubierto por B1 — `country_code` da el predicado `DELETE WHERE country_code=… AND build_run_id=…`; combinado con append-only por build, el rollback queda limpio y scoped. **Pre-requisito:** la columna debe existir **antes** del primer build no-ES (orden de migración no negociable).

**H5 · Mismatch de scope en el ancla nacional: incluye `'otros'` en N̂ pero el techo censal lo excluye.**
`seal.py` compara `n_hat_sum` nacional (que **incluye** estratos `'otros'`) contra el ancla all-segment `(None,None)` que **excluye** `'otros'` por diseño del censo ES. [VERIFIED `seal.py:96,146-148`; exclusión declarada en provenance del censo ES, diseño cap.#17] La doctrina lo avisa en prosa pero **el código lo computa igual**; en un país cuya cuota `'otros'` difiera de ES, el veredicto nacional se **desplaza en silencio**.
→ **RESOLUCIÓN:** computar el ancla nacional **like-for-like** — sumar `n_external` sobre el **mismo set de segmentos** que entra en `n_hat_sum`, o excluir `'otros'` de ambos lados. Es un fix de cómputo (no de esquema), reversible, y debe entrar con el cableado del censo de cada país. **Resoluble.**

### Resumen del veredicto
- **El MOTOR numérico HOLDS** (álgebra invariante, verificado). **La CADENA DE SELLADO no** (country-BLIND por debajo del esquema).
- **Cierran por diseño** (enhebrado `country_code` + `DEFAULT='ES'` + mover dicts a pack), todo reversible, sin gate: **B1, B2, B5, B6, B9, B10, P1, P3(parc.), P4, P5, P6, P7, P8, H2, H3, H4, H5**.
- **OPEN ITEMS con causa y gating declarados (no ocultos):**
  1. **B8/P3 — numerador canónico sin cablear** (el núcleo genuinamente sin cerrar): gated en ESCRITURA-SERVING-OF-RECORD; dry-run→golden→Ferrari→CI.
  2. **H1 — ancla no vinculante:** fix = margen-conocido en Fienberg (esfuerzo L, Nivel Inalcanzable #1); mitigado por detección R+triangulación; regla operativa "no sellar con `n_hat_high`".
  3. **B3/P2 — ≥3 listas ortogonales:** límite estructural real; gated en `KNOW_COUNTRY`; si el país no las tiene, no-sellable por encima de Chapman (declarado con causa, no fingido).
- **Estado de cifras:** 37,7%/80,5% son **[ASSUMED]** punto-en-el-tiempo; re-correr `cli.py` contra DB viva antes de declarar progreso.

---

## Sub-proyectos institucionales (360 por faceta)

> **Qué es esta sección.** Cada **faceta** del motor de Calidad/Sello tratada como un **proyecto institucional 360**: verificación átomo-a-átomo `[VERIFIED path:línea]` leyendo la fuente real, mecanismo al átomo, **costura** ES→genérico, **fix** exacto, pasada **adversarial** (DE/FR/IT/PT/no-UE), **sellado** multi-vía y **herramienta NEXT-LEVEL** €0. Son **26 facetas** derivadas de los 7 deep-dives por ola (`g0`–`g6`). Honestidad cruda: los open items se declaran con causa, nunca se maquillan; las cifras vivas siguen **punto-en-el-tiempo** (stack caído).
>
> **Cómo leer cada faceta (funnel).** Primero la **Ficha 360** (digest escaneable: costura · fix · adversarial · sellado · herramienta); luego el **deep-dive** `(a)`–`(f)` con la prueba `[VERIFIED]`. Las referencias internas a `break #N` / `sealing_hole #N` apuntan al catálogo del [Veredicto](#veredicto-adversarial-roturas--resolución) (B#/P#/H#); alguna numeración inline «faceta N» proviene de los índices de trabajo de las olas, no de la numeración 01–26 de aquí.

### Índice de facetas

1. [Faceta 01 — Estimador Chapman 2-listas + bootstrap CI](#faceta-01--estimador-chapman-2-listas--bootstrap-ci) · `g0`
2. [Faceta 02 — Seam de triangulacion-contraste contra censo externo](#faceta-02--seam-de-triangulacion-contraste-contra-censo-externo) · `g0`
3. [Faceta 03 — Doctrina de ortogonalidad (las 7 clases universales)](#faceta-03--doctrina-de-ortogonalidad-las-7-clases-universales) · `g0`
4. [Faceta 04 — Sello registral legacy + desambiguacion del doble-sistema](#faceta-04--sello-registral-legacy--desambiguacion-del-doble-sistema) · `g0`
5. [Faceta 05 — Estimador Fienberg K-listas log-lineal + seleccion BIC](#faceta-05--estimador-fienberg-k-listas-log-lineal--seleccion-bic) · `g1`
6. [Faceta 06 — Hacer VINCULANTE el ancla censal (gate no implementado)](#faceta-06--hacer-vinculante-el-ancla-censal-gate-no-implementado) · `g1`
7. [Faceta 07 — Mapeo source_key->bucket (membresia por pais, data-driven)](#faceta-07--mapeo-source_key-bucket-membresia-por-pais-data-driven) · `g1`
8. [Faceta 08 — Calibracion de constantes de politica + gate de evidencia insuficiente](#faceta-08--calibracion-de-constantes-de-politica--gate-de-evidencia-insuficiente) · `g1`
9. [Faceta 09 — Cota dependence-robust de identificacion parcial](#faceta-09--cota-dependence-robust-de-identificacion-parcial) · `g2`
10. [Faceta 10 — Vectorizacion de patrones de captura (read_patterns)](#faceta-10--vectorizacion-de-patrones-de-captura-read_patterns) · `g2`
11. [Faceta 11 — Numerador canonico / predicado de punto-de-venta (v_servable_dealer)](#faceta-11--numerador-canonico--predicado-de-punto-de-venta-v_servable_dealer) · `g2`
12. [Faceta 12 — 100% como intervalo + detector de saturacion](#faceta-12--100-como-intervalo--detector-de-saturacion) · `g2`
13. [Faceta 13 — Gate de identificabilidad IDENT_CAP + dispatcher de estrato](#faceta-13--gate-de-identificabilidad-ident_cap--dispatcher-de-estrato) · `g3`
14. [Faceta 14 — Unidad de captura e integridad del overlap (m)](#faceta-14--unidad-de-captura-e-integridad-del-overlap-m) · `g3`
15. [Faceta 15 — Particion de region + diseno de la rejilla de estratificacion](#faceta-15--particion-de-region--diseno-de-la-rejilla-de-estratificacion) · `g3`
16. [Faceta 16 — Orquestacion de ejecucion, config DSN/env + CLI de onboarding](#faceta-16--orquestacion-de-ejecucion-config-dsnenv--cli-de-onboarding) · `g3`
17. [Faceta 17 — Criterio de sello por estrato + figura coverage_lower anti-maquillaje](#faceta-17--criterio-de-sello-por-estrato--figura-coverage_lower-anti-maquillaje) · `g4`
18. [Faceta 18 — Merge probabilistico Splink + resolucion locale-aware](#faceta-18--merge-probabilistico-splink--resolucion-locale-aware) · `g4`
19. [Faceta 19 — Esquema de almacenamiento MSE + persistencia append-only](#faceta-19--esquema-de-almacenamiento-mse--persistencia-append-only) · `g4`
20. [Faceta 20 — Contrato de test + barrido CI (matematica + pack + por-pais)](#faceta-20--contrato-de-test--barrido-ci-matematica--pack--por-pais) · `g4`
21. [Faceta 21 — Roll-up nacional honesto + split certified/uncertified](#faceta-21--roll-up-nacional-honesto--split-certifieduncertified) · `g5`
22. [Faceta 22 — Artefacto censo externo + contrato de provenance](#faceta-22--artefacto-censo-externo--contrato-de-provenance) · `g5`
23. [Faceta 23 — Llave de estrato multi-tenant (country_code + region text)](#faceta-23--llave-de-estrato-multi-tenant-country_code--region-text) · `g5`
24. [Faceta 24 — Canal R de verificacion ortogonal (Rcapture + LCMCR)](#faceta-24--canal-r-de-verificacion-ortogonal-rcapture--lcmcr) · `g6`
25. [Faceta 25 — Ontologia de tipos de dealer + colapso a segmentos](#faceta-25--ontologia-de-tipos-de-dealer--colapso-a-segmentos) · `g6`
26. [Faceta 26 — Vista de serving + endpoints API (latest-por-pais)](#faceta-26--vista-de-serving--endpoints-api-latest-por-pais) · `g6`

---

### Faceta 01 — Estimador Chapman 2-listas + bootstrap CI

> **Ficha 360**
>
> **Costura** — chapman() es matematica pura country-invariante (cero literales ES/DB/R, estimators.py:1-5,77-132). La costura no esta en la funcion sino en su FRECUENCIA DE USO: el dispatcher (estimators.py:342-360) cae a Chapman K==2 como excepcion en ES (fuentes densas) pero como NORMA en paises de ecosistema delgado (DE/FR/IT/PT: solo GEO+OEM cross-border, K cae a 2), volviendo el sello nacional un mar de 'low' que nunca certifica.
>
> **Fix** — No tocar chapman() (no romper lo correcto). Anadir una ruta sparse-MSE de primera clase (SparseMSE/dga via el bridge Rscript existente estimators_r.py:86-129) para estratos K<3/solapamiento-cero, conservando Chapman como suelo honesto cuando hasta esa ruta degenera. El confidence='low' (estimators.py:122) se mantiene como invariante estructural: K=2 jamas sella, solo pone piso.
>
> **Adversarial** — Pais delgado -> casi todo estrato K=2 -> sello ~0% indistinguible de pais genuinamente vacio (sealing_hole #3). m muy pequeno -> bootstrap inestable, N_hat puede explotar via (m+1) en el denominador; seed fijo da reproducibilidad pero oculta la fragilidad si no se auditea el ancho del CI. Dos listas que son espejos del mismo mecanismo inflan m -> N_hat subestimado -> coverage_lower miente al alza, y Chapman no detecta no-ortogonalidad con K=2.
>
> **Sellado** — Multi-via: (1) textbook N_hat(200,120,40)=592.24 [test_exhaustiveness.py:19-23]; (2) bracketing ci_low<=n_hat<=ci_high y ci_low>=n_obs [l.26-31]; (3) guarda m>n1 lanza ValueError, falla CERRADO [l.34-36]; (4) determinismo por seed=20260620 -> CI byte-identico; (5) cross-check R/SparseMSE bajo tol=0.25. confidence='low' forzado impide que el suelo se presente como certificacion.
>
> **Herramienta NEXT-LEVEL** — SparseMSE (GPL>=2, https://cran.r-project.org/package=SparseMSE) [VERIFIED NEXT-LEVEL.md:119]: intervalo finito donde el 2-list floor degenera, via el Rscript bridge existente, degrada graceful sin R. Complemento dga (Bayesian Model Averaging, GPL>=2, https://cran.r-project.org/package=dga) [VERIFIED NEXT-LEVEL.md:127] para que el sello deje de depender de un solo modelo. EUR0=True.

#### (a) Verificacion de code_hints [VERIFIED]
- `chapman_point(n1,n2,m)` [VERIFIED estimators.py:77-83]: `n_hat = ((n1+1)*(n2+1)/(m+1)) - 1` (l.79); varianza Seber `num=(n1+1)*(n2+1)*(n1-m)*(n2-m)`, `den=(m+1)**2*(m+2)`, `var=num/den if den>0 else inf` (l.80-82). Es el estimador insesgado-en-pequena-muestra de Petersen.
- `chapman(...)` [VERIFIED estimators.py:86-132]: firma con `n_boot=4000` (l.91) y `seed=20260620` (l.92) por KEYWORD-only; guarda de conteos imposibles `if m<0 or n1<m or n2<m: raise ValueError` (l.99-100); `n_obs=n1+n2-m` (l.101).
- Bootstrap no-parametrico [VERIFIED estimators.py:104-121]: `labels = [0]*only1 + [1]*only2 + [2]*m` con `only1=n1-m, only2=n2-m` (l.107-109), 0=L1 / 1=L2 / 2=ambos; `rng=np.random.default_rng(seed)` (l.110); loop `for i in range(n_boot)` (l.113) re-muestrea la UNION etiquetada con `rng.choice(labels, size=size, replace=True)` (l.114), reconstituye `bn1,bn2,bm` por conteo de etiquetas (l.115-117) y re-aplica `chapman_point` (l.118).
- Pisos del CI [VERIFIED estimators.py:120-121]: `ci_low = max(n_obs, percentile(boot,2.5))`, `ci_high = max(ci_low, percentile(boot,97.5))` — el suelo `n_obs` impide "menos de lo visto"; `ci_high` nunca por debajo de `ci_low`.
- `confidence = "low"` FORZADO con comentario "2-list is a floor, never a certification (per §2.3)" [VERIFIED estimators.py:122].
- Propiedades del tipo `Estimate` [VERIFIED estimators.py:61-71]: `coverage_point=n_obs/n_hat`; `coverage_lower=n_obs/ci_high` etiquetada "anti-maquillaje figure used for sealing".
- Dispatch K==2 [VERIFIED estimators.py:352-360]: calcula `n1,n2,m` por marginalizacion de `freqs` y llama `chapman(n1,n2,m)`, luego `_mark_identified`.
- Tests [VERIFIED tests/test_exhaustiveness.py:19-36]: `test_chapman_point_textbook` exige `N_hat≈592.24` para (200,120,40) (l.19-23); `test_chapman_estimate_ci_brackets_point` exige `n_obs==280`, `ci_low<=n_hat<=ci_high`, `ci_low>=n_obs`, `confidence=="low"` (l.26-31); `test_chapman_rejects_impossible_overlap` exige `ValueError` para `chapman(10,10,20)` (m>n1) (l.34-36).

#### (b) El mecanismo al atomo
La via de captura-recaptura para K=2 listas ortogonales. Petersen-Chapman estima la celda no-observada como `(n1+1)(n2+1)/(m+1)-1`; el +1 de Chapman corrige el sesgo de muestra pequena del Petersen crudo `n1*n2/m`. La clave del 360 es que el CI **NO** usa la varianza Seber-Wald (que es asimptotica y subcuenta cuando `m` es chico) sino un bootstrap que re-muestrea el vector de etiquetas {solo-L1, solo-L2, ambos}: al reconstruir `bm` por conteo de la etiqueta 2 en cada re-muestra, la **discreteza de `m`** se propaga honestamente al ancho del intervalo. El `seed` fijo (una fecha, no un literal ES) da reproducibilidad byte-estable. El `confidence="low"` no es opinion: es un INVARIANTE estructural — 2 listas jamas certifican, solo ponen suelo, porque con K=2 la independencia no es testeable (no hay grados de libertad para una interaccion). El resultado entra a `_mark_identified` y compite contra `IDENT_CAP` igual que cualquier estimador.

#### (c) Costura ES -> generico
El nucleo `chapman()` es matematica PURA country-invariante: cero literales ES, cero DB, cero R (por diseno, docstring l.3-5). La costura NO esta dentro de la funcion sino en su FRECUENCIA DE USO: el dispatcher cae a Chapman siempre que un estrato tiene exactamente K=2 listas presentes. En ES el ecosistema de fuentes es denso (7 clases ortogonales pobladas) y K=2 es la excepcion; en un pais de fuentes delgadas (DE/FR/IT/PT con solo GEO+OEM cross-border, break #3) K=2 es la NORMA y el pais entero se vuelve un mar de Chapman 'low' que nunca sella. La costura, por tanto, es metodologica: el motor asume implicitamente "K=2 es raro". El fix no toca `chapman()` (no se rompe lo correcto) sino que ANADE una ruta de primera clase para estratos sparse — ver (f) — y mantiene Chapman como el suelo honesto cuando hasta esa ruta degenera.

#### (d) Riesgo adversarial concreto
- **Pais de ecosistema delgado (DE/FR/IT/PT):** casi todo estrato cae a K=2 -> sello nacional ~0% por construccion, INDISTINGUIBLE de "pais genuinamente 0% cubierto" (acopla con sealing_hole #3 / faceta 23).
- **`m` muy pequeno:** el bootstrap re-muestrea poquisimas etiquetas '2'; `chapman_point` con `m` que colapsa a 0 en alguna re-muestra dispara `(m+1)` en el denominador -> N_hat puede explotar; el `seed` fijo da reproducibilidad pero OCULTA la fragilidad si nadie auditea el ancho del CI (`ci_high/n_hat`).
- **Ruido (no-UE / marketplaces disfrazados):** si las "2 listas" son en realidad dos espejos del mismo mecanismo, `m` se infla artificialmente (sobre-solapan) -> N_hat se subestima -> coverage_lower miente al alza. Chapman no puede detectar la no-ortogonalidad con K=2 (sin grados de libertad).

#### (e) Criterio de sellado + verificacion multi-via
Chapman SOLO entra al sello via su `coverage_lower=n_obs/ci_high` y solo si `_mark_identified` lo deja identified; aun asi `confidence="low"` lo marca como suelo. Verificacion ortogonal:
1. **Textbook:** `N_hat(200,120,40)=592.24` exacto [test l.19-23].
2. **Propiedad de bracketing:** `ci_low<=n_hat<=ci_high` y `ci_low>=n_obs` [test l.26-31] — el sello no puede afirmar menos de lo visto.
3. **Guarda de imposibilidad:** `m>n1` lanza ValueError [test l.34-36] — datos corruptos fallan CERRADO, no producen un N silencioso.
4. **Determinismo:** mismo `seed` -> mismo CI byte-identico (re-run gate).
5. **2a via R:** cross-check contra Rcapture/SparseMSE bajo `tol=0.25` (estimators_r.crosscheck) sobre los mismos `n1,n2,m`.

#### (f) Herramienta NEXT-LEVEL
**SparseMSE** (Chan-Silverman-Vincent 2019) — Multiple Systems Estimation for Sparse Capture Data. Es la palanca exacta para el fallo no-ES CRITICAL: estratos con pares de listas de solapamiento CERO o casi-cero donde el log-lineal Python degenera a observed-only/inf-CI y Chapman queda como unico suelo 'low'. SparseMSE maneja la no-existencia del MLE, parametros en -inf y la no-identificabilidad, devolviendo un intervalo FINITO; corre por el mismo Rscript subprocess bridge que ya existe (estimators_r.py) y degrada graceful si R ausente. Convierte un pais de fuentes pobres de "sella ~0%" a "sella lo que el sparse-MSE puede fijar".
- URL: https://cran.r-project.org/package=SparseMSE — Lic: **GPL (>=2)** [VERIFIED NEXT-LEVEL.md:119], EUR0=True.
- Trio 2a-via complementario: **dga** (Bayesian Model Averaging, GPL>=2, https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127]) integra la incertidumbre de seleccion-de-modelo en el intervalo, asi el suelo Chapman deja de depender de UN modelo.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 02 — Seam de triangulacion-contraste contra censo externo

> **Ficha 360**
>
> **Costura** — La parametricidad por pais existe a medias: census_dir(country_code) y la firma load_external_census(country_code) son genericas (triangulation.py:36-50, paths.py:50-52), pero quedan cortocircuitadas por CENSUS_CSV_NAME='dirce_cnae451.csv' (l.27, provenance ES), CENSUS_DIR/DEFAULT_CSV bindeadas en import-time a ES (l.32-33) que hacen status() reportar siempre la ruta ES (l.84-88), y seal.compute auto-cargando load_external_census() SIN country_code (seal.py:69) -> un build DE triangula contra el censo espanol. Ademas n_hat_sum incluye 'otros' (seal.py:96) pero el ancla (None,None) no.
>
> **Fix** — Enhebrar country_code de cli->compute->load_external_census(country_code); renombrar CENSUS_CSV_NAME a generico ('census.csv') o manifest por pais; mover CENSUS_DIR/DEFAULT_CSV de import-time a resolucion por-llamada y parametrizar status(country_code); reconciliar scope (excluir 'otros' del sumatorio triangulado O exigir fila-ancla 'otros' en el CSV) para que (None,None) compare scopes iguales.
>
> **Adversarial** — dirce_cnae451.csv mis-etiqueta la provenance de cualquier pais (break #10); aunque el operador deje el CSV DE correcto, seal.compute carga ES por defecto (break #2) y status() reporta la ruta ES. Scope mismatch (sealing_hole #5): el ancla nacional excluye 'otros' pero n_hat_sum lo incluye -> veredicto nacional desplazado en silencio para cualquier pais cuya cuota 'otros' difiera de ES. Censo de provenance dudosa sin tag [MEDIDO]/[ESTIMADO] da falsa confianza dentro de 0.7-1.4.
>
> **Sellado** — Multi-via: (1) verdicts consistent/high/low/no_anchor [test_exhaustiveness.py:208-214]; (2) carga CSV con clave nacional (None,None)=40000 [l.217-227]; (3) NUEVA scope-equality assertion (segmentos del n_hat_sum == scope del ancla, test que inyecte 'otros' grande); (4) provenance [MEDIDO]/[ESTIMADO DECLARADO] impuesta por el contrato de 8 tests del ancla; (5) panel multi-ancla: >=2 anclas independientes en banda y su desacuerdo = distrust, no promedio.
>
> **Herramienta NEXT-LEVEL** — Eurostat SBS (NACE G45, https://ec.europa.eu/eurostat/web/structural-business-statistics) Reutilizacion libre Decision 2011/833/EU [VERIFIED NEXT-LEVEL.md:191] = techo registral generico para todo pais UE; GLEIF LEI Golden Copy CC0 1.0 (https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy) [VERIFIED NEXT-LEVEL.md:175] ancla registral dia-uno; Great Expectations Apache-2.0 (https://github.com/great-expectations/great_expectations) [VERIFIED NEXT-LEVEL.md:167] para que el scope-mismatch falle CERRADO. EUR0=True.

#### (a) Verificacion de code_hints [VERIFIED]
- Import country-aware [VERIFIED triangulation.py:24]: `from pipeline.paths import DEFAULT_COUNTRY, census_dir`.
- `CENSUS_CSV_NAME = "dirce_cnae451.csv"` [VERIFIED triangulation.py:27] — el filename hornea la provenance ESPANOLA (DIRCE/CNAE-451) en una constante "country-agnostic" segun su propio comentario (l.26), lo que es una contradiccion.
- `CENSUS_DIR = census_dir()` (l.32) y `DEFAULT_CSV = CENSUS_DIR / CENSUS_CSV_NAME` (l.33) [VERIFIED]: se evaluan en IMPORT-TIME con `census_dir()` sin argumento -> `<repo>/countries/ES/census` [VERIFIED pipeline/paths.py:50-52 + DEFAULT_COUNTRY="ES" l.22]. Quedan atados a ES para toda la vida del proceso.
- `load_external_census(path=None, country_code=DEFAULT_COUNTRY)` [VERIFIED triangulation.py:36-63]: la firma YA es parametrica (`country_code`), resuelve `p = path or (census_dir(country_code)/CENSUS_CSV_NAME)` (l.50); fila con prov/seg vacios -> clave `(None,None)` ancla nacional (l.56-57); devuelve `{}` si el fichero no existe (l.51-52).
- `triangulate(n_hat, n_external)` [VERIFIED triangulation.py:66-81]: `ratio=n_hat/n_external`; `>1.4 -> n_hat_high`, `<0.7 -> n_hat_low`, else `consistent`; `None/<=0 -> no_anchor` (l.72-80).
- `status()` [VERIFIED triangulation.py:84-88]: usa la constante de modulo `DEFAULT_CSV` (ES) -> SIEMPRE reporta la ruta ES aunque se cargue otro pais.
- Integracion en sello [VERIFIED seal.py:68-69]: `if external_census is None: external_census = triangulation.load_external_census()` — invocado SIN `country_code` -> defaultea a ES.
- Contraste nacional [VERIFIED seal.py:144-148]: `triangulation.triangulate(n_hat_sum, external_census.get((None,None)))`.
- Mismatch de scope [VERIFIED seal.py:96]: `n_hat_sum = sum(s.estimate.n_hat for s in identified)` suma TODOS los estratos identificados, incluido `segment='otros'`; el ancla `(None,None)` es un total nacional unico. Si el censo nacional excluye 'otros' (DIRCE CNAE-451 solo cuenta venta), se compara una suma que incluye 'otros' contra un techo que no.
- Tests [VERIFIED tests/test_exhaustiveness.py:208-227]: `test_triangulation_verdicts` exige consistent/n_hat_high/n_hat_low/no_anchor (l.211-214); `test_triangulation_loads_csv` confirma `(28,compraventa)->1200`, fila vacia -> `(None,None)->40000` (l.217-227).

#### (b) El mecanismo al atomo
Es la 2a via NO-vinculante (hoy reportada, no gateante): contrasta el N_hat del MSE contra un censo construido por un MECANISMO DISTINTO (registro fiscal/estadistico), porque un N_hat es creible solo si concuerda con algo que no comparte su sesgo. El atomo es la banda `[0.7, 1.4]` sobre el ratio `N_hat/n_external`: dentro = consistent, arriba = n_hat_high (listas correlacionadas no modeladas o dedup imperfecto), abajo = n_hat_low (cobertura externa mas amplia o estratos faltantes). La firma de `load_external_census` ya acepta `country_code`, pero TRES amarres la matan en la practica: el filename `dirce_cnae451.csv` (provenance ES), las constantes de modulo `CENSUS_DIR/DEFAULT_CSV` evaluadas en import-time contra ES, y la llamada de `seal.compute` que omite `country_code`. El veredicto se anexa a `diagnostics`/se persiste en `external_ref` pero NUNCA cambia el `sealed` (faceta 9 es el gate no-construido).

#### (c) Costura ES -> generico
La parametricidad existe a medias: `census_dir(country_code)` y la firma de `load_external_census` son genericas, pero quedan cortocircuitadas por (1) `CENSUS_CSV_NAME="dirce_cnae451.csv"` que asume nomenclatura ES para todo pais; (2) `CENSUS_DIR`/`DEFAULT_CSV` bindeadas en import-time -> `status()` siempre miente la ruta ES; (3) `seal.compute` auto-carga `load_external_census()` sin pasar `country_code` (seal.py:69), asi que un build DE triangula contra el censo ESPANOL. (4) El mismatch de scope: `n_hat_sum` incluye 'otros', el ancla `(None,None)` no.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT:** `dirce_cnae451.csv` mis-etiqueta la provenance de cualquier pais (break #10); aunque el operador deje el CSV correcto en `countries/DE/census/`, `seal.compute` igual carga ES por defecto (break #2). El `status()` reporta la ruta ES incluso tras cargar DE.
- **Scope mismatch (sealing_hole #5):** el ancla nacional EXCLUYE 'otros' pero `n_hat_sum` lo INCLUYE -> el veredicto nacional se desplaza silenciosamente en cualquier pais cuya cuota 'otros' difiera de ES (en ES 'otros' es residual; en un pais con taxonomia distinta puede ser grande).
- **No-UE / ruido:** un censo de provenance dudosa (auto-declarado, no medido) tomado como techo veta o valida indebidamente; sin tag [MEDIDO]/[ESTIMADO DECLARADO] el ratio 0.7-1.4 da falsa confianza.

#### (e) Criterio de sellado + verificacion multi-via
La triangulacion hoy NO sella (advisory). Para elevarla a senal de sellado fiable:
1. **Unit verdicts:** consistent/high/low/no_anchor exactos [test l.208-214].
2. **Carga CSV + clave nacional:** `(None,None)` parsea bien [test l.217-227].
3. **Scope-equality assertion (NUEVA):** el conjunto de segmentos del `n_hat_sum` triangulado DEBE igualar el scope del ancla (excluir 'otros' del sumatorio O exigir una fila-ancla 'otros'); un test que inyecte un pais con 'otros' grande y verifique que el veredicto no se desplaza.
4. **Provenance contract:** SOURCE.md tagueado [MEDIDO]/[ESTIMADO DECLARADO] (faceta 13) impuesto por test.
5. **Multi-ancla (2a y 3a via):** que >=2 anclas independientes aterricen el N_hat en banda, y que su DESACUERDO sea senal de distrust, no promedio.

#### (f) Herramienta NEXT-LEVEL
**Panel de anclas multiples auto-minadas** sustituye el CSV-unico ES por un panel generico por pais:
- **Eurostat Structural Business Statistics (SBS, NACE G45 venta/reparacion de vehiculos)** — conteo de establecimientos por pais UE = techo registral generico que EXISTE para DE/FR/IT/PT sin escribir adaptador. URL: https://ec.europa.eu/eurostat/web/structural-business-statistics — Lic: **Reutilizacion libre (Decision 2011/833/EU; atribucion)** [VERIFIED NEXT-LEVEL.md:191], EUR0=True.
- **GLEIF LEI Golden Copy** — entidades legales globales con pais+direccion, ancla registral CC0 dia-uno. URL: https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy — Lic: **CC0 1.0** [VERIFIED NEXT-LEVEL.md:175], EUR0=True.
- **Great Expectations** (validacion de datos como contrato pre-sello) para hacer el scope-mismatch FALLAR CERRADO: una expectativa "el vocabulario de segmentos del census casa el scope del n_hat_sum" niega el sello si no casan. URL: https://github.com/great-expectations/great_expectations — Lic: **Apache-2.0** [VERIFIED NEXT-LEVEL.md:167], EUR0=True.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 03 — Doctrina de ortogonalidad (las 7 clases universales)

> **Ficha 360**
>
> **Costura** — Las 7 clases (GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG, lists.py:49) son el invariante universal correcto. La costura es la MEMBRESIA: _EXACT (lists.py:27-45) es un dict ES y bucket_for (l.65-74) hornea la palabra espanola 'oficial' (l.71) y la marca 'mercedes' (l.69), con else->MKT (l.74) que FALLA ABIERTO. Una fuente de pais nuevo no mapeada cae a MKT y read_patterns la salta (capture.py:203-204), desapareciendo del MSE en silencio.
>
> **Fix** — Conservar las 7 clases como invariante; mover la membresia a datos (discovery_list(country_code,list_key,orthogonality_class), faceta 16, con el dict ES como semilla); volver bucket_for FALLA-CERRADO: un source_key desconocido se pone en cuarentena o lanza, jamas se traga como MKT. Anadir un contrato que exija >=3 buckets ortogonales con captura real por estrato sellado.
>
> **Adversarial** — DE/FR (break #3): solo GEO+OEM cross-border -> K cae a 2 en casi todo estrato -> el motor K>=3->log-lineal->sellable no arranca (doctrina correcta, roster sub-poblado). Falsa ortogonalidad: dos fuentes que comparten mecanismo (espejos del mismo registro) correlacionan y sesgan N_hat sin que nada lo detecte (el motor confia en la etiqueta, no la verifica). Fail-open: la fuente mas fuerte no mapeada cae a MKT y se excluye, coverage_lower sub-cuenta sin error.
>
> **Sellado** — Multi-via: (1) taxonomia DORK/REG ortogonales, GRAPH/COLLAPSE no, 7 cubiertas, metadata [test_exhaustiveness_vector_lists.py:17-47]; (2) NUEVO contrato K>=3 demostrado (no asumido) por estrato sellado; (3) test de ortogonalidad empirica (baja correlacion de solapamiento entre listas independientes); (4) fail-closed: source_key foraneo no mapeado FALLA el build; (5) linaje con >=3 aristas a buckets distintos por estrato sellado.
>
> **Herramienta NEXT-LEVEL** — GLEIF LEI Golden Copy (CC0 1.0, https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy) [VERIFIED NEXT-LEVEL.md:175]: lista REG ortogonal global dia-uno que restaura K>=3 en DE/FR/IT/PT, cerrando break #3. Complementos: Common Crawl + schema.org/AutoDealer (indice CC BY 4.0, https://commoncrawl.org/) [VERIFIED NEXT-LEVEL.md:183] como lista huella-web declarada; BoTorch (MIT, https://github.com/pytorch/botorch) [VERIFIED NEXT-LEVEL.md:111] selector VoI que rankea que lista ortogonal adquirir. EUR0=True.

#### (a) Verificacion de code_hints [VERIFIED]
- Doctrina [VERIFIED lists.py:1-22]: "Two source_keys belong to the same MSE list iff they share a capture mechanism (and are therefore NOT independent)" (l.3-4); los marketplaces colapsan a una sola lista MKT (l.5-7); GEO/CENSUS/DGT/ASSOC/OEM se mantienen separadas porque cada una descubre por un mecanismo genuinamente distinto (l.7-8).
- `ORTHOGONAL_LISTS = ("GEO","CENSUS","DGT","ASSOC","OEM","DORK","REG")` [VERIFIED lists.py:49] — 7 clases; MKT/GRAPH/COLLAPSE excluidas a proposito (l.47-48).
- `LIST_METADATA` [VERIFIED lists.py:51-62]: 10 entradas (las 7 ortogonales + GRAPH/COLLAPSE/MKT) con (clase, descripcion); DORK="search_own_domain (V3)", REG="mercantile_registry (V4)", GRAPH="graph_dependent (V5, dependent)", COLLAPSE="resolution (V6)".
- `bucket_for(source_key)` [VERIFIED lists.py:65-74]: `_EXACT` primero (l.67-68); luego prefijos `oem_`/`mercedes` -> OEM (l.69); `'oficial' in source_key` o `endswith('_new_stock')` -> OEM (l.71); **else -> MKT (l.74)** = FALLA ABIERTO.
- `orthogonal_buckets(include_mkt=False)` [VERIFIED lists.py:77-81]: orden fijo = `ORTHOGONAL_LISTS` (+ MKT si include_mkt).
- Consumo en el motor [VERIFIED capture.py:175-176]: `read_patterns` toma `buckets=orthogonal_buckets(include_mkt)`, `idx={b:i...}`; cada `list_key not in idx` se SALTA (l.203-204) -> una lista no-mapeada (caida a MKT) desaparece del patron 0/1 sin error. El K del estrato = numero de buckets ortogonales con captura.
- Tests [VERIFIED tests/test_exhaustiveness_vector_lists.py:29-44]: `test_v3_v4_are_orthogonal` exige DORK y REG en ORTHOGONAL_LISTS y que `orthogonal_buckets()` cubra las 7 (l.29-32); `test_v5_v6_are_not_orthogonal` exige GRAPH/COLLAPSE FUERA (l.36-39); `test_bucket_for_vectors` mapea overture->GEO, dork_municipal->DORK, borme_cnae->REG, graph_recursive->GRAPH, collapse_invisible->COLLAPSE (l.17-25); metadata presente para las nuevas (l.43-47).

#### (b) El mecanismo al atomo
Es el INVARIANTE semantico sobre el que descansa TODA la matematica captura-recaptura: las 7 clases (GEO/CENSUS/DGT/ASSOC/OEM/DORK/REG) son mecanismos de descubrimiento genuinamente independientes, y dos `source_keys` del mismo mecanismo COLAPSAN a una lista (si no, fingirian independencia y sesgarian N). MKT (sesgo de seed marketplace), GRAPH (dependencia de grafo) y COLLAPSE (resolucion, no observacion) se EXCLUYEN deliberadamente. El atomo operativo es el orden fijo de `orthogonal_buckets`, que define la posicion de cada bit en el patron 0/1 que `read_patterns` arma por `(stratum, resolved_ulid)`; el K del estrato (cuantas clases lo vieron) decide el estimador (faceta 4). La doctrina es universal y correcta; el punto fragil es `bucket_for`, que traduce `source_key` real -> clase y FALLA ABIERTO a MKT.

#### (c) Costura ES -> generico
Las 7 clases SON el invariante universal (no se tocan: cualquier pais descubre por geo/registro/asociacion/OEM/dork/marketplace). La costura es la MEMBRESIA: `_EXACT` (lists.py:27-45) es un dict ES (osm/overture/autocasion_census/dgt_cat/aedra/aecs/acevas/borme_cnae...) y las heuristicas de prefijo hornean la palabra espanola `'oficial'` (l.71) y la marca `'mercedes'` (l.69). Una fuente de un pais nuevo que no casa ningun patron cae a MKT (l.74) y DESAPARECE del MSE en silencio (capture.py:203-204). Fix: conservar las 7 clases como invariante; mover la membresia a datos (`discovery_list(country_code, list_key, orthogonality_class)`, faceta 16, el dict ES como mera semilla); y volver `bucket_for` FALLA-CERRADO — un `source_key` desconocido se pone en cuarentena/lanza, no se traga como MKT.

#### (d) Riesgo adversarial concreto
- **DE/FR (break #3):** solo GEO+OEM son cross-border; CENSUS/DGT/ASSOC/DORK/REG estan vacias hasta tener adaptadores nacionales -> K cae a 2 en casi todo estrato -> el motor "K>=3 -> log-lineal -> sellable" no arranca. La doctrina es correcta pero el ROSTER esta sub-poblado.
- **Falsa ortogonalidad:** un pais mete dos fuentes que CREE independientes pero comparten mecanismo (dos espejos del mismo registro mercantil) -> la "ortogonalidad" es falsa, las listas correlacionan, y N_hat se sesga sin que NADA lo detecte (el motor confia en la etiqueta de clase, no la verifica).
- **Fail-open silencioso:** la fuente mas fuerte de un pais nuevo (p.ej. un registro local no mapeado) cae a MKT y se excluye del MSE -> coverage_lower sub-cuenta sin error visible.

#### (e) Criterio de sellado + verificacion multi-via
1. **Taxonomia:** DORK/REG ortogonales, GRAPH/COLLAPSE no, las 7 cubiertas, metadata presente [tests l.17-47].
2. **Contrato K>=3 por estrato (NUEVO):** un test/contrato de datos que verifique que cada estrato SELLADO tiene >=3 buckets ortogonales con captura real (no asumir, DEMOSTRAR).
3. **Test de ortogonalidad empirica:** baja correlacion de solapamiento entre listas declaradas independientes (dos espejos del mismo registro mostrarian solapamiento anomalo -> distrust).
4. **Fail-closed:** inyectar un `source_key` foraneo NO mapeado debe FALLAR el build (espejo del invariante country-proof), no caer a MKT.
5. **Linaje:** grafo que muestre, por estrato sellado, >=3 aristas a buckets distintos (prueba de K>=3 real).

#### (f) Herramienta NEXT-LEVEL
**GLEIF LEI Golden Copy** es la palanca que cierra break #3: una espina registral CC0 GLOBAL que surte una lista REG ortogonal a CADA pais el dia uno (cada entidad legal con LEI lleva pais + direccion + a menudo id de registro local), restaurando K>=3 en DE/FR/IT/PT sin escribir un adaptador de registro nacional.
- URL: https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy — Lic: **CC0 1.0 Universal (dominio publico, comercial OK, sin atribucion)** [VERIFIED NEXT-LEVEL.md:175], EUR0=True.
- Complementos que pueblan mas clases ortogonales generico: **Common Crawl + extractor schema.org/AutoDealer** (lista "huella web declarada", indice CC BY 4.0, https://commoncrawl.org/ [VERIFIED NEXT-LEVEL.md:183]); y **BoTorch** (MIT, https://github.com/pytorch/botorch [VERIFIED NEXT-LEVEL.md:111]) como selector activo Value-of-Information que rankea QUE lista ortogonal candidata adquirir para maximizar la reduccion del intervalo nacional por unidad de coste.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 04 — Sello registral legacy + desambiguacion del doble-sistema

> **Ficha 360**
>
> **Costura** — Es el sistema MAS atado a ES de la etapa; decision port-or-retire por pais, no reuso byte-identico. Amarres: raise SystemExit si no hay EXACTAMENTE 52 provincias (load_denominator_provincia.py:64-65) -> aborta en DE/FR/JP; RATIO_451_45=0.2605 es CNAE-451 espanol sin analogo (l.38); literales kind IN ('compraventa','concesionario_oficial')/'desguace' en SQL (0042:24, 0043:34); source_key='dgt_cat' censo ES (0043:31); DSN hardcodeado (l.34). El doble-sistema mide cosas distintas: registral=techo DIRCE (80.5%), MSE=cota inferior (37.7%).
>
> **Fix** — Declarar el INTERVALO MSE como canonico y el registral como contraste explicito (resolver risk #1, narrativa al consumidor); sustituir el techo DIRCE/DGT por un techo registral generico por pais (Eurostat SBS NACE G45.1 / GLEIF); bajar el assert-52 a 'numero de regiones segun geo'; parametrizar el set de kind y el source_key del censo de desguace; DSN por os.environ. Onboardar un pais = decidir portar (con techo generico) o retirar el registral, portando o omitiendo su contrato de test explicitamente.
>
> **Adversarial** — load_denominator_provincia ABORTA con SystemExit fuera de 52 provincias ES (break #4: DE=401 Kreise, FR=101 departements, JP=47 prefecturas); RATIO_451_45 sin analogo -> denominador venta inconstruible; literales kind/source_key ES no casan taxonomia local. Confusion del doble-sistema (risk #1): registral 80.5% (techo) vs MSE 37.7% (cota inferior) miden cosas distintas; sin declarar cual gobierna, '80.5% sellado' se lee como exhaustividad = maquillaje involuntario. Portar a pais sin registro publico fabrica techo sin provenance.
>
> **Sellado** — Multi-via: (1) invariantes de vista vivos: 52 prov x 2 segmentos, verdicts en set fijo, umbrales venta 85/50 y desguace found>=census [test_province_seal_view.py:59-95]; (2) regression guard del dedup: nacional venta 60-110%, no ~165% entity-level [l.119-126], protege la clave canonica COALESCE; (3) coverage=num/den con ROUND_HALF_UP de PG [l.97-112]; (4) NUEVO: doctrina declarada MSE-canonico vs registral-contraste, testeada en la superficie API; (5) port-or-retire por pais con su contrato portado u omitido explicitamente.
>
> **Herramienta NEXT-LEVEL** — Eurostat SBS (NACE G45, https://ec.europa.eu/eurostat/web/structural-business-statistics) Reutilizacion libre Decision 2011/833/EU [VERIFIED NEXT-LEVEL.md:191] = techo registral generico que elimina RATIO_451_45 y el assert-52; GLEIF CC0 (https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy) [VERIFIED NEXT-LEVEL.md:175] techo cross-border sin analogo CNAE; in-toto Apache-2.0 (https://github.com/in-toto/in-toto) [VERIFIED NEXT-LEVEL.md:143] atesta CUAL sello (MSE canonico vs registral contraste) salio de que inputs, resolviendo la confusion del doble-sistema. EUR0=True.

#### (a) Verificacion de code_hints [VERIFIED]
- `v_province_seal` VENTA [VERIFIED 0042_province_seal_view.sql:18-44]: numerador = `count(DISTINCT COALESCE(vdr.resolved_ulid, e.entity_ulid))` sobre `e.kind IN ('compraventa','concesionario_oficial')` con `EXISTS (vehicle status='available')` (l.19-28); denominador = `denominator_estimate.point_est` (segment='venta'); verdict `SELLADO>=85 / PARCIAL 50-85 / GAP<50` (l.36-41). El comentario documenta que usar `entity_ulid` sin dedup sobre-cuenta ~2x (164.9% vs 79.4% correcto) -> el COALESCE canonico es obligatorio (l.8-12).
- DESGUACE [VERIFIED 0043_province_seal_desguace.sql:16-66]: anade segmento desguace por UNION ALL; numerador = `count(DISTINCT entity_ulid)` de todos los desguaces hallados; denominador = los `FILTER (WHERE es.source_key='dgt_cat')` (l.28-35); verdict `SELLADO cuando numerador>=denominador` (found>=census), else GAP (l.61-65). Verificado live 52/52 SELLADO (1895>=1292) (l.10-11).
- `load_denominator_provincia.py` [VERIFIED]: `DSN` hardcodeado `postgresql://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep` (l.34); `RATIO_451_45 = 23085/88621 = 0.2605` (l.38); `den_venta = round(cnae45 * RATIO_451_45)` (l.53); **`if len(rows)!=52: raise SystemExit("ABORT: expected 52 provinces...")`** (l.64-65); pre-check FK contra `geo_province` (l.71-74); idempotente DELETE+INSERT segment='venta' (l.86-94).
- Tests [VERIFIED tests/test_province_seal_view.py]: 52 provincias en AMBOS segmentos (l.59-63); verdicts en set fijo {SELLADO,PARCIAL,GAP,NO_DENOM} (l.65-67); umbrales venta 85/50 (l.69-82); desguace discovery-seal >=100 (l.84-95); coverage=num/den con ROUND_HALF_UP de PG (l.97-112); no-negativos (l.114-117); **regression guard del bug dedup: nacional venta 60-110% (no ~165%)** (l.119-126); desguace found>=census nacional (l.128-131).

#### (b) El mecanismo al atomo
Es un sistema de sello PARALELO al MSE canonico, vivo como VISTA (no snapshot). Mide dos cosas estructuralmente distintas: VENTA = cobertura servida (concesionarios/compraventa CON stock disponible, deduplicados por la clave canonica `COALESCE(resolved_ulid, entity_ulid)`) contra un TECHO registral DIRCE CNAE-451; DESGUACE = cobertura de DESCUBRIMIENTO (hallados vs censo DGT-CAT), sellado cuando found>=census. El denominador venta se construye apportando el conteo CNAE-45 provincial por el ratio nacional 451/45=0.2605 (DIRCE 2025). El atomo critico de gobernanza: el sello registral mide TECHO (80.5%, cuanto del registro cubrimos) mientras el MSE mide COTA INFERIOR de exhaustividad (37.7%); son metricas ORTOGONALES y confundirlas es el riesgo #1. La narrativa correcta: el INTERVALO MSE es la verdad de exhaustividad; el registral es solo contraste/techo.

#### (c) Costura ES -> generico
Este es el sistema MAS atado a ES de la etapa, y la decision es port-or-retire por pais, no reuso byte-identico. Amarres: (1) `raise SystemExit` si no hay EXACTAMENTE 52 provincias (load_denominator_provincia.py:64-65) -> ABORTA en DE (401 Kreise), FR (101 departements), JP (47 prefecturas); (2) `RATIO_451_45` es CNAE-451 espanol sin analogo universal (l.38); (3) literales de taxonomia `kind IN ('compraventa','concesionario_oficial')` y `kind='desguace'` (0042 l.24, 0043 l.34) horneados en SQL; (4) `source_key='dgt_cat'` como censo de desguace (0043 l.31) es ES-especifico; (5) DSN hardcodeado (l.34) arrastra credencial dev. Fix: (a) declarar el MSE como canonico y el registral como contraste explicito (resolver risk #1); (b) sustituir el techo DIRCE/DGT por un techo registral generico por pais (Eurostat SBS NACE G45.1 / GLEIF); (c) bajar el assert-52 a "numero de regiones del pais segun geo"; (d) parametrizar el set de `kind` y el `source_key` del censo; (e) DSN por `os.environ`.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT/JP:** `load_denominator_provincia.py` ABORTA con SystemExit fuera de las 52 provincias ES (break #4); `RATIO_451_45` no tiene analogo -> el denominador venta no se puede construir; los literales `kind`/`source_key` ES no casan la taxonomia local.
- **Confusion del doble-sistema (risk #1):** registral 80.5% (techo DIRCE) vs MSE 37.7% (cota inferior) miden cosas DISTINTAS; si no se declara cual GOBIERNA, un consumidor lee "80.5% sellado" como exhaustividad y el numero se vuelve maquillaje involuntario.
- **Ruido / no-UE:** sin CNAE/DIRCE/DGT-CAT analogo, portar el registral a un pais sin registro automotriz publico fabrica un techo sin provenance -> rompe la doctrina anti-fabricacion.

#### (e) Criterio de sellado + verificacion multi-via
1. **Invariantes de vista vivos:** 52 provincias x 2 segmentos, verdicts en set fijo, umbrales 85/50 venta y found>=census desguace [tests l.59-95].
2. **Regression guard del dedup:** nacional venta 60-110% (no el ~165% del bug entity-level) [test l.119-126] — protege la clave canonica COALESCE.
3. **coverage=num/den exacto** con la semantica de redondeo de PG [test l.97-112].
4. **Doctrina declarada (NUEVO):** un documento/flag que marque el MSE-interval como canonico y el registral como contraste, testeado en la superficie API para que no se sirvan como equivalentes.
5. **Port-or-retire per pais:** onboardar un pais incluye decidir si porta el registral (con techo generico) o lo retira; el contrato de test se porta o se omite explicitamente, nunca entra mal-formado.

#### (f) Herramienta NEXT-LEVEL
**Eurostat SBS (NACE G45)** reemplaza el techo DIRCE/DGT-CAT espanol por un conteo de establecimientos registral GENERICO para todo pais UE, eliminando el `RATIO_451_45` y el assert-52 como dependencias ES.
- URL: https://ec.europa.eu/eurostat/web/structural-business-statistics — Lic: **Reutilizacion libre (Decision 2011/833/EU; atribucion)** [VERIFIED NEXT-LEVEL.md:191], EUR0=True.
- **GLEIF LEI Golden Copy** (CC0 1.0, https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy [VERIFIED NEXT-LEVEL.md:175]) da el techo registral cross-border cuando no hay analogo CNAE nacional.
- **in-toto** (atestacion de provenance del build de sello) resuelve la confusion del doble-sistema al emitir un CERTIFICADO no-repudiable que liga {git SHA + content-hashes de inputs} -> {coverage}, declarando criptograficamente CUAL sello (MSE canonico vs registral contraste) salio de que datos. URL: https://github.com/in-toto/in-toto — Lic: **Apache-2.0** [VERIFIED NEXT-LEVEL.md:143], EUR0=True.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 05 — Estimador Fienberg K-listas log-lineal + seleccion BIC

> **Ficha 360**
>
> **Costura** — estimators.py es matematica pura country-invariante [VERIFIED: cero literales ES], PERO el gate confidence='high' exige k_present>=3 (estimators.py:246) — supuesto del ecosistema de fuentes ES — y statsmodels-ausente degrada SILENCIOSAMENTE cada estrato a confidence='none' via fallback (estimators.py:202-213), haciendo que un pais sin la libreria certifique ~0%.
>
> **Fix** — (1) Mantener el nucleo generico pero anadir un dispatcher que enrute k<3/esparso/solapamiento-cero a SparseMSE en lugar de degenerar a observed-only/inf-CI. (2) Aumentar el unico modelo BIC-greedy (estimators.py:217-236) con Bayesian Model Averaging (dga) para que el CI integre la incertidumbre de seleccion-de-modelo; coverage_lower del cuantil 2.5% del posterior. (3) Convertir statsmodels-ausente en gate de CI duro (no fallback 'none' silencioso). (4) Desacoplar 'sellable' de k>=3 fijo: parametrizar K_min por pais.
>
> **Adversarial** — DE/FR/IT/PT delgados -> k_present cae a 2, la rama log-lineal nunca se ejecuta (todo Chapman 'low'); con k=3 y celdas separadas exp(intercepto) explota (separacion perfecta beta0->+inf). no-UE/JP -> statsmodels no converge -> fallback 'none' masivo, pais certifica ~0%. Ruido: listas que comparten mecanismo oculto (espejos de marketplace) violan ortogonalidad; el BIC solo modela interacciones PAR (max 6), la dependencia de orden 3 no entra en la clase de modelos -> N_hat sesgado a la baja y CI estrecho -> sello falso.
>
> **Sellado** — Golden: Petersen N=600 (test 42-47); 3 listas independientes recuperan N=1000 rel 0.03 con CI que abraza la verdad y confidence='high' (66-73); dependencia positiva ensancha sin sesgar (76-90). Multi-via: (1) Rcapture closedpMS.t cross-check tol=0.25; (2) mediana posterior dga == punto log-lineal dentro de tol, coverage_lower del 2.5% de dga vs ci_high Python -> usar el mas conservador; (3) estratos sinteticos N-conocido convergen. Regla dura: jamas sellar sobre n_hat; solo coverage_lower=n_obs/ci_high con ci_high ensanchado por la cota dependence-robust (estimators.py:344-347).
>
> **Herramienta NEXT-LEVEL** — dga (Bayesian Model Averaging para captura-recaptura) — GPL(>=2) — https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127]. Complemento SparseMSE — GPL(>=2) — https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]. Ambos via el bridge Rscript existente (estimators_r.py), CPU, EUR0. Candor: licencias tomadas del registro NEXT-LEVEL.md (CRAN); el doc pide verificar upstream antes de adoptar.

#### (a) Verificacion de code_hints [VERIFIED]
- `_design_and_counts` **[VERIFIED estimators.py:138-157]**: construye `(X, y)` sobre las `2^k-1` celdas observables. `patterns = [p for p in itertools.product((0,1), repeat=k) if any(p)]` (148) EXCLUYE la celda all-zero; `y = freqs.get(p,0)` (150) inyecta ceros estructurales validos para Poisson; columnas = intercepto (151) + k efectos principales `p[j]` (152-153) + interacciones `p[a]*p[b]` (154-155).
- `_fit_poisson` **[VERIFIED estimators.py:160-169]**: `import statsmodels.api as sm` LAZY (163), `sm.GLM(y, X, family=Poisson()).fit(maxiter=200)` (165-166); `except Exception: return None` (168-169) -> dependencia dura silenciosa.
- `loglinear_mse` **[VERIFIED estimators.py:172-262]**: valida empty/longitudes/all-zero-suministrada (187-193); `n_obs=sum(freqs.values())` (194); `lists_present`/`k_present` (195-196); baseline solo-main-effects (199-201); **fallback degenerado** si `res is None` -> `method='loglinear_failed'`, `confidence='none'` (202-213); **BIC greedy** (217-236) SOLO si `select_interactions and k_present>=3`, `candidates=combinations(lists_present,2)`, `while improved and len(chosen)<max_interactions` (=6, 176/220), acepta si `r2.bic_llf < best_bic-1e-6` (230); `m0=exp(intercept)` (240), `n_hat=n_obs+m0` (241), **delta method** `se_n=m0*se_intercept` (243), CI 244-245; `confidence='high' if k_present>=3 else 'low'` (246).
- Tests **[VERIFIED tests/test_exhaustiveness.py:42-90]**: `test_loglinear_two_list_matches_petersen` (42-47, Petersen N=600); `test_loglinear_three_list_recovers_true_n` (66-73, recupera N=1000 rel 0.03, `ci_low<=1000<=ci_high`, `confidence=='high'`); `test_loglinear_positive_dependence_widens_not_biases` (76-90).

#### (b) Mecanismo al atomo
La celda no-observada se predice como `m0 = exp(beta0)` del GLM Poisson ajustado SOLO sobre celdas observadas. Bajo independencia, el log-lineal solo-main-effects es el Petersen/Fienberg clasico: `N_hat = n_obs + exp(intercepto)`. Las interacciones par-a-par anadidas por BIC capturan dependencia entre listas; bajo correlacion POSITIVA inflan `exp(beta0)` -> el CI se ENSANCHA en vez de sesgar N (la doctrina del docstring 11-15). El delta-method es exacto: `d/dbeta0 exp(beta0)=exp(beta0)`, luego `se(m0)=m0*se(beta0)` y la `se` sobre N es identica. `max_interactions=6` y `bic_llf` (penaliza parametros) impiden sobre-ajustar celdas esparsas. La frontera `k_present>=3` para `confidence='high'` (246) es el unico portal a "sellable".

#### (c) Costura ES->generico + fix exacto
El estimador es **country-INVARIANTE** [VERIFIED: cero literales ES en estimators.py]. La costura es INDIRECTA y doble:
1. `confidence='high'` exige `k_present>=3` (estimators.py:246): acopla la sellabilidad a tener >=3 listas ortogonales, supuesto del ecosistema ES (break #3). En DE/FR la mayoria de estratos caen a `k=2` -> nunca alcanzan el log-lineal.
2. `statsmodels` es dependencia de runtime DURA: ausente o sin convergencia -> TODO estrato cae al fallback `confidence='none'` (202-213) -> el pais certifica ~0%.

**Fix:** (i) mantener la matematica generica pero ROUTEAR los estratos `k<3` / esparsos / solapamiento-cero a un estimador sparse-capable (**SparseMSE**) en vez de degenerar; (ii) AUMENTAR el unico modelo BIC-greedy con Bayesian Model Averaging (**dga**) para que el CI integre la incertidumbre de SELECCION-de-modelo en vez de ser condicional a un camino greedy; (iii) convertir `statsmodels`-ausente en un GATE de CI duro, no un fallback silencioso.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT:** ecosistema delgado -> `k_present` colapsa a 2 en casi todo estrato; la rama log-lineal nunca se toma; todo es Chapman 'low'. Donde `k=3` pero celdas esparsas/separadas, `exp(intercepto)` EXPLOTA (separacion perfecta -> `beta0->+inf`) -> `N_hat` enorme (lo atrapa IDENT_CAP, pero como uncertified, no sellado).
- **no-UE/JP:** lo anterior + fallo de convergencia de statsmodels en disenos degenerados -> fallback masivo 'none'.
- **ruido:** dos listas que comparten un mecanismo oculto (espejos de marketplace disfrazados de distintos) violan homogeneidad/ortogonalidad; el BIC solo modela interacciones PAR (max 6) -> dependencia de orden 3 (sesgo de fuente compartido por 3 listas) NO entra en la clase de modelos -> `N_hat` sesgado a la baja, CI demasiado estrecho -> SELLO FALSO.

#### (e) Criterio de sellado + verificacion multi-via
- **Golden:** Petersen 2-listas = 600 (test 42-47); 3 listas independientes recuperan N=1000 dentro de rel 0.03 con CI que abraza la verdad (66-73); dependencia positiva ENSANCHA sin sesgar (76-90).
- **Multi-via:** (1) R `Rcapture::closedpMS.t` cross-check dentro de `tol=0.25` (estimators_r.crosscheck, ya existe); (2) la mediana del posterior **dga** debe coincidir con el punto log-lineal dentro de tol, y `coverage_lower` derivado del cuantil 2.5% de dga vs `ci_high` Python -> el sello usa el MAS conservador; (3) estratos sinteticos con N conocido: el estimador converge.
- **Regla dura:** jamas sellar sobre `n_hat`; solo `coverage_lower = n_obs/ci_high` (estimators.py:66-71), donde `ci_high` ya viene ensanchado por la cota dependence-robust (estimators.py:344-347).

#### (f) Herramienta NEXT-LEVEL
**dga — Capture-Recapture Estimation using Bayesian Model Averaging** · GPL(>=2) · https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127,135]. Eleva el sello de "depende de UN modelo elegido por BIC" a un POSTERIOR de N que integra la incertidumbre de seleccion-de-modelo; `coverage_lower` se toma del cuantil 2.5% del posterior promediado. Nivel inalcanzable: ningun humano integra sobre el espacio completo de estructuras de dependencia y lo propaga a un intervalo nacional estratificado cada build; es el estimador courtroom-grade de HRDAG (Johndrow/Lum/Ball). Corre por el bridge Rscript existente (estimators_r.py), CPU, EUR0, degrada graceful. Complemento: **SparseMSE** (GPL>=2, https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]) para los estratos de solapamiento-cero. Candor: la licencia GPL(>=2) viene del entry de NEXT-LEVEL.md (CRAN); el doc mismo pide "verificar cada URL/licencia a fuente antes de adoptar" — no la re-verifique upstream en esta sesion.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 06 — Hacer VINCULANTE el ancla censal (gate no implementado)

> **Ficha 360**
>
> **Costura** — load_external_census YA es parametrica por country_code (triangulation.py:36-50, paths.py:50-52) pero compute() nunca enhebra country y el ancla solo es nacional (None,None). Mismatch de scope (sealing_hole #5): el ancla (None,None) EXCLUYE 'otros' mientras n_hat_sum (seal.py:96) SUMA estratos identificados INCLUYENDO seg='otros' (capture.py:111) -> ratio nacional sobre scopes desalineados. Ademas _seal_one (seal.py:39-47) IGNORA external_ref; el censo solo se persiste (seal.py:179,195), nunca veta.
>
> **Fix** — (1) Implementar inyeccion known-margin: log(n_external) como offset Poisson / total marginal fijo en _design_and_counts/_fit_poisson (estimators.py:160-262) via bridge dga/SparseMSE, fijando N en estratos que hoy fallan IDENT_CAP -> mueve masa uncertified->certified. (2) Gatear sealed en coverage_lower>=0.95 AND verdict==consistent. (3) Alinear scopes: excluir 'otros' de n_hat_sum al triangular o anadir fila censal comparable. (4) Etiquetar n_external [MEDIDO]/[ESTIMADO DECLARADO]; solo [MEDIDO] puede PIN (vinculante), [ESTIMADO] solo contrasta.
>
> **Adversarial** — Justo un pais nuevo con 2-3 listas ruidosas puede ser internamente consistente pero sesgado y declarar SELLADO sobre un denominador que el censo rechazaria (sealing_hole #1). DE/FR/IT/PT no tienen DIRCE/DGT cableado -> el gate vinculante debe aceptar Eurostat SBS / GLEIF. no-UE puede no tener ancla -> degradar a advisory sin bloquear onboarding. Inyectar mal el margen ([ESTIMADO] tomado como [MEDIDO]) propaga el sesgo del ancla al N pineado.
>
> **Sellado** — ES golden: pinear con DIRCE MANTIENE sellados los ya sellados y SOLO ANADE nuevos-identificados (monotonia, cero regresion); ratio N_hat/n_external en 0.7-1.4 por construccion. Multi-via: (1) DOS anclas independientes (DIRCE + GLEIF/Eurostat) aterrizan el mismo N_hat; el desacuerdo es distrust, no se promedia; (2) alterar UNA fila del censo voltea el gate (test mecanico); (3) provenance [MEDIDO]/[ESTIMADO] impuesto por el contrato de 8 tests (test_exhaustiveness_triangulation_loaded.py).
>
> **Herramienta NEXT-LEVEL** — dga / SparseMSE inyeccion de margen-conocido via bridge R — GPL(>=2) — https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:135]. Panel de anclas: Eurostat SBS (Reutilizacion libre, Decision 2011/833/EU) [VERIFIED NEXT-LEVEL.md:191] + GLEIF LEI Golden Copy (CC0 1.0) [VERIFIED NEXT-LEVEL.md:175]. Certificado no-repudiable: in-toto (Apache-2.0, https://github.com/in-toto/in-toto) [VERIFIED NEXT-LEVEL.md:143].

#### (a) Verificacion de code_hints [VERIFIED]
- `_seal_one` **[VERIFIED seal.py:39-47]**: `e = est.estimate_stratum(freqs)` (40); `cov_lower = e.coverage_lower` (41); `sealed = e.identified and math.isfinite(cov_lower) and cov_lower >= threshold` (42-46). **`external_ref` / censo NO se referencian** -> el sello es pura auto-consistencia interna.
- `compute` **[VERIFIED seal.py:68-69,144-148,179,195]**: el censo se carga (`external_census = triangulation.load_external_census()` 68-69) pero SOLO se usa para (i) persistir `ext_ref` (`external_census.get((s.province_code,s.segment))` 179; columna `external_ref` 195) y (ii) el REPORTE nacional `triangulation.triangulate(n_hat_sum, external_census.get((None,None)))` (146-148). NUNCA alimenta `estimate_stratum` ni la decision `sealed`.
- `triangulate` **[VERIFIED triangulation.py:66-81]**: devuelve `verdict` consistent/n_hat_high/n_hat_low/no_anchor — ADVISORY, no gate.
- Punto de inyeccion del margen-conocido **[VERIFIED estimators.py:160-262]**: `_design_and_counts`/`_fit_poisson` es donde entraria un offset Poisson `log(n_external)` o una celda-marginal fija.

#### (b) Mecanismo al atomo
Hoy el sello es internamente auto-consistente: `coverage_lower = n_obs/ci_high >= 0.95` con `ci_high` del log-lineal ensanchado por la cota dependence-robust. El censo externo solo puede DESCRIBIR (el `verdict` en el dict de summary) — no puede VETAR ni PIN-ear. Dos rutas NO construidas: **(a) gate duro**: negar el sello si `n_obs < threshold*n_external` o si `verdict != consistent`; **(b) inyeccion known-margin**: alimentar `log(n_external)` como offset Poisson / total marginal fijo en el ajuste Fienberg, de modo que estratos que hoy fallan IDENT_CAP obtengan N fijado por un mecanismo INDEPENDIENTE (registro/fiscal), trasladando masa uncertified->certified SIN inventar dato.

#### (c) Costura ES->generico + fix exacto
La carga ya es parametrica por pais: `load_external_census(country_code=DEFAULT_COUNTRY)` con `census_dir(cc)` **[VERIFIED triangulation.py:36-50, paths.py:50-52]** — pero `compute()` nunca enhebra `country` y el ancla solo es nacional `(None,None)`. **Mismatch de scope (sealing_hole #5):** el ancla `(None,None)` EXCLUYE el segmento 'otros', pero `n_hat_sum` (seal.py:96) suma TODOS los estratos identificados INCLUYENDO `seg='otros'` (capture.py:111 `segment_for(kind) if kind else "otros"`) -> la ratio nacional se computa sobre scopes desalineados.

**Fix:** (1) implementar la inyeccion known-margin via bridge dga/SparseMSE usando el `n_external` por-estrato; (2) GATEAR el sello en census-consistency (`coverage_lower>=0.95 AND verdict==consistent`); (3) ALINEAR scopes: o excluir 'otros' de `n_hat_sum` al comparar con el ancla, o exigir que el censo lleve una fila nacional comparable a 'otros'; (4) ETIQUETAR cada `n_external` [MEDIDO] vs [ESTIMADO DECLARADO] y permitir PIN (vinculante) solo a anclas [MEDIDO]; las [ESTIMADO] solo contrastan (advisory) — para que un estimado declarado JAMAS se propague como margen medido.

#### (d) Riesgo adversarial concreto
Es PRECISAMENTE en un pais nuevo con 2-3 listas ruidosas donde el MSE puede ser internamente consistente pero muy sesgado y declarar SELLADO sobre un denominador que el censo rechazaria (sealing_hole #1). **DE/FR/IT/PT:** no hay analogo DIRCE/DGT cableado; el gate vinculante debe aceptar otra ancla (Eurostat SBS NACE G45.1, GLEIF/LEI). **no-UE:** el ancla puede no existir -> debe degradar a advisory, nunca bloquear onboarding. **Ruido:** inyectar mal el margen (un [ESTIMADO DECLARADO] tomado como [MEDIDO]) propaga el sesgo del ancla al N pineado -> el sello certifica el error del censo.

#### (e) Criterio de sellado + verificacion multi-via
- **Sobre ES (golden monotonia):** fijar con DIRCE debe MANTENER sellados los estratos ya sellados y SOLO ANADIR los nuevos-identificados (cero regresion). La ratio `N_hat/n_external` debe quedar en 0.7-1.4 por construccion.
- **Adversarial:** golden de que las transiciones uncertified->certified son census-driven, no threshold-gamed.
- **Multi-via:** (1) DOS anclas independientes (DIRCE + GLEIF/Eurostat) deben aterrizar el mismo N_hat nacional; el DESACUERDO entre anclas es senal de distrust, no se promedia; (2) alterar UNA fila del censo debe voltear el gate (test mecanico); (3) provenance [MEDIDO]/[ESTIMADO] impuesto por el contrato de 8 tests ya existente (test_exhaustiveness_triangulation_loaded.py).

#### (f) Herramienta NEXT-LEVEL
**dga / SparseMSE — inyeccion de margen-conocido via el bridge R existente** · GPL(>=2) · https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:135]. Es el next_level #1 del diseno 07 (poblacion-con-margen-conocido) que convierte masa uncertified en certified sin inventar dato. PANEL de anclas vinculantes multi-mecanismo: **Eurostat SBS** (NACE G45 venta/reparacion) · Reutilizacion libre (Decision 2011/833/EU) [VERIFIED NEXT-LEVEL.md:22,191] y **GLEIF LEI Golden Copy** · CC0 1.0 [VERIFIED NEXT-LEVEL.md:20,175] dan ancla registral dia-uno a CUALQUIER pais. Para hacer el sello vinculante un CERTIFICADO no-repudiable: **in-toto** · Apache-2.0 · https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:143]. Candor: licencias dga/SparseMSE del registro CRAN en NEXT-LEVEL.md (verificar upstream); CC0 de GLEIF y Decision 2011/833 de Eurostat son licencias publicas conocidas.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 07 — Mapeo source_key->bucket (membresia por pais, data-driven)

> **Ficha 360**
>
> **Costura** — La resolucion source_key->bucket es 100% Python en build-time (bucket_for, lists.py:65-74), con default fail-OPEN a MKT (lists.py:74) y heuristicas ES: '"oficial" in source_key' (palabra espanola) y startswith('mercedes') (una marca). discovery_list (0048:22-28) tiene orthogonality_class pero NO source_key NI country_code; el seed (capture.py:120-134) escribe la taxonomia Python en la DB cada build en vez de leerla de filas de pais. Las fuentes de otro pais caen a MKT -> excluidas de read_patterns (capture.py:203-204) en silencio.
>
> **Fix** — (1) Anadir discovery_list_membership(country_code char(2), source_key text, orthogonality_class text, PK(country_code,source_key)) o extender discovery_list con source_key+country_code; sembrar con _EXACT como filas SOLO-ES. (2) bucket_for pasa a lookup DB por (country_code, source_key) con el dict Python como fallback puro-ES. (3) CRITICO: cambiar fail-OPEN->MKT por fail-CLOSED: source_key no mapeado en un pack RAISE/falla el build via gate Great Expectations. (4) Verificar cada clase ortogonal con >=1 fuente real por pais (>=3 por estrato ideal).
>
> **Adversarial** — DE: mobile.de/autohaus/kba caen a MKT -> la lista registral KBA nunca entra al MSE, nada sella. FR: 'officiel' (frances) != 'oficial' (espanol) -> heuristica OEM falla; diacriticos rompen el match. IT/PT/JP/no-UE: claves en locale/kanji nunca casan _EXACT. Ruido (mis-promocion): un marketplace con 'oficial' en la clave (coches_oficial_mkt) es ASCENDIDO a OEM -> inyecta lista no-ortogonal -> N sesgado. El fail-open es el peor por SILENCIOSO: la lista mas fuerte del pais desaparece sin error y coverage_lower sub-cuenta.
>
> **Sellado** — Contrato pre-sello (Great Expectations): inyectar un source_key foraneo no mapeado => la expectativa FALLA el build (fail-closed mecanico, espejo COUNTRY-PROOF); baseline ES byte-identica; suite versionada por country pack. Multi-via: (1) conteo UNMAPPED del guard Pydantic CountryPack == conteo del _gap_report SQL --dry-run sobre la misma DB; (2) cada clase ortogonal con >=1 fila de fuente por pais activo (test); (3) source_key duplicado entre dos packs -> guard de disjuntez (CROSS-PACK) lo bloquea.
>
> **Herramienta NEXT-LEVEL** — Great Expectations (validacion de datos como contratos bloqueantes) — Apache-2.0 — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Complementos: Pydantic (MIT, https://github.com/pydantic/pydantic) [VERIFIED NEXT-LEVEL.md:587] guard tipado CountryPack; GLEIF LEI Golden Copy (CC0 1.0) [VERIFIED NEXT-LEVEL.md:175] lista REG dia-uno por pais. Alternativas: Pandera, Soda Core, dbt tests.

#### (a) Verificacion de code_hints [VERIFIED]
- `_EXACT` **[VERIFIED lists.py:27-45]**: dict de source_keys ES -> bucket: `osm/overture/geo_sweep->GEO`, `autocasion_census->CENSUS`, `dgt_cat->DGT`, `aedra/aecs/acevas->ASSOC`, `dork_municipal->DORK`, `borme_cnae->REG`, `graph_recursive->GRAPH`, `collapse_invisible->COLLAPSE`.
- `bucket_for` **[VERIFIED lists.py:65-74]**: lookup exacto primero (67-68); luego heuristicas de prefijo `startswith("oem_") or startswith("mercedes")->OEM` (69-70); `"oficial" in source_key or endswith("_new_stock")->OEM` (71-72); **`return "MKT"` por defecto (74)** = FAIL-OPEN: todo source_key no reconocido cae SILENCIOSAMENTE a MKT, que el MSE excluye por defecto.
- `discovery_list` **[VERIFIED migrations/0048_discovery_capture.sql:22-28]**: columnas `list_key (PK)`, `orthogonality_class`, `description`, `is_orthogonal`, `created_at`. Tiene `orthogonality_class` pero **NO `source_key` y NO `country_code`** -> no hay tabla de membresia por-fuente.
- `build` **[VERIFIED capture.py:109-134]**: `bucket = bucket_for(source_key)` se llama en build-time (110); `discovery_capture` guarda el BUCKET resuelto (`list_key`), no el source_key; el seed de `discovery_list` (120-134) escribe la TAXONOMIA desde el dict Python `LIST_METADATA` cada build (`INSERT...ON CONFLICT DO UPDATE`), NO la lee de filas de pais.
- `read_patterns` **[VERIFIED capture.py:203-204]**: `if list_key not in idx: continue` -> las capturas de un bucket fuera de los ortogonales (MKT cuando include_mkt=False) se PIERDEN.

#### (b) Mecanismo al atomo
La resolucion source_key->bucket es 100% Python en build-time (`capture.build` -> `bucket_for`). El `discovery_list` de la DB es un espejo derivado de los 10 buckets Python, re-sembrado cada build, NUNCA la fuente de verdad. NO existe tabla de membresia por-fuente. Un source_key que no esta en `_EXACT` ni casa las 4 reglas de prefijo -> MKT -> excluido -> sus capturas nunca entran a `read_patterns` -> ese mecanismo es INVISIBLE al MSE, bajando K y `coverage_lower` en silencio.

#### (c) Costura ES->generico + fix exacto
El default fail-open y las heuristicas ES son la costura: `"oficial"` es la palabra espanola; `startswith("mercedes")` es UNA marca; las claves `_EXACT` son todas fuentes ES. Las fuentes de un pais nuevo caen a MKT por defecto (break #3, silencioso).

**Fix:** (1) anadir `discovery_list_membership(country_code char(2), source_key text, orthogonality_class text, PRIMARY KEY(country_code, source_key))` — o extender `discovery_list` con `source_key+country_code`; sembrarla con el dict ES `_EXACT` como filas SOLO-ES; (2) `bucket_for` pasa a lookup en DB por `(country_code, source_key)` con el dict Python como fallback PURO-ES; (3) **CRITICO:** cambiar el default de fail-OPEN (->MKT, silencioso) a fail-CLOSED — un source_key no mapeado en un country pack debe RAISE / fallar el build (gate Great Expectations pre-sello), jamas tirar en silencio la lista mas fuerte del pais; (4) verificar que cada clase ortogonal tiene >=1 fuente real por pais (idealmente >=3 por estrato).

#### (d) Riesgo adversarial concreto
- **DE:** `mobile.de`/`autohaus`/`kba` (registro) caen a MKT -> la lista registral KBA de DE nunca entra al MSE, K baja, nada sella.
- **FR:** `lacentrale`/`argus`; **`officiel` (frances) != `oficial` (espanol)** -> la heuristica OEM falla; diacriticos rompen el match.
- **IT/PT/JP/no-UE:** identico; claves en kanji/locale nunca casan `_EXACT`.
- **Ruido (el peor, mis-promocion):** un marketplace cuya clave contiene 'oficial' (p.ej. `coches_oficial_mkt`) es ASCENDIDO a OEM -> inyecta una lista NO-ortogonal al MSE -> N sesgado. El fail-open es el mas peligroso porque es SILENCIOSO: la lista registral mas fuerte del pais desaparece sin error y `coverage_lower` sub-cuenta.

#### (e) Criterio de sellado + verificacion multi-via
- **Contrato pre-sello (Great Expectations):** inyectar un source_key foraneo NO presente en el mapa de buckets => la expectativa FALLA el build (prueba mecanica de fail-closed, espejo del invariante COUNTRY-PROOF). La baseline ES pasa byte-identica. Suite versionada por country pack (additive).
- **Multi-via:** (1) el conteo UNMAPPED del guard tipado Pydantic (CountryPack) == el conteo del `_gap_report` SQL `--dry-run` sobre la misma DB; (2) cada clase ortogonal tiene >=1 fila de fuente por pais activo (test); (3) adversarial: source_key duplicado entre dos packs -> el guard de disjuntez (espejo sealing_hole CROSS-PACK) lo bloquea.

#### (f) Herramienta NEXT-LEVEL
**Great Expectations — validacion de datos / expectations como unit tests del dato** · Apache-2.0 · https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Codifica las precondiciones estadisticas OCULTAS del sello (ningun source_key cae en silencio a MKT, cada clase ortogonal poblada, vocabulario del censo casa los segmentos) como contratos EJECUTABLES, versionados y BLOQUEANTES. La revision manual jamas atrapa el fail-open; la maquina si. Alternativas: Pandera, Soda Core, dbt tests. Complementos: **Pydantic** (MIT, https://github.com/pydantic/pydantic [VERIFIED NEXT-LEVEL.md:587]) como guard tipado CountryPack en CI; **GLEIF LEI Golden Copy** (CC0 1.0 [VERIFIED NEXT-LEVEL.md:175]) para dar a cada pais una lista REG dia-uno a la que apuntar el mapa data-driven. Candor: Apache-2.0/MIT son licencias conocidas de estos proyectos y estan tal cual en NEXT-LEVEL.md; CC0 de GLEIF idem.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 08 — Calibracion de constantes de politica + gate de evidencia insuficiente

> **Ficha 360**
>
> **Costura** — Tres escalares de politica ES son literales de modulo sin dimension de pais: DEFAULT_THRESHOLD=0.95 (seal.py:27), IDENT_CAP=5.0 (estimators.py:304), banda 0.7-1.4 (triangulation.py:75-80). Estan presentados como universales pero calibrados al ecosistema ES. Ademas el gate 'evidencia insuficiente' NO existe [VERIFIED por ausencia]: estimate_stratum devuelve confidence 'none'/'low' e identified=False (estimators.py:362-373,316-317) y el roll-up solo parte identified/unidentified (seal.py:91-95); un pais que sella ~0% por datos delgados es indistinguible de uno genuinamente 0% cubierto.
>
> **Fix** — (1) Mover las 3 constantes a un objeto CountryPolicy(seal_threshold, ident_cap, triangulation_band) con los valores ES como fila del pack ES y default documentado. (2) Calibrar cada una contra calidad de datos local MEDIBLE (ident_cap de la distribucion n_hat/n_obs; banda de la dispersion de provenance), no a ojo. (3) Construir el gate honesto: estrato/pais con <K_min listas ortogonales o >X% de estratos fallando IDENT_CAP emite status='insufficient_evidence' (distinto de sealed=False a 0%). (4) Acoplar al selector de listas VoI para que el gate sea accionable.
>
> **Adversarial** — DE/FR/IT/PT delgados: la mayoria de estratos fallan IDENT_CAP=5.0 -> roll-up certifica ~0% y 0.95 inalcanzable SIN senal de recalibracion (break #9); un regulador no distingue 'fallamos' de 'no hay dealers'. no-UE: banda 0.7-1.4 calibrada al dedup ES puede ser erronea donde el resolver deja mas duplicados. Ruido: calibrar a ojo por pais reintroduce subjetividad; el gate debe justificarse contra un estadistico medible o se vuelve perilla para fabricar sellos.
>
> **Sellado** — Un pais delgado debe aflorar insufficient_evidence, NO sealed=False. Tests: (1) pais sintetico todo-estrato-k<3 -> gate emite insufficient_evidence, nunca sello 0%; (2) SparseMSE recupera intervalo finito donde Python da inf-CI en solapamiento-cero, asi un pais delgado-pero-cubierto aun sella (lo distingue de vacio); (3) cross-check SparseMSE vs log-lineal en estratos con solapamiento dentro de tol=0.25 (estimators_r.py:175-193); (4) constantes recalibradas mantienen el ES golden byte-identico (cero regresion).
>
> **Herramienta NEXT-LEVEL** — SparseMSE (MSE para datos de captura esparsos) — GPL(>=2) — https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]. Complementos: Great Expectations/Pandera como gate de evidencia pre-sello (Apache-2.0) [VERIFIED NEXT-LEVEL.md:167]; NannyML (Apache-2.0, https://github.com/NannyML/nannyml) [VERIFIED NEXT-LEVEL.md:611] para recalibracion sin-etiquetas. Candor: NannyML es el encaje mas debil (disenado para confianza de clasificador); primario SparseMSE + gate Great Expectations.

#### (a) Verificacion de code_hints [VERIFIED]
- `DEFAULT_THRESHOLD = 0.95` **[VERIFIED seal.py:27]** — barra del sello sobre `coverage_lower`.
- `IDENT_CAP = 5.0` **[VERIFIED estimators.py:304]** con `_mark_identified` (307-318): `identified=False` si `n_obs<=0 or not isfinite(ci_high)` (309-310) o `n_hat>cap or ci_high>cap` (311-313); degrada `'high'->'low'` si no identificado (316-317). El cap = `5.0*n_obs` <=> piso de cobertura implicito >= 20%.
- banda `0.7-1.4` **[VERIFIED triangulation.py:75-80]**: `ratio>1.4->n_hat_high`, `ratio<0.7->n_hat_low`, else `consistent`.
- **El gate "evidencia insuficiente" NO existe [VERIFIED por ausencia]**: `estimate_stratum` devuelve `confidence 'none'/'low'` e `identified=False` para estratos delgados (estimators.py:362-373, 316-317); el roll-up (seal.py:91-95) solo parte identified/unidentified y certifica la suma identified. Un pais que sella ~0% por fuentes delgadas es INDISTINGUIBLE de uno genuinamente 0% cubierto — NINGUNA senal se emite.

#### (b) Mecanismo al atomo
Tres escalares gobiernan TODO el veredicto: `threshold=0.95` (barra del sello), `IDENT_CAP=5.0` (corte de identificabilidad: `N_hat<=5*n_obs` <=> piso de cobertura >=20%), banda `0.7-1.4` (tolerancia de triangulacion). Los tres se presentan como universales pero son POLITICA ES calibrada al ecosistema de datos ES. No hay calibracion por-pais ni meta-senal que diga "tienes <3 listas ortogonales / datos demasiado delgados -> no intentes certificar, adquiere mas listas".

#### (c) Costura ES->generico + fix exacto
Las tres constantes son literales de modulo SIN dimension de pais [VERIFIED seal.py:27, estimators.py:304, triangulation.py:75-80].

**Fix:** (1) mover las tres a un objeto `CountryPolicy(seal_threshold, ident_cap, triangulation_band)` con los valores ES como la fila del pack ES y un default documentado; (2) CALIBRAR cada una contra calidad de datos local MEDIBLE (ident_cap de la distribucion observada `n_hat/n_obs`; banda de la dispersion de provenance de anclas) — NO a ojo, para no reintroducir subjetividad; (3) construir el GATE HONESTO: un estrato/pais con `< K_min` listas ortogonales o con `> X%` de estratos fallando IDENT_CAP emite `status='insufficient_evidence'` (distinto de `sealed=False` a 0%), diciendo al operador "adquiere mas listas" en vez de certificar ~0% en silencio; (4) acoplar al selector de listas activo (VoI) para que el gate sea accionable.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT delgados:** la mayoria de estratos fallan IDENT_CAP=5.0 -> el roll-up honesto certifica ~0% y 0.95 es inalcanzable, SIN senal de que CAP/threshold/banda necesitan recalibracion (break #9). Un regulador que lee "0% sellado" no distingue "fallamos" de "el pais no tiene puntos de venta".
- **no-UE:** la banda 0.7-1.4 calibrada a la calidad de dedup ES puede ser erronea donde el resolver deja mas duplicados (ratio sesgada).
- **Ruido:** calibrar a ojo por pais reintroduce subjetividad -> el gate debe justificarse contra un estadistico de calidad MEDIBLE, o se vuelve una perilla para fabricar sellos.

#### (e) Criterio de sellado + verificacion multi-via
- Un pais con datos delgados debe AFLORAR `insufficient_evidence`, NO `sealed=False`.
- **Tests:** (1) pais sintetico de datos delgados (todo estrato k<3) -> el gate emite `insufficient_evidence`, nunca un sello 0%; (2) **SparseMSE** recupera un intervalo FINITO donde el Python da inf-CI en estratos de solapamiento-cero, asi un pais delgado-pero-genuinamente-cubierto AUN puede sellar (distinguiendolo de vacio); (3) cross-check SparseMSE vs log-lineal en estratos CON solapamiento dentro de `tol=0.25` (gate de distrust ya existe estimators_r.py:175-193); (4) constantes recalibradas deben mantener el ES golden BYTE-identico (cero regresion).

#### (f) Herramienta NEXT-LEVEL
**SparseMSE — Multiple Systems Estimation for Sparse Capture Data** · GPL(>=2) · https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]. Maneja la no-existencia del MLE, parametros en -inf y la no-identificabilidad — recuperando un intervalo finito EXACTAMENTE donde el log-lineal Python degenera a observed-only/inf-CI; es lo que hace SELLABLE un ecosistema mas delgado que ES y permite al gate distinguir "delgado pero cubierto" de "genuinamente vacio". Corre bajo el bridge Rscript existente (estimators_r.py:86-129), CPU, EUR0, degrada graceful. Complementos: el gate de evidencia como contrato pre-sello **Great Expectations/Pandera** (Apache-2.0 [VERIFIED NEXT-LEVEL.md:167]) (>=3 listas ortogonales por estrato o rehusa); **NannyML** (Apache-2.0, https://github.com/NannyML/nannyml [VERIFIED NEXT-LEVEL.md:611]) para recalibracion sin-etiquetas de umbrales si el sello se trata como score monitorizado. **Candor honesto:** NannyML es el encaje MAS DEBIL de los tres (disenado para confianza de clasificador, no para constantes de captura-recaptura); la palanca primaria es SparseMSE + el gate Great Expectations. Licencias del registro NEXT-LEVEL.md (CRAN/repos), verificar upstream antes de adoptar.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 09 — Cota dependence-robust de identificacion parcial

> **Ficha 360**
>
> **Costura** — estimators.py:268-292 es country-invariante (cero literal ES); la costura es estadistica: dependence_robust_bound solo se ejecuta para k_present>=3 (estimators.py:342) y su clase-de-modelos enumera SOLO interacciones par individuales (estimators.py:281-282), calibrada al ecosistema ES donde la dependencia de orden superior es rara. En paises de fuentes delgadas la cota o no corre (K<3) o es estructuralmente demasiado estrecha.
>
> **Fix** — Para ES no se toca byte (sin literal de pais). Endurecimiento generico: (1) extender candidate_models a interacciones de orden>2 O sustituir el max-sobre-pares por una cota superior derivada de un posterior model-averaged (dga) tomando el cuantil 2.5% como la figura que gobierna coverage_lower; punto de integracion estimators.py:345. (2) Para estratos de solapamiento-cero, enrutar a SparseMSE (intervalo finito donde hoy hay inf-CI). (3) Property-test de widen-monotonia para garantizar que el techo nunca estrecha ci_high.
>
> **Adversarial** — DE/FR: 3 listas que comparten sesgo geografico de fuente no modelado producen dependencia de orden-3 que NO entra en el max (solo pares) -> techo subestima N -> coverage_lower inflado -> sello falso. IT/PT: celdas esparsas hacen _fit_poisson devolver None (estimators.py:287-288) y el max colapsa al modelo de independencia. No-UE/ruido: marketplaces espejo disfrazados de listas ortogonales no los detecta la banda (ortogonalidad asumida en lists.py, no testeada).
>
> **Sellado** — (1) unit existente low==n_obs & high>=0.9N [test_exhaustiveness.py:96-101]. (2) property widen-monotonia ci_high post-robust>=loglinear. (3) 2a via: cross-check vs cuantil 2.5% del posterior dga (BMA) dentro de tol. (4) via adversarial: estrato sintetico con dependencia orden-superior conocida donde el techo-solo-pares subestima N -> el sello NO debe certificar. Sellar solo cuando el techo abarca N a traves de la clase de dependencia.
>
> **Herramienta NEXT-LEVEL** — dga: Capture-Recapture Estimation using Bayesian Model Averaging (GPL >=2) [VERIFIED NEXT-LEVEL.md:127] https://cran.r-project.org/package=dga — integra TODAS las estructuras de interaccion; el sello toma el cuantil 2.5% del posterior promediado, metiendo la incertidumbre de seleccion-de-modelo en el intervalo. Complemento: SparseMSE (GPL >=2) [VERIFIED NEXT-LEVEL.md:119] https://cran.r-project.org/package=SparseMSE para solapamiento-cero. Ambos via bridge Rscript existente (estimators_r.py), CPU, €0.

#### (a) Verificacion de code_hints [VERIFIED]
- `dependence_robust_bound(freqs)` existe y hace EXACTAMENTE lo descrito [VERIFIED pipeline/exhaustiveness/estimators.py:268-292]:
  - `n_obs = int(sum(freqs.values()))` [:277]; `k = len(next(iter(freqs)))` [:278]; `lists_present = [j for j in range(k) if any(p[j] for p in freqs)]` [:279].
  - clase de modelos: `candidate_models = [[]]` (independencia) y luego `.append([cand])` por CADA par `itertools.combinations(lists_present, 2)` [:280-282] — UNA interaccion par a la vez.
  - `highs = [n_obs]` [:283]; por modelo: `_design_and_counts` -> `_fit_poisson`; si `res is None` se SALTA [:287-288]; `m0 = exp(params[0])`, `se = exp(params[0])*sqrt(cov_params[0,0])`, `highs.append(n_obs + m0 + 1.96*se)` [:289-291]; `return float(n_obs), float(max(highs))` [:292].
- Integracion en `estimate_stratum` SOLO para `k_present>=3` [VERIFIED estimators.py:342-350]: `est = loglinear_mse(freqs)` [:343]; `_, robust_high = dependence_robust_bound(freqs)` [:345]; `if robust_high > est.ci_high: est.ci_high = robust_high` [:346-347] — WIDEN-ONLY, nunca estrecha; `return _mark_identified(est)` [:350].
- Cadena al sello [VERIFIED estimators.py:65-71]: `coverage_lower = n_obs / ci_high`; el robust_high al subir `ci_high` solo puede BAJAR coverage_lower -> es el denominador anti-maquillaje real.
- Test [VERIFIED tests/test_exhaustiveness.py:96-101]: `test_dependence_robust_bound` con `_independent_cells(1000,(0.3,0.4,0.5))`; `assert low == n_obs`; `assert high >= 1000*0.9`.

#### (b) Mecanismo al atomo
Es un intervalo de IDENTIFICACION PARCIAL (no un IC frecuentista): suelo = `n_obs` (tienes con certeza lo que viste); techo = `max` sobre la clase {independiente, cada interaccion par individual} del extremo superior Fienberg `n_obs + m0 + 1.96*se`. La dependencia positiva entre listas infla `exp(intercept)=m0`, luego N; tomar el `max` sobre estructuras de dependencia plausibles produce un techo conservador. Ese techo se inyecta en `ci_high` (widen-only) para que el sello (`coverage_lower=n_obs/ci_high`) JAMAS pueda subir falsamente por sub-estimar N bajo listas correlacionadas. Es la valvula que impide sellar sobre un N_hat optimista.

#### (c) Costura ES->generico
El nucleo es matematica PURA y country-invariante: opera sobre un dict abstracto de patrones 0/1, sin un solo literal ES (verificado: no aparece 'ES'/provincia/CNAE en estimators.py). La costura NO es un string horneado sino ESTADISTICA: (1) solo se invoca para `k_present>=3` (en paises de ecosistema delgado casi ningun estrato llega a K>=3, asi que la cota ni se ejecuta); (2) la clase de modelos enumera UNICAMENTE interacciones par individuales [estimators.py:281-282], calibrada implicitamente al ecosistema ES donde la dependencia de orden superior es rara.

#### (d) Riesgo adversarial concreto
- DE/FR: las pocas listas ortogonales transfronterizas (GEO+OEM) comparten un sesgo geografico de fuente NO modelado; un estrato de 3 listas con dependencia de orden-3 comun NO entra en el `max` (solo pares) -> techo subestima N -> coverage_lower inflado -> SELLO FALSO.
- IT/PT (ecosistema fino): idem; ademas con celdas esparsas `_fit_poisson` devuelve None para varios modelos [:287-288] y el `max` se reduce al modelo de independencia, colapsando el techo.
- No-UE/ruido: marketplaces re-etiquetados como listas 'ortogonales' (espejos del mismo mecanismo) -> la cota no lo detecta porque la ortogonalidad se ASUME aguas arriba (lists.py), no se testea aqui.

#### (e) Criterio de sellado + verificacion multi-via
- (1) unit existente: `low==n_obs` y `high>=0.9*N` en datos sinteticos independientes [VERIFIED:96-101].
- (2) widen-monotonia (a anadir): property test `ci_high` post-robust >= `ci_high` log-lineal (nunca estrecha).
- (3) 2a via independiente: cross-check contra el cuantil 2.5% de un posterior BMA (dga) que integra TODAS las estructuras; el `max`-de-pares debe quedar acotado por arriba dentro de tol.
- (4) via adversarial: estrato sintetico con dependencia de orden superior CONOCIDA donde el techo-solo-pares subestima N -> el sello NO debe certificar (hoy puede).
- Sellar solo cuando el techo demostrablemente abarca N a traves de la clase de dependencia.

#### (f) Herramienta NEXT-LEVEL
`dga` (Bayesian Model Averaging) eleva la clase-de-modelos hecha-a-mano a un posterior que INTEGRA todas las estructuras de interaccion; la cota inferior del sello pasa a ser el cuantil 2.5% del posterior promediado -> la incertidumbre de seleccion-de-modelo entra en el intervalo por construccion (estandar HRDAG, recuentos defendibles en tribunales). Complemento `SparseMSE` para los estratos de solapamiento-CERO donde la cota actual degenera a observed-only. Ambos corren por el bridge Rscript ya existente (estimators_r.py).

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 10 — Vectorizacion de patrones de captura (read_patterns)

> **Ficha 360**
>
> **Costura** — capture.py:160-218 sin literal ES directo, pero (1) la clave de estrato es (province_code, segment) sin country_code [capture.py:205,215] -> dos paises colisionan en el mismo estrato (ES '01' == FR '01'); (2) el drop silencioso 'if list_key not in idx: continue' [capture.py:203-204] excluye cualquier fuente que bucket_for mapeo a MKT, y bucket_for falla-en-abierto hacia MKT para claves no reconocidas [lists.py:65-74] -> la fuente fuerte de un pais nuevo desaparece del MSE sin error.
>
> **Fix** — (1) Enhebrar country_code por la firma y el SQL/clave: anadir param country_code, SELECTarlo y key por (country_code, prov, seg) — el enthreading F20 en este punto exacto (capture.py:160-167). (2) Hacer ruidoso el drop: antes de vectorizar, exigir que cada list_key distinto del build mapee a idx O sea una clase no-ortogonal declarada explicitamente; una clave que cae a MKT solo porque bucket_for no la reconocio debe FALLAR el build (contrato Great Expectations), no desvanecerse. (3) Congelar el orden de buckets por build (persistido en diagnostics) para comparabilidad de la serie temporal.
>
> **Adversarial** — DE/FR: colision province_code char(2) (ES '01' == FR '01') si ambos en la tabla sin country_code. Cualquier pais: fuente ortogonal mal-mapeada a MKT por heuristicas ES de bucket_for ('oficial'/'mercedes') se descarta en capture.py:203-204 -> lista mas fuerte desaparece -> coverage_lower sub-cuenta. Ruido: list_key con typo se ignora silenciosamente. Orden: insertar una lista a mitad de orthogonal_buckets desplaza idx y rompe la comparabilidad de la serie de saturacion (F24).
>
> **Sellado** — (1) unit: filas sinteticas -> {patron:freq} esperado, all-zero y MKT excluidos. (2) paridad include_mkt True/False solo difiere en columna MKT. (3) fail-closed: inyectar source_key no-en-idx -> el gate pre-sello FALLA el build (cero-drop-silencioso). (4) aislamiento pais: dos paises en txn revertida no fusionan estratos. (5) linaje: aristas del grafo == filas de discovery_capture (OpenLineage).
>
> **Herramienta NEXT-LEVEL** — Great Expectations (Apache-2.0) [VERIFIED NEXT-LEVEL.md:167] https://github.com/great-expectations/great_expectations — contrato de datos PRE-sello que falla-CERRADO si un source_key cae a MKT en silencio, si los region_code no casan la rejilla del pais, o si una clase ortogonal tiene 0 fuentes; convierte la precondicion oculta de read_patterns en invariante bloqueante (el bug bucket_for-falla-abierto). Complemento: Pandera (schema-como-contrato). CPU puro, €0.

#### (a) Verificacion de code_hints [VERIFIED]
- `read_patterns(build_run_id, *, dsn, include_mkt=False, province_code=None, segment=None)` [VERIFIED pipeline/exhaustiveness/capture.py:160-218].
  - `buckets = orthogonal_buckets(include_mkt)` [:175] -> [VERIFIED lists.py:77-81] devuelve `ORTHOGONAL_LISTS=("GEO","CENSUS","DGT","ASSOC","OEM","DORK","REG")`, +`MKT` si include_mkt.
  - `idx = {b:i for i,b in enumerate(buckets)}` [:176] — mapa bucket->posicion en ORDEN FIJO.
  - SQL: `SELECT resolved_ulid, province_code, segment, list_key FROM discovery_capture WHERE build_run_id=%s` (+filtros opcionales prov/seg) [:188-195].
  - agrupacion: `for resolved_ulid, prov, seg, list_key in rows: if list_key not in idx: continue` [:202-204] — MKT y CUALQUIER list_key no-mapeada EXCLUIDOS; `ukey=(prov,seg,resolved_ulid)`; `by_unit[ukey][2][idx[list_key]] = 1` [:205-208].
  - salida: `pat = tuple(vec); if not any(pat): continue` [:213-214] — celda all-zero EXCLUIDA (es lo que el MSE estima); `out[(prov,seg)][pat] += 1` [:215-217]; `return out, buckets` [:218].

#### (b) Mecanismo al atomo
Una unidad fisica (`resolved_ulid`) dentro de un estrato `(prov,seg)` se convierte en un vector 0/1 sobre el orden fijo de buckets ortogonales; un 1 en la posicion i significa "la lista ortogonal i capturo esta unidad". Las unidades vistas por CERO listas ortogonales se descartan [:213-214] porque la celda all-zero es justo el objetivo de estimacion (lo no-observado). La salida es el dict de frecuencias por estrato `{patron:conteo}` que alimenta `estimate_stratum`. El filtro `if list_key not in idx` [:203-204] ES el filtro de ortogonalidad: MKT (sesgo marketplace) y cualquier clave fuera de las 7 clases quedan fuera del MSE.

#### (c) Costura ES->generico
`read_patterns` no tiene literal ES directo, pero arrastra DOS costuras: (1) la CLAVE de estrato es `(province_code, segment)` [:205,:215] SIN dimension country_code -> filas de dos paises en la misma `discovery_capture` COLISIONAN en el mismo estrato (province char(2) '01'=ES-Alava == FR-Ain '01'). (2) el drop silencioso `if list_key not in idx: continue` [:203-204] elimina cualquier fuente que `bucket_for` mapeo fuera de las 7 clases — y `bucket_for` FALLA-EN-ABIERTO hacia MKT para claves no reconocidas [VERIFIED lists.py:65-74: si no esta en _EXACT ni casa prefijos 'oem_'/'mercedes'/'oficial'/'_new_stock' -> return 'MKT'] -> la fuente de un pais nuevo cae a MKT y se excluye del MSE SIN error.

#### (d) Riesgo adversarial concreto
- DE/FR: colision de estrato por province_code char(2) si ambos paises estan en la tabla sin country_code (depende de F20).
- Cualquier pais: una fuente GENUINAMENTE ortogonal mal-mapeada a MKT por las heuristicas de prefijo ES de bucket_for ('oficial' es palabra espanola, 'mercedes' una marca) se descarta en [:203-204] -> la LISTA MAS FUERTE del pais desaparece en silencio -> coverage_lower sub-cuenta -> un estrato identificado pasa a no-identificado o un sello se cae.
- Ruido: un list_key con typo inserta filas de captura que read_patterns ignora (no in idx) -> infra-captura fantasma.
- Orden: idx depende del orden de orthogonal_buckets; si un pais inserta una lista a mitad del array, el mapa de posiciones se desplaza y los patrones historicos dejan de ser comparables entre builds (rompe la serie de saturacion de F24).

#### (e) Criterio de sellado + verificacion multi-via
- (1) unit: filas sinteticas de discovery_capture -> read_patterns devuelve el `{patron:freq}` esperado, all-zero excluido, MKT excluido cuando include_mkt=False (contrato de la funcion).
- (2) paridad: include_mkt True vs False difieren SOLO por la columna MKT.
- (3) fail-closed (Great Expectations): inyectar un source_key no presente en idx y exigir que el gate pre-sello FALLE el build (prueba mecanica de cero-drop-silencioso) — espejo del invariante COUNTRY-PROOF.
- (4) aislamiento pais: sembrar dos paises en txn revertida y afirmar que sus estratos NO se fusionan (patron test_country_coexistence).
- (5) linaje: nº de aristas del grafo de captura == filas de discovery_capture (OpenLineage).

#### (f) Herramienta NEXT-LEVEL
`Great Expectations` (contrato de datos PRE-sello) corre ANTES de seal.compute y FALLA-CERRADO el build si algun source_key cae en silencio a MKT, si los codigos de region no casan el ancho de la rejilla geo del pais, si una clase ortogonal tiene 0 fuentes reales, o si el filtro all-zero se dispara mal. Convierte la precondicion estadistica oculta de read_patterns en un invariante ejecutable, versionado y bloqueante — es exactamente el bug bucket_for-falla-abierto-hacia-MKT. Complemento: Pandera (mismo rol, mas ligero, schema-como-contrato).

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 11 — Numerador canonico / predicado de punto-de-venta (v_servable_dealer)

> **Ficha 360**
>
> **Costura** — migrations/0056:35-37 hornea literales kind ES ('particular','desguace','garaje') -> un pais con otra taxonomia debe re-codificar el SQL. Ademas la vista tiene CERO consumidores [grep VERIFIED]: stats.py:26, geo.py:51 y el sello (v_province_seal) cada uno lleva su propio predicado inline -> tres scopes divergentes (54.587 / geo-excluye-no-verificados / ~18.298 por cabecera 0056:5-9). Costura doble: taxonomia horneada + hueco de cableado.
>
> **Fix** — (1) Parametrizar el predicado por pais: mover la regla kind->POS-servible a un pack (taxonomy.yaml o tabla seg_map(country,kind,is_sales_point), default-ES) y construir v_servable_dealer desde la tabla en vez de literales inline (misma pack-ificacion que F14). (2) Cablearla como numerador UNICO: reescribir stats.py:26, geo.py:51 y el numerador del sello a COUNT(DISTINCT resolved_cdp_code) FROM v_servable_dealer filtrado por pais -> colapsa tres scopes a uno. (3) Por cambiar una cifra de cara al usuario, gate dry-run -> golden -> Ferrari -> CI antes de exponer.
>
> **Adversarial** — DE/FR/IT/PT: kind literales son enum ES; otra taxonomia -> predicado que sobre-cuenta (no excluye nada) o sub-cuenta (excluye POS validos). No-UE/JP: sin 'desguace' la exclusion es vacua, garaje-con-inventario no mapea. Profundo: mientras vivan tres scopes (stats 54.6k / geo / seal 18.3k) cualquier fraccion de cobertura publicada es atacable por numerador inconsistente. Ruido: kind fuera del enum ES no cae limpio en exclusion ni inclusion.
>
> **Sellado** — (1) paridad: COUNT(DISTINCT resolved_cdp_code) de v_servable_dealer == numerador de stats.py == set paginado de geo.py == numerador del sello. (2) golden: casa cifras verificadas-vivas (directorio ~36.3k, con-inventario ~18.3k, cabecera 0056:17-19). (3) Ferrari/dry-run antes de exponer la cifra publica. (4) aislamiento: conteo ES byte-estable tras parametrizar a pack. (5) gate breaking-change del contrato API.
>
> **Herramienta NEXT-LEVEL** — sraoss/pg_ivm — Incremental View Maintenance (PostgreSQL License) [VERIFIED NEXT-LEVEL.md:764] https://github.com/sraoss/pg_ivm — promueve v_servable_dealer a INCREMENTAL MATERIALIZED VIEW: numerador canonico unico materializado, siempre-fresco (sin REFRESH), leido identico por stats+geo+sello; su verificacion incluye 'IMMV con PK (country_code)' [NEXT-LEVEL.md:767] = aislamiento multi-tenant del numerador. Hace 'numerador==paginado==scope-certificado' un invariante materializado. €0, extension PG.

#### (a) Verificacion de code_hints [VERIFIED]
- La vista existe y hornea kind ES [VERIFIED migrations/0056_v_servable_dealer.sql:26-37]:
  `CREATE OR REPLACE VIEW v_servable_dealer AS SELECT se.entity_ulid, se.cdp_code, se.kind, vdr.resolved_cdp_code, EXISTS(SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid=se.entity_ulid) AS has_inventory FROM servable_entity se JOIN v_dealer_resolved vdr ON vdr.entity_ulid=se.entity_ulid WHERE se.status='active' AND se.kind::text NOT IN ('particular','desguace') AND (se.kind::text <> 'garaje' OR EXISTS(...servable_vehicle...))`. Literales kind ES en [:35-37].
- CERO consumidores [VERIFIED grep v_servable_dealer]: solo aparece en docs/ (generic-engine-bible), plans/ y la propia migracion 0056 — NINGUN modulo en services/ o pipeline/ la lee.
- TRES numeradores divergentes vivos [VERIFIED]:
  - stats.py:26 `WHERE e.kind::text NOT IN ('particular','desguace')` (directorio).
  - geo.py:51 `count(*) FROM entity WHERE kind <> 'particular'` — SCOPE DISTINTO (solo excluye particular, mantiene desguace).
  - numerador del sello = served_canonical via `v_province_seal` (geo.py:113-114).
  - la cabecera de 0056:5-9 documenta los tres scopes: stats=54.587, geo excluye no-verificados, seal ~18.298.

#### (b) Mecanismo al atomo
v_servable_dealer es el "punto de venta de coches" canonico PRETENDIDO: publish-gated (`servable_entity`), `status='active'`, vende coches (`kind NOT IN particular/desguace`), y para `garaje` solo con inventario servible; `resolved_cdp_code` es la identidad dedup a COUNT DISTINCT; `has_inventory` marca punto con stock vivo. La intencion de diseno (cabecera 0056:8-10) es que stats.py, geo.py Y el sello LEAN de aqui para que `count_publico == set_paginado == scope_certificado`. Pero es una VIEW con cero consumidores: las tres superficies siguen con su predicado inline -> coverage=numerador/denominador se computa contra TRES numeradores -> TODA fraccion de cobertura es atacable. Este es el unico nucleo genuinamente sin cerrar de la etapa.

#### (c) Costura ES->generico
Doble costura: (1) el predicado hornea literales kind ES 'particular','desguace','garaje' [:35-37] — un pais con kinds distintos (sin 'desguace' regulatorio, otra ontologia POS) debe RE-CODIFICAR el SQL. (2) aun en ES la vista NO es la verdad en la practica porque nada la consume. Es a la vez costura de taxonomia-horneada Y hueco de cableado.

#### (d) Riesgo adversarial concreto
- DE/FR/IT/PT: 'particular'/'desguace'/'garaje' son valores del ENUM kind ES; un pais con otra taxonomia produce un predicado que o no excluye nada (sobre-cuenta) o excluye POS validos (sub-cuenta) -> numerador mal-scopeado por pais.
- No-UE/JP: sin categoria 'desguace' la exclusion es vacua y la regla garaje-con-inventario puede no mapear.
- El adversarial profundo: mientras vivan tres scopes, un auditor (o competidor) ataca CUALQUIER fraccion publicada senalando el numerador inconsistente — stats dice 54.6k, geo otro numero, seal 18.3k.
- Ruido: un kind fuera del enum ES no cae limpio ni en exclusion ni en inclusion.

#### (e) Criterio de sellado + verificacion multi-via
- (1) paridad: COUNT(DISTINCT resolved_cdp_code) de v_servable_dealer == numerador que sirve stats.py == set paginado de geo.py == numerador del sello (UN numero, tres superficies).
- (2) golden: el conteo cableado casa las cifras verificadas-vivas (directorio ~36.3k, con-inventario ~18.3k segun cabecera 0056:17-19) dentro de tolerancia.
- (3) Ferrari/dry-run ANTES de exponer (cambia una cifra de cara al usuario: "Puntos de venta" publico — unico cambio de la etapa que lo exige).
- (4) aislamiento pais: el conteo ES es byte-estable tras parametrizar el predicado a un pack (re-derivar ES desde taxonomy.yaml -> mismo numero).
- (5) gate de breaking-change sobre el contrato API.

#### (f) Herramienta NEXT-LEVEL
`sraoss/pg_ivm` (Incremental View Maintenance) promueve v_servable_dealer de VIEW plana a INCREMENTAL MATERIALIZED VIEW: el numerador canonico unico queda materializado, siempre-fresco (sin REFRESH, O(delta) en cada INSERT base) y leido identico por stats+geo+sello sub-50ms. Su verificacion incluye EXPLICITAMENTE "Aislamiento pais: IMMV con PK (country_code)" [VERIFIED NEXT-LEVEL.md:767], justo el aislamiento multi-tenant del numerador que F17 necesita. Convierte "numerador==paginado==scope-certificado" en un INVARIANTE materializado en vez de tres queries a mano. (pg_ivm cierra la mitad frescura/consistencia; la mitad parametrizacion-del-predicado-por-pais la complementa el country-pack contract / pycountry, pero la herramienta que ELEVA es pg_ivm.)

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 12 — 100% como intervalo + detector de saturacion

> **Ficha 360**
>
> **Costura** — La serie append-only (0048:55-74) y coverage_lower son country-invariantes, pero: (1) exhaustiveness_estimate NO tiene country_code [0048:58 province_code char(2)] -> una DB multi-pais mezcla series de dos paises en el mismo espacio de build_run_id (depende de F20). (2) el threshold 0.95 que define sealed es politica ES [seal.py:27] -> un pais de fuentes delgadas hace plateau bajo 0.95 y un detector atado al threshold nunca declararia saturacion; la senal correcta es 'la cota inferior dejo de subir', no 'coverage_lower>=0.95'.
>
> **Fix** — (1) Construir el detector: persistir coverage_lower + ancho de IC por build (ya almacenado) y correr un test de change-point/convergencia sobre la serie nacional POR PAIS; declarar saturacion solo cuando la pendiente de la cota inferior se aplana (sin subida > epsilon en k builds sucesivos). (2) Desacoplar 'saturacion' (cota inferior dejo de subir) de 'sellado a 0.95' (threshold) — son afirmaciones distintas. (3) Enhebrar country_code para que cada pais tenga su serie. (4) Acoplar con el selector activo: negar saturacion mientras el VoI de alguna lista candidata > epsilon.
>
> **Adversarial** — Cifras 37.7%/80.5% vienen de recon con stack caido, NO re-ejecutables -> sin inputs hash-pineados (DVC) el 'subio entre builds' es drift disfrazado de medicion. Listas infra-pobladas / 4-de-25 adaptadores -> FALSA saturacion: cota plana por falta de ingestion, no por exhaustion ('no cubierto' indistinguible de 'no observado'). DE/FR: plateau bajo; 'parar>=0.95' nunca dispara, 'parar si plano' dispara pronto. PT/IT/no-UE: mismo confound de inanicion. Ruido: build anomalo (statsmodels no converge -> masa 'none') crea change-point falso.
>
> **Sellado** — (1) serie sintetica monotona-luego-plateau dispara saturacion en el plateau conocido (unit ruptures). (2) niega saturacion mientras el VoI de cualquier lista candidata > epsilon (acopla selector activo). (3) back-test ES: NO declarar saturacion en el 37.7% con listas infra-pobladas [NEXT-LEVEL.md:202]. (4) reproducibilidad: re-correr build_run_id pasado desde inputs hash-pineados -> coverage_lower byte-identico (DVC/in-toto). (5) aislamiento pais de la serie.
>
> **Herramienta NEXT-LEVEL** — ruptures — change-point detection offline (BSD-2-Clause) [VERIFIED NEXT-LEVEL.md:199] https://github.com/deepcharles/ruptures — regla de parada formal sobre la serie de coverage_lower: saturacion solo cuando el change-point muestra que la cota inferior dejo de subir. Complemento: BoTorch (MIT) [VERIFIED NEXT-LEVEL.md:111] https://github.com/pytorch/botorch (VoI=expected information gain; saturacion solo si el VoI marginal de toda lista candidata ~0, no confunde inanicion con exhaustion). Reproducibilidad: DVC (Apache-2.0) [VERIFIED NEXT-LEVEL.md:151] https://github.com/iterative/dvc inputs hash-pineados. CPU, €0.

#### (a) Verificacion de code_hints [VERIFIED]
- Sustrato = serie temporal append-only [VERIFIED migrations/0048_discovery_capture.sql:55-74]: `exhaustiveness_estimate (id bigserial PK, build_run_id text NOT NULL, province_code char(2), segment text, k_lists, n_obs, n_hat, ci_low, ci_high, coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, external_ref, diagnostics jsonb, created_at)`. Cada build inserta un set de filas keyed por build_run_id -> la tabla ES una serie temporal de coverage_lower por estrato a traves de builds.
- coverage_lower nacional [VERIFIED seal.py:107]: `nat_cov_lower = n_obs_cert / nat_ci_high`.
- sello nacional [VERIFIED seal.py:138]: `"sealed": bool(nat_cov_lower >= threshold)`; `DEFAULT_THRESHOLD=0.95` [VERIFIED seal.py:27].
- la figura por estrato [VERIFIED estimators.py:65-71]: `coverage_lower = n_obs/ci_high` (anti-maquillaje).
- composicion SELLADO [VERIFIED seal.py:42-46 estrato: `identified AND isfinite(cov_lower) AND cov_lower>=threshold`; seal.py:78-81 R-crosscheck ADJUNTO a diagnostics (advisory); seal.py:144-148 triangulacion nacional ADJUNTA] — hoy R-agree y triangulacion NO son gates, son advisory.
- El DETECTOR de saturacion (la regla de parada sobre la serie) NO existe en codigo: es design section H / next_level idea #4.

#### (b) Mecanismo al atomo
Exhaustividad NO es un entero: es el intervalo `[coverage_lower, coverage_point] = [n_obs/ci_high, n_obs/n_hat]`. La cota inferior es la figura anti-maquillaje (sobre-estimar N solo puede BAJARLA). A traves de builds, `exhaustiveness_estimate` acumula un coverage_lower por (build_run_id, estrato) -> una serie temporal. La definicion HONESTA de "100% / no queda nada que encontrar" no es juicio humano de "parece completo" sino el criterio ESTADISTICO de parada: la cota inferior nacional deja de subir entre builds sucesivos. Hoy el sustrato (serie append-only) EXISTE pero el detector (la regla de parada sobre la serie) NO esta construido.

#### (c) Costura ES->generico
La serie append-only y coverage_lower son country-invariantes (math pura + storage). Costura: (1) la serie NO tiene columna country_code [VERIFIED 0048:58 province_code char(2), sin country] -> una DB multi-pais mezcla las series de dos paises en el mismo espacio de build_run_id (depende de F20). (2) el threshold 0.95 que define `sealed` es politica ES [VERIFIED seal.py:27] — un pais de fuentes delgadas hace plateau por debajo de 0.95 y el detector NUNCA declararia saturacion aunque la cota inferior haya dejado genuinamente de subir; la senal de saturacion debe ser "la cota inferior dejo de subir", NO "coverage_lower>=0.95".

#### (d) Riesgo adversarial concreto
- Las cifras actuales (37.7%/80.5%) vienen de recon con el stack CAIDO y NO son re-ejecutables -> un detector de saturacion necesita una serie reproducible; sin inputs hash-pineados (DVC) el "subio entre builds" es DRIFT disfrazado de medicion.
- Listas infra-pobladas / solo 4/25 adaptadores corridos -> el detector puede declarar FALSA saturacion: la cota inferior esta plana no porque el pais este exhausto sino porque no se INGIRIO ninguna lista nueva — "no cubierto" indistinguible de "no observado por esa lista".
- DE/FR (ecosistema fino): coverage_lower hace plateau bajo; "parar cuando >=0.95" nunca dispara, "parar cuando plano" dispara demasiado pronto (confunde inputs finos con saturacion).
- PT/IT/no-UE: mismo confound de inanicion de inputs.
- Ruido: un build anomalo (statsmodels no converge -> masa 'none' -> coverage cae) crea un change-point falso.

#### (e) Criterio de sellado + verificacion multi-via
- (1) serie sintetica monotona-luego-plateau dispara saturacion EXACTAMENTE en el plateau conocido (unit de change-point ruptures).
- (2) se NIEGA a declarar saturacion mientras el VoI esperado de CUALQUIER lista candidata > epsilon (acopla con el selector activo).
- (3) back-test sobre la historia ES: el detector NO debe declarar saturacion en el 37.7% actual con listas infra-pobladas [VERIFIED NEXT-LEVEL.md:202].
- (4) gate de reproducibilidad: re-correr un build_run_id pasado desde inputs hash-pineados -> coverage_lower BYTE-identico (DVC/in-toto); si no, la serie no es medicion.
- (5) aislamiento pais de la serie (cada pais su propia serie por country_code).

#### (f) Herramienta NEXT-LEVEL
`ruptures` (deteccion de change-point offline) implementa la regla de parada FORMAL sobre la serie de coverage_lower: declarar "no queda nada que encontrar" SOLO cuando el change-point muestra que la cota inferior dejo de subir, reemplazando el "parece completo" humano. Complemento `BoTorch` (acquisition = expected information gain) cierra el lazo: la saturacion se declara solo cuando el VoI marginal de TODA lista candidata ~0, asi el detector no confunde inanicion-de-inputs con exhaustion. Reproducibilidad sostenida por `DVC` (inputs hash-pineados) para que el "subio" sea real, no drift.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 13 — Gate de identificabilidad IDENT_CAP + dispatcher de estrato

> **Ficha 360**
>
> **Costura** — IDENT_CAP=5.0 es politica ES (piso fijo 20%) horneada como constante de modulo [VERIFIED estimators.py:304], presentada como universal (break #9); el corte binario _mark_identified [VERIFIED estimators.py:311] descarta informacion parcial. En pais de fuentes delgadas casi todo estrato falla el cap -> roll-up ~0%, indistinguible de mercado vacio (sealing_hole #3).
>
> **Fix** — 1) Mover IDENT_CAP al pack de politica por pais (seed 5.0 ES, no literal de modulo). 2) Reemplazar el binario _mark_identified por un peso de identificabilidad continuo w in [0,1] (funcion del ancho relativo del CI) propagado como inflacion de varianza al roll-up, no include/exclude 0/1. 3) Emitir senal explicita 'evidencia insuficiente para certificar' cuando el pais falla el cap en >X% de estratos (cierra sealing_hole #3).
>
> **Adversarial** — DE/FR/IT/PT: ecosistema cross-border colapsa estratos a K=2 y dispara m0 en los K>=3 -> certifica ~0% sin senal que distinga datos delgados de mercado vacio. No-UE/ruido: espejos de marketplace correlacionados pueden pasar el cap con N_hat sesgado-bajo (la cota robust no ve dependencia de orden superior, facet 3) y sellar en falso; el seed fijo del bootstrap oculta la fragilidad del ancho del CI.
>
> **Sellado** — Via1 (unit, presente): test_sparse_overlap_flagged_unidentified [VERIFIED test_exhaustiveness.py:123-134] + test_dense_overlap_is_identified [VERIFIED 137-140]. Via2: backtest con estratos sinteticos de N conocido -> el gate vira en el piso 20% y el peso continuo es monotono en cobertura real. Via3: golden cross-country -> pais delgado emite 'evidencia insuficiente', no ~0% silencioso. Sellado: cap parametrizado+justificado, ningun estrato unidentified-y-sealed, distincion delgado/vacio probada y expuesta.
>
> **Herramienta NEXT-LEVEL** — SparseMSE (CRAN) — MSE robusto sparse/sin-solape, recupera intervalo finito donde el log-lineal Python da inf-CI (justo lo que IDENT_CAP rechaza); corre por el bridge Rscript existente. https://cran.r-project.org/package=SparseMSE — GPL (>=2) [VERIFIED NEXT-LEVEL.md:119]. Complemento dga (Bayesian Model Averaging) https://cran.r-project.org/package=dga — GPL (>=2) [VERIFIED NEXT-LEVEL.md:127]: posterior de N que da el peso de identificabilidad continuo.

#### (a) Verificacion de code_hints [VERIFIED]
- `IDENT_CAP = 5.0` constante de modulo [VERIFIED estimators.py:304]. El comentario doctrinal 298-303 declara explicitamente: "N_hat debe ser <= IDENT_CAP * n_obs ... 5.0 => un estrato solo esta 'identified' si su piso de cobertura implicito es >= 20%".
- `_mark_identified(e)` [VERIFIED estimators.py:307-318]: `cap = IDENT_CAP * e.n_obs` (308); rama-1 `if e.n_obs <= 0 or not math.isfinite(e.ci_high): e.identified = False` (309-310); rama-2 `elif e.n_hat > cap or e.ci_high > cap: e.identified = False` (311-313); rama-3 `else: e.identified = e.confidence != "none"` (315); democion `if not e.identified and e.confidence == "high": e.confidence = "low"` (316-317).
- `estimate_stratum(freqs, list_order=None)` [VERIFIED estimators.py:321-373]: calcula `k_present` = nº de listas con >=1 captura (339-340); K>=3 -> `loglinear_mse` + ensancha `ci_high` con `dependence_robust_bound` y aplica `_mark_identified` (342-350); K==2 -> deriva n1/n2/m y `chapman(...)` + `_mark_identified` (352-360); K<2 -> `single_list_no_estimate` con `ci_high=float("inf")`, `confidence="none"`, `identified=False` (363-373).
- Tests [VERIFIED test_exhaustiveness.py:123-134] `test_sparse_overlap_flagged_unidentified` (3 listas, solape ~0 -> `identified is False`); [VERIFIED 137-140] `test_dense_overlap_is_identified` (solape denso -> `identified is True`).

#### (b) Mecanismo al atomo
El gate es un **corte multiplicativo unico**: `cap = 5.0 * n_obs`. Un `Estimate` queda `identified` SII se cumplen a la vez: `n_obs>0` AND `finite(ci_high)` AND `n_hat<=cap` AND `ci_high<=cap` AND `confidence!='none'`. El factor 5.0 codifica un **piso de cobertura implicito del 20%** (n_obs/N_hat >= 1/5). El detalle critico es que el cap se aplica a **ci_high ademas de a n_hat** (linea 311): un punto acotado pero con intervalo explosivo (m0 enorme -> CI ancho) se rechaza correctamente — es la valvula que impide que masa no-fijada entre al denominador certificado. La democion 316-317 garantiza la **monotonia anti-maquillaje**: un estrato no-identificado nunca conserva confianza 'high'; baja a 'low'. El dispatcher es el enrutador por densidad: la decision K>=3 / K==2 / K<2 selecciona el nucleo (Fienberg / Chapman / observed-only) y SIEMPRE pasa por `_mark_identified` salvo el K<2, que nace `identified=False` por construccion (su `ci_high=inf` fallaria igual la rama-1). En K>=3 el cap se evalua contra el `ci_high` YA ensanchado por la cota dependence-robust (facet 3), de modo que la identificabilidad se juzga sobre el techo conservador, no sobre el optimista.

#### (c) Costura ES->generico
`IDENT_CAP=5.0` es **politica ES presentada como universal** (break #9). No se deriva de la calidad de datos del pais: es un piso fijo del 20% horneado como constante de modulo. El corte es ademas **binario**: tira informacion parcial util que un peso continuo conservaria.

**Fix exacto:**
1. Mover `IDENT_CAP` al **pack de politica por pais** (junto a threshold y banda 0.7-1.4, facet 23) como `ident_cap`, con 5.0 como *seed* default ES, no como literal de modulo.
2. Sustituir/aumentar el `_mark_identified` binario por un **peso de identificabilidad continuo** w in [0,1] derivado del ancho relativo del CI (p.ej. funcion monotona de `n_obs/ci_high` o de `ci_high/n_hat`), propagado como **inflacion de varianza** en el roll-up nacional (facet 6) en vez de un include/exclude 0/1. Asi un estrato debil contribuye atenuado en lugar de desaparecer.
3. Emitir una **senal explicita "evidencia insuficiente para certificar"** (distinta de "0% cubierto") cuando el pais falla el cap en > X% de estratos — el gate honesto que dice "necesitas mas listas ortogonales", cerrando el sealing_hole #3.

#### (d) Riesgo adversarial concreto
En **DE/FR/IT/PT** el ecosistema cross-border colapsa la mayoria de estratos a K=2 (solo GEO+OEM son transfronterizas, break #3) -> Chapman 'low', y muchos K>=3 igual fallan el cap 5.0 porque el solape esparso dispara m0. Resultado: el motor certifica **~0%** para un pais que puede estar genuinamente bien cubierto, y NO hay senal que distinga "datos delgados" de "mercado vacio" (sealing_hole #3) — indistinguibles. **No-UE / ruido**: un pais inundado de espejos de marketplace (pseudo-listas correlacionadas) puede *pasar* el cap con un N_hat sesgado-a-la-baja (la cota robust no captura dependencias de orden superior compartidas, facet 3), **sellando en falso**. El bootstrap con seed fijo (facet 1) reproduce pero **oculta** la fragilidad del ancho del CI si nadie lo mira.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (unit, presente)**: `test_sparse_overlap_flagged_unidentified` [VERIFIED 123-134] y `test_dense_overlap_is_identified` [VERIFIED 137-140] fijan el comportamiento binario en 5.0.
- **Via 2 (backtest N-conocido)**: generar estratos sinteticos con N VERDADERO a densidades de solape crecientes; asertar que el gate vira exactamente en el piso 20% y que el peso continuo (una vez anadido) es **monotono** en la cobertura real.
- **Via 3 (golden cross-country)**: un pais sintetico de fuentes delgadas debe producir la senal "evidencia insuficiente", NO un sello ~0% silencioso — golden de que ambos estados son **distinguibles**.
- **Sellado**: el gate queda sellado cuando (i) el cap esta parametrizado por pais y justificado contra calidad de datos medible, (ii) ningun estrato es a la vez unidentified y sealed, (iii) la distincion datos-delgados / mercado-vacio es senal probada y expuesta.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**SparseMSE** (CRAN) — MSE robusto para datos de captura sparse/sin-solapamiento (Chan-Silverman-Vincent): recupera un intervalo FINITO exactamente en los estratos donde el log-lineal Python degenera a observed-only/inf-CI, es decir **los que IDENT_CAP rechaza hoy**. Corre bajo el bridge Rscript existente (estimators_r.py:86-129) y degrada graceful si R ausente.
- URL https://cran.r-project.org/package=SparseMSE — Lic **GPL (>=2)** [VERIFIED NEXT-LEVEL.md:119].
- Complemento **dga** (Bayesian Model Averaging) https://cran.r-project.org/package=dga — **GPL (>=2)** [VERIFIED NEXT-LEVEL.md:127]: produce un POSTERIOR de N que integra la incertidumbre de seleccion-de-modelo; su cuantil es la fuente natural del **peso de identificabilidad continuo** que sustituye el corte duro 5.0. Verificacion: cross-check SparseMSE/dga vs log-lineal en estratos con solape dentro de tol=0.25 (puerta de distrust ya existente estimators_r.py:175-193).

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 14 — Unidad de captura e integridad del overlap (m)

> **Ficha 360**
>
> **Costura** — La unidad (v_dealer_resolved.resolved_ulid) es agnostica de pais, pero la calidad del resolver determinista ES-tuned gobierna m, y WHERE kind IN DEALER_KINDS [VERIFIED capture.py:72,88] hornea la taxonomia ES (pierde entidades de otro pais en silencio). La clave de estrato no enhebra country_code: al anadirlo (facet 20) las unidades de dos paises colisionan en el espacio de resolved_ulid.
>
> **Fix** — 1) Enhebrar country_code en la clave seen de _fetch_raw/build y en el INSERT de discovery_capture. 2) WHERE kind IN (...) lee el set de kinds del pack del pais, no la tupla de modulo DEALER_KINDS. 3) Mantener la invariante never-finer (unit splink nunca mas fina que resolved) explicita y testeada al cambiar el resolver por pais.
>
> **Adversarial** — DE/FR/JP: resolver ES-tuned deja duplicados partidos (nombres compuestos alemanes, diacriticos franceses, kanji/kana) -> dos listas que vieron el mismo dealer fallan el solape -> m subcontado -> CI ancho -> nada sella. Sin Splink (facet 12) la unidad es solo el dedup determinista, recall topado por blocking ES. No-UE sin id estable: m colapsa a cero, sello inalcanzable por unidad fragmentada, no por baja cobertura.
>
> **Sellado** — Via1 (adyacente, presente): union-find Splink [VERIFIED test_exhaustiveness.py:196-206] + normalizadores [VERIFIED 188-193]; PERO no hay test directo del colapso una-fila-por-(unidad,bucket) de build() -> hueco a sellar. Via2: integracion con DB sintetica, mismo dealer bajo 3 source_key con entity_ulid partidos -> filas=1/bucket, m==solape disenado, splink nunca >filas que resolved. Via3: intervalo de confianza sobre el dedup, sensibilidad de m al error del resolver acotada.
>
> **Herramienta NEXT-LEVEL** — ER-Evaluation — cardinalidad ER con intervalos de confianza; mide el error del dedup y lo propaga a la incertidumbre de m. https://github.com/OlivierBinette/er-evaluation — AGPL-3.0 [VERIFIED NEXT-LEVEL.md:522] (MARCA copyleft de red: CLI offline o portar math a scipy BSD para ruta servida [VERIFIED :524]). Complemento Splink (Fellegi-Sunter, MIT) https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:450]: sube m preservando never-finer.

#### (a) Verificacion de code_hints [VERIFIED]
- Doctrina de la unidad [VERIFIED capture.py:1-9]: "The capture unit is the *resolved* (cross-source deduped) entity (v_dealer_resolved.resolved_ulid), so a dealer seen in OSM and in autocasion collapses to ONE capture row per list — the fix for the old m=10 problem where unmerged entity_ulids undercounted the overlap."
- `_fetch_raw(conn, unit='resolved'|'splink', splink_run_id)` [VERIFIED capture.py:49-92]: rama `resolved` [VERIFIED 77-92] `SELECT dr.resolved_ulid, COALESCE(re.province_code,e.province_code), COALESCE(re.kind::text,e.kind::text), es.source_key FROM entity_source es JOIN entity e ON e.entity_ulid=es.entity_ulid JOIN v_dealer_resolved dr ON dr.entity_ulid=es.entity_ulid LEFT JOIN entity re ON re.entity_ulid=dr.resolved_ulid WHERE e.kind::text IN %s` con `DEALER_KINDS`; rama `splink` [VERIFIED 57-76] usa `COALESCE(sc.splink_cluster, dr.resolved_ulid)` (62) — fallback a resolved cuando la entidad no esta en el run Splink.
- `build(...)` colapso [VERIFIED capture.py:107-118]: `seen: dict[(resolved_ulid,bucket)] = (province, seg)`; primer link gana (`if key not in seen`); `rows` = una fila por (unidad, bucket).
- INSERT idempotente [VERIFIED capture.py:140-148] `ON CONFLICT (resolved_ulid, list_key, build_run_id) DO NOTHING`; `replace=True` -> DELETE del build (136-139).

#### (b) Mecanismo al atomo
La **unidad de captura** — lo que cuenta como UN dealer fisico y por tanto define `m` (solape) y el ancho del CI — es la entidad cross-source deduplicada `v_dealer_resolved.resolved_ulid`. El SQL enhebra `entity_source -> entity -> v_dealer_resolved` y **COALESCE** de `province_code`/`kind` desde la entidad RESUELTA (`re`) sobre la cruda (`e`) [VERIFIED capture.py:80-83/62-65], de modo que los atributos del estrato siguen a la unidad canonica, no a la fila origen. `build()` colapsa los links de `entity_source` a un dict `seen` clavado `(resolved_ulid, bucket)`: el PRIMER link de una unidad resuelta a un bucket ortogonal gana, produciendo **exactamente una fila de captura por (dealer fisico, lista)**. Esa es la definicion operativa de "un dealer visto en OSM y en autocasion colapsa a UNA fila por lista", que arreglo el viejo m=10 donde `entity_ulid` sin mergear partia el mismo dealer y destruia el solape. `unit='splink'` cambia la clave a `COALESCE(splink_cluster, resolved_ulid)` — **nunca mas fina que resolved** (fallback a resolved si ausente del run), imponiendo la invariante *never-finer*: la unidad solo puede volverse MAS GRUESA (mas merge -> mas solape -> CI mas estrecho), jamas mas fina. El INSERT es idempotente y el build append-only por `build_run_id`.

#### (c) Costura ES->generico
La definicion de la unidad es **agnostica de pais** (es lo que `v_dealer_resolved` resuelva), asi que la costura es INDIRECTA: la **calidad del resolver determinista gobierna m**, y ese resolver (blocking/normalizacion) esta afinado a ES. Ademas `WHERE e.kind::text IN DEALER_KINDS` [VERIFIED capture.py:72,88] hornea la taxonomia ES de tipos (facet 14): un pais con kinds distintos **pierde entidades del universo de captura en silencio**. La clave de estrato `(province_code, segment)` se enhebra implicitamente; al anadir `country_code` como dimension externa (facet 20) la clave de `seen` y el SELECT deben enhebrarlo o las unidades de dos paises **colisionan** en el mismo espacio de `resolved_ulid`.

**Fix exacto:**
1. Enhebrar `country_code` en la clave de `seen` de `_fetch_raw`/`build` y en el INSERT de `discovery_capture`.
2. Hacer que `WHERE kind IN (...)` lea el set de kinds del **pack del pais**, no la tupla de modulo `DEALER_KINDS`.
3. Mantener la invariante never-finer EXPLICITA y testeada cuando se cambie el resolver por pais.

#### (d) Riesgo adversarial concreto
En un pais donde el resolver determinista (`v_dealer_resolved`) deja duplicados cross-source partidos — nombres compuestos alemanes ("Auto Mueller GmbH & Co. KG" vs "Autohaus Mueller"), diacriticos franceses, kanji/kana japones que el blocker ES-tuned no casa (facet 12) — dos listas que vieron el MISMO dealer fisico fallan el solape -> **m subcontado -> CI artificialmente ancho -> coverage_lower bajo -> nada sella**. Sin Splink encendido (facet 12) la unidad es SOLO el dedup determinista, asi que el recall del solape esta topado por el blocking ES de name/phone/municipality. **No-UE**: un pais sin id nacional estable y con alta varianza de transliteracion es el peor caso — `m` colapsa hacia cero y el sello es inalcanzable no porque la cobertura sea baja sino porque la **unidad esta fragmentada** (un fallo de medicion disfrazado de fallo de cobertura).

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (presente, adyacente)**: los tests de union-find Splink [VERIFIED test_exhaustiveness.py:196-206] prueban el merge transitivo y los normalizadores [VERIFIED 188-193] guardan la ruta never-finer. **PERO no hay test directo** que aserte que `build()` colapsa dos links del mismo `resolved_ulid` en UNA fila de captura — esa invariante de integridad esta hoy **sin guardia** (hueco a sellar).
- **Via 2**: test de integracion sobre DB sintetica donde el MISMO dealer fisico se inserta bajo 3 `source_key` con `entity_ulid` partidos que el resolver mergea -> asertar filas de captura = (1 por bucket), `m` == solape disenado, y que `unit='splink'` NUNCA produce MAS filas que `unit='resolved'` (never-finer).
- **Via 3**: cross-check de cardinalidad certificada — poner un intervalo de confianza sobre el propio dedup y asertar que la sensibilidad de `m` al error del resolver esta acotada.
- **Sellado**: la unidad queda sellada cuando (i) el colapso una-fila-por-(unidad,bucket) de `build()` esta unit-testeado, (ii) la invariante never-finer esta testeada resolved<->splink, (iii) el filtro de kind y la clave de estrato estan parametrizados por pais, (iv) el dedup arrastra un error medido que alimenta la incertidumbre de `m`.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**ER-Evaluation** — cardinalidad de entity-resolution CON intervalos de confianza: convierte "la unidad resuelta es de verdad UN dealer fisico" de supuesto a magnitud MEDIDA con error acotado, que propaga a la incertidumbre de `m`.
- URL https://github.com/OlivierBinette/er-evaluation — Lic **AGPL-3.0** [VERIFIED NEXT-LEVEL.md:522] (licencia tambien [VERIFIED :63]). **MARCA**: copyleft de red; usar como CLI offline de analisis/reporte (sin servicio de red que la exponga) o portar la matematica del estimador a scipy (BSD) para una ruta servida permisiva [VERIFIED NEXT-LEVEL.md:524].
- Complemento para RECUPERAR solape perdido: **Splink** (Fellegi-Sunter probabilistico) https://github.com/moj-analytical-services/splink — **MIT** [VERIFIED NEXT-LEVEL.md:401,450]: es el mecanismo que SUBE `m` (solape mas apretado -> CI menor -> coverage_lower mayor) preservando never-finer (corre sobre DuckDB/Postgres existente, €0). Owned por facet 12 pero es la palanca directa de integridad de `m`.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 15 — Particion de region + diseno de la rejilla de estratificacion

> **Ficha 360**
>
> **Costura** — geo_province.code es CHAR(2) PK sin columna country [VERIFIED 0001_geo.sql:5] (break #1): trunca codigos no-ES (AGS aleman 5 dig, DOM frances '971' 3-char) y ES'01'(Alava) colisiona con FR'01'(Ain) en el mismo estrato. El CHECK left(code,2)=province_code [VERIFIED 0001_geo.sql:26] hornea el coding INE 2+3. La homogeneidad intra-estrato es premisa implicita del log-lineal [VERIFIED estimators.py:238-241], no garantizada por la rejilla coarse 52x4 [VERIFIED capture.py:8].
>
> **Fix** — 1) Ensanchar province_code CHAR(2)->region_code TEXT en geo_province/geo_municipality/discovery_capture/exhaustiveness_estimate; anadir country_code CHAR(2) NOT NULL, PK (country_code, region_code) (coordinado con facet 20). 2) Sustituir el CHECK left(code,2) por uno parametrizado por pais o eliminarlo si el coding no es prefijo-jerarquico. 3) Adoptar vocabulario ISO 3166-2 por pais (ES como seed). 4) Eje de estratificacion fino opcional (tamano municipio / urbano-rural / celda H3) para la homogeneidad Fienberg.
>
> **Adversarial** — DE (401 Kreise, AGS 5 dig) y FR (101 departements, DOM '971') no caben en CHAR(2) -> truncamiento/rechazo. ES'01'/FR'01' colisionan -> build multi-pais sin country_code (facet 20) suma N_hat cruzando paises. Disparidad municipal extrema viola Fienberg y sesga N sin marca. Re-cortar por multiples ejes a la vez deja celdas en K<3 (no-identificadas): un cambio de geometria puede BAJAR el % sellado por construccion, riesgo de mala-lectura.
>
> **Sellado** — Via1 (schema): migracion inserta region_code no-ES (AGS '09162', '971') y par ES'01'/FR'01' bajo country distinto -> coexisten sin colision, CHECK no rechaza (golden tenancy). Via2 (conservacion): suma de n_obs sobre celdas region x segment == n_obs nacional al re-cortar. Via3 (homogeneidad): bondad-de-ajuste del log-lineal por celda o contraste pooled-vs-stratified [VERIFIED seal.py:109-114] que aflore heterogeneidad. Sellado: region_code text+country sin colision, conservacion testeada, diagnostico de heterogeneidad minimizado sin tirar celdas a K<3.
>
> **Herramienta NEXT-LEVEL** — pycountry (ISO 3166-1/-2 + ISO 4217) — autoridad de subdivisiones ISO 3166-2 que reemplaza el INE char(2) ES-only por vocabulario de region country-proof. https://github.com/pycountry/pycountry — LGPL-2.1 [VERIFIED NEXT-LEVEL.md:530] (alt iso3166 MIT [VERIFIED :531]). Homogeneidad: Uber H3 (h3-py) https://github.com/uber/h3 Apache-2.0 [VERIFIED NEXT-LEVEL.md:361] -> celdas de area uniforme contra el sesgo de estratos administrativos dispares [VERIFIED :360]. Backbone generico: GeoNames dump CC-BY 4.0 [VERIFIED :377].

#### (a) Verificacion de code_hints [VERIFIED]
- `geo_province` [VERIFIED 0001_geo.sql:4-9]: `code CHAR(2) PRIMARY KEY` (5, "INE province code, 2 digits"), `ccaa_code CHAR(2)` — **sin columna country**.
- `geo_municipality` [VERIFIED 0001_geo.sql:18-27]: `code CHAR(5) PRIMARY KEY` (19, "INE municipality code, 5 digits (province = left 2)"), `province_code CHAR(2) NOT NULL REFERENCES geo_province(code)` (21), invariante `CONSTRAINT municipality_province_prefix CHECK (left(code,2)=province_code)` (26).
- Rejilla [VERIFIED capture.py:8] docstring "Strata: province_code x segment (4 broad dealer types) ~ 52 x 4"; [VERIFIED capture.py:31] "kind -> 4 broad segments (province x segment ~ 200 strata, per §2.2)".
- Homogeneidad Fienberg: [VERIFIED estimators.py:217] `if select_interactions and k_present >= 3:` es el gate de busqueda BIC de interacciones; la homogeneidad intra-estrato es la **premisa implicita** de `loglinear_mse` (un unico intercept `m0=exp(beta0)` por estrato, [VERIFIED estimators.py:238-241]) — NO una sentencia literal en la 217. [ASSUMED a nivel de linea; VERIFIED como premisa del estimador 172-262].

#### (b) Mecanismo al atomo
La **dimension-1 del estrato** es `region_code` (en ES: el `province_code` INE CHAR(2) '01'..'52'), su clave primaria gobierna toda la cadena: `discovery_capture.province_code` -> `read_patterns` agrupa por `(province, segment)` -> `estimate_stratum` corre un MSE INDEPENDIENTE por celda. La **geometria de la rejilla** es `region x segment` ~ 52x4 = 208 celdas. El supuesto que hace VALIDA toda la matematica Fienberg por celda es la **homogeneidad intra-estrato**: dentro de una celda, la probabilidad de captura por cada lista es constante entre unidades. Si la celda mezcla sub-poblaciones heterogeneas (urbano vs rural, municipio grande vs diminuto) con probabilidades de captura distintas, el log-lineal **sesga N** por heterogeneidad no modelada — exactamente lo que la cota dependence-robust (facet 3) intenta atenuar pero no elimina. Hay un **tradeoff de geometria**: rejilla *coarse* (pocas celdas grandes) -> mas heterogeneidad intra-estrato -> sesgo; rejilla *fine* (muchas celdas pequenas) -> cada celda cae a K<3 -> no-identificada (facet 4) -> masa uncertified. El diseno de la rejilla es la palanca que arbitra ese tradeoff.

#### (c) Costura ES->generico
`geo_province.code` es **CHAR(2) PK sin columna country** [VERIFIED 0001_geo.sql:5]. Esto rompe de dos formas (break #1):
1. **Truncamiento**: CHAR(2) no admite codigos no-ES — AGS aleman (5 digitos), departement frances '971'-'976' (3-char DOM), prefectura japonesa. Un codigo Kreis aleman se trunca/rechaza.
2. **Colision**: ES '01' (Alava) y FR '01' (Ain) caen en el MISMO estrato sin columna que los separe -> el MSE mezcla dos paises en una celda.
Ademas `geo_municipality.code CHAR(5)` y el `CHECK left(code,2)=province_code` [VERIFIED 0001_geo.sql:26] hornean el coding INE 2+3 espanol; load_geo.py:26-70 hardcodea 52 provincias + zfill(2)/zfill(3) [VERIFIED NEXT-LEVEL.md:376].

**Fix exacto:**
1. Ensanchar `province_code CHAR(2)` -> `region_code TEXT` (o VARCHAR generoso) en `geo_province`, `geo_municipality`, `discovery_capture` y `exhaustiveness_estimate`; anadir `country_code CHAR(2) NOT NULL` (coordinado con facet 20) de modo que la PK pase a `(country_code, region_code)`.
2. Reemplazar el `CHECK left(code,2)=province_code` por un check parametrizado por pais o eliminarlo donde el coding no sea prefijo-jerarquico.
3. Adoptar un **vocabulario de region canonico por pais** (ISO 3166-2) en vez del INE char(2), con ES mapeado como seed.
4. Para la homogeneidad: anadir un eje de estratificacion fino (tamano de municipio / urbano-rural / celda H3) opcional, gobernado por el tradeoff coarse/fine.

#### (d) Riesgo adversarial concreto
**DE** (401 Kreise, AGS de 5 digitos) y **FR** (101 departements, DOM '971'+) **no caben** en CHAR(2): el loader trunca o rechaza, y la rejilla se queda sin dimension-1 valida. **ES vs FR**: '01' colisiona -> un build multi-pais sobre la misma tabla (sin country_code, facet 20) **suma N_hat a traves de paises** en la celda '01'. **Homogeneidad**: en paises con disparidad municipal extrema (una sola "region" que abarca metropolis y campo), la celda viola Fienberg y N se sesga sin que nada lo marque. **Re-estratificar por multiples ejes a la vez** (region x segmento x urbano/rural) es un **re-corte combinatorio** que puede dejar muchas celdas en K<3 -> no-identificadas -> el pais certifica menos (masa uncertified sube) aunque la cobertura real no haya cambiado: un cambio de geometria puede BAJAR el % sellado por construccion, riesgo de mala-lectura.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (schema)**: test de migracion que inserta un `region_code` no-ES (AGS '09162' Munich, '971' Guadeloupe) y un par ES'01'/FR'01' bajo country_code distinto -> asertar que coexisten sin colision y que el `CHECK` no rechaza (golden de tenancy).
- **Via 2 (invariante de conservacion)**: la suma de `n_obs` sobre todas las celdas region x segment == `n_obs` nacional (ninguna unidad perdida ni doble-contada al re-cortar la rejilla).
- **Via 3 (homogeneidad)**: por celda, un test de bondad-de-ajuste del log-lineal (residuos de Pearson) o un contraste pooled-vs-stratified [VERIFIED seal.py:109-114 pooled UNRELIABLE] que aflore heterogeneidad; el detector debe marcar las celdas donde el supuesto Fienberg se rompe.
- **Sellado**: la rejilla queda sellada cuando (i) region_code es text con country_code y soporta codigos no-ES sin colision, (ii) la conservacion de masa al re-cortar esta testeada, (iii) existe un diagnostico de heterogeneidad intra-estrato y la geometria elegida lo minimiza sin tirar celdas a K<3.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**pycountry** (ISO 3166-1/-2 + ISO 4217) — autoridad de subdivisiones ISO 3166-2 para el grano de region: reemplaza el INE char(2) ES-only por un **vocabulario de region country-proof** valido para CUALQUIER pais, eliminando truncamiento y colision de raiz.
- URL https://github.com/pycountry/pycountry — Lic **LGPL-2.1** [VERIFIED NEXT-LEVEL.md:530]. Alt permisiva `iso3166` (MIT, solo paises) [VERIFIED :531] para el subconjunto sin copyleft.
- Para la **homogeneidad intra-estrato** (estratos de tamano uniforme): **Uber H3 (h3-py)** https://github.com/uber/h3 — **Apache-2.0** [VERIFIED NEXT-LEVEL.md:361]. El doc lo ata explicitamente: "El sello actual estratifica por unidades administrativas de tamano muy dispar (un municipio rural enorme vs uno urbano diminuto sesgan la cota MSE)" [VERIFIED NEXT-LEVEL.md:360]; H3 da celdas de area uniforme -> cumple mejor el supuesto Fienberg.
- Para el **backbone de region generico** pan-pais: **GeoNames dump** (admin1/admin2) https://download.geonames.org/export/dump/ — **CC-BY 4.0** [VERIFIED NEXT-LEVEL.md:377]; reemplaza el load_geo.py que hardcodea 52 provincias + zfill INE [VERIFIED :376].

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 16 — Orquestacion de ejecucion, config DSN/env + CLI de onboarding

> **Ficha 360**
>
> **Costura** — cli.py:36-37 invoca seal.compute SIN external_census ni country [VERIFIED]; el default cascada external_census=None -> load_external_census(country_code=DEFAULT_COUNTRY='ES') -> dirce_cnae451.csv [VERIFIED seal.py:68-69, triangulation.py:27,38,50] deja la parametricidad MUERTA al llegar desde la orquestacion (break #2). DSN literal en capture.py:17 y migrate.py:15 [VERIFIED] no leen os.environ (a diferencia de discover.py:46/harvest_dealer.py:25 [VERIFIED]). cli.py no pasa por config_guard [VERIFIED cli.py:14-15].
>
> **Fix** — 1) Anadir --country CC requerido a argparse y enhebrarlo run->capture.build->seal.compute->load_external_census(country_code=); quitar el default 'ES' para que un build sin country falle ruidoso. 2) capture.py:17 y migrate.py:15 -> os.environ.get('CARDEEP_DSN', dev-default), patron ya probado [VERIFIED discover.py:46]. 3) Wirar config_guard.require_prod_secrets en cli.run [VERIFIED config_guard.py:140-171]. 4) Sustituir el string 'live DB 127.0.0.1:5433' [VERIFIED cli.py:31] por el host resuelto. 5) Onboarding como secuencia explicita migrar->seed->build->compute->verify.
>
> **Adversarial** — DE/FR/IT/PT: cli.py run sobre otro pais triangula N_hat contra el censo ES (DIRCE/DGT/FACONAUTO) por el default DEFAULT_COUNTRY='ES' -> veredicto de triangulacion es basura semantica (falso 'consistent'/'n_hat_high'). No-UE: load devuelve {} (no_anchor honesto) pero el operador no sabia que apuntaba a ES por default. DSN literal: en no-dev se conecta a cardeep_dev_only o falla confuso y arrastra la credencial dev (el config_guard que lo atraparia no esta wired en esta ruta). Onboarding a medias (migrar sin seed geo) -> estratos region NULL como celda nacional espuria.
>
> **Sellado** — Via1 (parametricidad): cli.run(country='DE') con fixture DE+censo DE -> load_external_census resuelve countries/DE/census, NO el CSV ES; cli.run() sin country lanza error. Via2 (env): CARDEEP_DSN a DB efimera -> capture.build/migrate.apply usan esa DSN; con CARDEEP_ENV=prod+DSN dev, assert_safe_dsn ABORTA [VERIFIED config_guard.py:99-106]. Via3 (onboarding e2e): golden migrar->seed->build->compute->verify sobre pais #2 sintetico -> sello aislado y reproducible, baseline ES byte-identica (cero regresion). Sellado: --country e2e + fallo ruidoso, capture/migrate env-driven, sello tras config_guard, onboarding testeado e idempotente.
>
> **Herramienta NEXT-LEVEL** — Pydantic — run-config del sello como contrato tipado validado en la frontera: country pasa a REQUERIDO, dsn de env validado, defaults ES silenciosos imposibles. https://github.com/pydantic/pydantic — MIT [VERIFIED NEXT-LEVEL.md:587]. Onboarding como maquina de estados guard-gated: transitions (pytransitions) https://github.com/pytransitions/transitions MIT [VERIFIED NEXT-LEVEL.md:595]. Drains/build como tareas durables sobre el PG existente: Procrastinate https://github.com/procrastinate-org/procrastinate MIT [VERIFIED NEXT-LEVEL.md:555].

#### (a) Verificacion de code_hints [VERIFIED]
- `cli.run(...)` [VERIFIED cli.py:18-70] secuencia `capture.build(run_id, unit=, splink_run_id=)` (30) -> `seal.compute(run_id, threshold=, include_mkt=, r_crosscheck=)` (36-37) -> imprime denominador. **`compute()` se invoca SIN `external_census` ni `country`** [VERIFIED cli.py:36-37].
- Flags `--run-id/--threshold/--include-mkt/--unit/--splink-run-id/--r-crosscheck` [VERIFIED cli.py:77-82]. **No hay flag `--country`**.
- DSN **hardcodeado** `"postgresql://cardeep:cardeep_dev_only@localhost:5433/cardeep"` [VERIFIED capture.py:17] y [VERIFIED migrate.py:15] — NO leen `os.environ`.
- Contraste: el resto del pipeline SI es env-driven: [VERIFIED discover.py:46] `os.environ.get("CARDEEP_DSN", ...)`, [VERIFIED harvest_dealer.py:25] idem, [VERIFIED discover_schedule.py:44] idem.
- `seal.compute` auto-carga censo ES [VERIFIED seal.py:68-69] `if external_census is None: external_census = triangulation.load_external_census()`; `load_external_census(country_code=DEFAULT_COUNTRY)` [VERIFIED triangulation.py:38] con `DEFAULT_COUNTRY` importado de `pipeline.paths` (24) y `p = path or (census_dir(country_code)/CENSUS_CSV_NAME)`, `CENSUS_CSV_NAME='dirce_cnae451.csv'` [VERIFIED triangulation.py:27,50].
- `config_guard` [VERIFIED config_guard.py:76-171]: `assert_safe_dsn`/`require_api_key_or_fail`/`require_prod_secrets` solo arman bajo `CARDEEP_ENV=prod`; wired en API lifespan + schedulers. **`cli.py` NO importa config_guard** [VERIFIED cli.py:14-15] (solo `capture, seal` y `r_status`).

#### (b) Mecanismo al atomo
`cli.py` es el **entrypoint operativo end-to-end**: argparse -> `run()` -> `capture.build` -> `seal.compute` -> `report`. Degradacion graciosa: R/Splink ausentes no rompen (`r_status()` informa, `unit='resolved'` por defecto). El problema atomico es la **fuga de parametricidad por pais en la frontera de orquestacion**: aunque `seal.compute` ACEPTA `external_census=` y `triangulation.load_external_census` ACEPTA `country_code=`, la CLI **nunca los pasa** (cli.py:36-37), asi que el default cascada `external_census=None -> load_external_census() -> country_code=DEFAULT_COUNTRY='ES' -> dirce_cnae451.csv`. La parametricidad existe en las firmas pero esta **MUERTA al llegar desde arriba** (break #2). Segundo atomo: el **DSN hardcodeado** en capture.py:17 y migrate.py:15 — unicos dos puntos del pipeline que NO leen `os.environ` (a diferencia de discover/harvest/schedule) — bloquea correr el sello contra cualquier DB no-default y arrastra la credencial `cardeep_dev_only` a entornos no-dev. Tercero: `cli.py` no pasa por `config_guard`, asi que el sello no tiene el fail-fast de prod que SI tienen API y schedulers.

#### (c) Costura ES->generico
La costura es la **cadena de defaults ES en la frontera CLI->compute->triangulation**. Un build aleman lanzado por `cli.py run` triangula su `N_hat(DE)` contra el **censo ESPANOL** (DIRCE/DGT/FACONAUTO via dirce_cnae451.csv) porque nadie enhebra `country`. Y el DSN literal impide apuntar a otra DB sin editar codigo.

**Fix exacto:**
1. Anadir `--country CC` (requerido, sin default oculto) a argparse [VERIFIED cli.py:76-82] y enhebrarlo `run(country) -> capture.build(country=) -> seal.compute(country=) -> triangulation.load_external_census(country_code=country)`. Quitar el default `'ES'` de la cascada: que un build SIN country **falle ruidoso**, no triangule contra ES en silencio.
2. Reemplazar el DSN literal de capture.py:17 y migrate.py:15 por `os.environ.get("CARDEEP_DSN", <dev-default>)` — el patron YA probado [VERIFIED discover.py:46, harvest_dealer.py:25].
3. Wirar `config_guard.require_prod_secrets((dsn,"CARDEEP_DSN"))` en `cli.run` para que el sello tenga el mismo fail-fast de prod [VERIFIED config_guard.py:140-171].
4. Reemplazar el string hardcodeado "live DB 127.0.0.1:5433" [VERIFIED cli.py:31] por el host resuelto.
5. Procedimiento de onboarding de pais como secuencia explicita: migrar -> seed geo -> build captura -> compute -> verificacion 2a via (R/triangulacion).

#### (d) Riesgo adversarial concreto
**DE/FR/IT/PT**: `cli.py run` sobre datos de otro pais **triangula contra el censo ES** (break #2) -> el veredicto de triangulacion (consistent/n_hat_high/n_hat_low) es **basura semantica** (compara peras alemanas con un techo DIRCE espanol) y puede declarar 'consistent' o disparar un falso 'n_hat_high' sin sentido. **No-UE**: sin censo del pais, `load_external_census` devuelve {} (no_anchor) — esto al menos es honesto, PERO el operador no sabe que ESTABA apuntando a ES por default. **DSN literal**: en un entorno no-dev, capture.py/migrate.py se conectan a `cardeep_dev_only@localhost:5433` o fallan confuso, y arrastran la credencial dev fuera de dev (el config_guard que lo atraparia NO esta wired en esta ruta [VERIFIED cli.py:14-15]). **Ruido**: un onboarding a medias (migrar sin seed geo) produce estratos con region NULL que el sello cuenta como una celda nacional espuria.

#### (e) Criterio de sellado + verificacion multi-via
- **Via 1 (parametricidad)**: test que invoca `cli.run(country='DE')` con una DB DE de fixture y un censo DE -> asertar que `load_external_census` resolvio `countries/DE/census/...`, NO el CSV ES; y que `cli.run()` sin country **lanza error** (no silenciosamente ES).
- **Via 2 (env-driven)**: test que setea `CARDEEP_DSN` a una DB efimera y corre capture.build/migrate.apply -> asertar que se conectan a esa DSN, no al literal; y con `CARDEEP_ENV=prod` + DSN dev, `config_guard.assert_safe_dsn` ABORTA [VERIFIED config_guard.py:99-106].
- **Via 3 (onboarding e2e)**: golden de la secuencia migrar->seed->build->compute->verify sobre un pais #2 sintetico -> el sello del pais #2 sale aislado y reproducible, y la baseline ES queda byte-identica (cero regresion).
- **Sellado**: la orquestacion queda sellada cuando (i) `--country` se enhebra de extremo a extremo y un build sin country falla ruidoso, (ii) capture/migrate son env-driven como el resto del pipeline, (iii) el sello pasa por config_guard, (iv) el onboarding de pais es un procedimiento testeado e idempotente.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Pydantic** — el run-config del sello como **CONTRATO TIPADO** validado en la frontera: `country` pasa a campo REQUERIDO, `dsn` se resuelve de env con validacion, y los defaults ES silenciosos se vuelven imposibles (un build sin country no construye un objeto valido).
- URL https://github.com/pydantic/pydantic — Lic **MIT** [VERIFIED NEXT-LEVEL.md:587]. Corre en CI sin DB viva (fixtures), €0 [VERIFIED :589].
- Para el **procedimiento de onboarding** como maquina de estados diagramable y guard-gated (migrar -> seed geo -> build -> compute -> verify): **transitions (pytransitions)** https://github.com/pytransitions/transitions — **MIT** [VERIFIED NEXT-LEVEL.md:595]: define `cover(CC)` como Machine con `conditions=` apuntando a los predicados (geo seed>0, dry-run verde, predicado de sellado) [VERIFIED :596-597].
- Para los **drains/build como tareas DURABLES** sobre el Postgres existente (retry, idempotencia, supervision) en vez de loops a mano: **Procrastinate** https://github.com/procrastinate-org/procrastinate — **MIT** [VERIFIED NEXT-LEVEL.md:555].

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 17 — Criterio de sello por estrato + figura coverage_lower anti-maquillaje

> **Ficha 360**
>
> **Costura** — El UNICO seam es la constante de politica DEFAULT_THRESHOLD=0.95 (seal.py:27), heredada de ES y presentada como universal (break #9); se enhebra via compute(threshold=...) (seal.py:54) -> _seal_one. La LEY del sello (coverage_lower=n_obs/ci_high; el punto NUNCA sella; estimators.py:66-71, __init__.py:16-19) es country-invariante y porta byte-identica. Acoplada: IDENT_CAP=5.0 (estimators.py:304) que alimenta el flag identified.
>
> **Fix** — Mover threshold (y ident_cap, banda triangulacion) de DEFAULT de modulo a politica por pais en countries/<CC>/seal_policy.yaml, default-ES={0.95,5.0,[0.7,1.4]}, cargada en compute(). Anadir gate de evidencia-insuficiente (facet 23): con <3 listas ortogonales en la mayoria de estratos, emitir confidence='insufficient_lists' en vez de certificar ~0% (indistinguible de pais vacio, sealing_hole #3). La logica del predicado AND de 3 clausulas (seal.py:42-46) no cambia.
>
> **Adversarial** — DE/FR/IT/PT delgados: K<3 dominante -> el sello rehusa bien, pero 0.95 inalcanzable sin senal de recalibracion vs pais vacio (sealing_hole #3). Si ci_high se subestima (cota robust insuficiente -facet 3- o dependencia orden>2 fuera del class-model), coverage_lower=n_obs/ci_high se sesga al alza -> sello indebido; toda la garantia anti-maquillaje depende de que ci_high sea cota superior real. Auto-consistencia (sealing_hole #1): 2-3 listas ruidosas correlacionadas pueden dar coverage_lower>=0.95 sesgado sin que ningun censo pueda vetar (facet 9 no construida).
>
> **Sellado** — Criterio: el predicado usa SOLO coverage_lower (nunca coverage_point), exige identified y finito. Multi-via: (1) unit coverage_lower==n_obs/ci_high (test_exhaustiveness.py:143-149); (2) invariante servido coverage_lower<=coverage_point<=1 en cada fila (test_api_exhaustiveness.py:48-59); (3) adversarial sealed==>coverage_lower>=threshold (test_api_exhaustiveness.py:61-72); (4) property-based para todo (n_obs,n_hat,ci_low,ci_high) con ci_high>=n_hat>=n_obs.
>
> **Herramienta NEXT-LEVEL** — PRIMARIA in-toto (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:643]: atestacion firmada {git SHA + content-hashes de inputs}->{coverage_lower,CI,N_hat} anclada a Sigstore/rekor; el sello pasa de afirmacion a certificado no-repudiable re-verificable por terceros. ADYACENTE dga BMA (GPL>=2) https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127] hace coverage_lower honesto ante incertidumbre de seleccion-de-modelo; Great Expectations (Apache-2.0) https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167] como contrato pre-sello fail-closed.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/exhaustiveness/seal.py:27` -> `DEFAULT_THRESHOLD = 0.95` [VERIFIED].
- `seal.py:30-37` -> dataclass `StratumSeal(province_code, segment, estimate, threshold, sealed)` [VERIFIED].
- `seal.py:39-47` -> `_seal_one`: `e = est.estimate_stratum(freqs); cov_lower = e.coverage_lower; sealed = (e.identified and math.isfinite(cov_lower) and cov_lower >= threshold)` [VERIFIED].
- `pipeline/exhaustiveness/estimators.py:61-63` -> `coverage_point = n_obs/n_hat if n_hat>0 else nan` [VERIFIED].
- `estimators.py:65-71` -> `coverage_lower = n_obs/ci_high if ci_high>0 else nan`; docstring literal: "Conservative coverage: observed over the UPPER bound of N-hat. This is the anti-maquillaje figure used for sealing." [VERIFIED].
- `pipeline/exhaustiveness/__init__.py:16-19` -> doctrine: "the point estimate is never used to certify coverage. Sealing uses N_hat_upper so that coverage_lower = n_obs / N_hat_upper, the conservative (anti-maquillaje) figure." [VERIFIED].
- `tests/test_exhaustiveness.py:143-149` -> `test_coverage_lower_uses_upper_bound`: with ci_high=125, coverage_point~=0.8 and coverage_lower~=80/125 [VERIFIED].
- Cross-dependency: `estimators.py:304` `IDENT_CAP=5.0` and `estimators.py:307-318` `_mark_identified` produce the `identified` flag that the seal predicate ANDs against [VERIFIED].

#### (b) Mecanismo al atomo
La LEY del sello es un AND de tres clausulas en `seal.py:42-46`:
1. `e.identified` -- compuerta de `_mark_identified` (estimators.py:307-318): identified sii `n_obs>0` AND `isfinite(ci_high)` AND `n_hat <= 5.0*n_obs` AND `ci_high <= 5.0*n_obs` AND `confidence != 'none'`. Degrada `high`->`low` si no identificado.
2. `math.isfinite(cov_lower)` -- bloquea ci_high=inf (estrato de lista unica, estimators.py:367).
3. `cov_lower >= threshold` con `cov_lower = n_obs / ci_high` (estimators.py:66-71).
La GARANTIA estructural: el denominador de coverage_lower es `ci_high` (la COTA SUPERIOR del IC), por lo que SOBRE-estimar N solo puede SUBIR ci_high -> BAJAR coverage_lower -> hace mas dificil sellar. Inflar N jamas puede inflar el sello. `coverage_point` (n_obs/n_hat) se computa y persiste (seal.py:192) pero NUNCA aparece en el predicado. El sello nacional reusa la misma figura: `nat_cov_lower = n_obs_cert / nat_ci_high` (seal.py:107), sellado si `>= threshold` (seal.py:138).

#### (c) Costura ES->generico + fix exacto
`DEFAULT_THRESHOLD = 0.95` (seal.py:27) es una CONSTANTE DE POLITICA heredada de ES, presentada como universal (break #9). Se enhebra via `compute(threshold=DEFAULT_THRESHOLD)` (seal.py:54) hasta `_seal_one`. La LEY en si (el punto nunca sella; coverage_lower = n_obs/ci_high) es country-INVARIANTE y correcta -- porta byte-identica. La costura es PURAMENTE la calibracion de 0.95 (y del IDENT_CAP=5.0 que alimenta `identified`).
- Fix: mover threshold de DEFAULT de modulo a politica por pais: `countries/<CC>/seal_policy.yaml` { threshold, ident_cap, triangulation_band }, default-ES = {0.95, 5.0, [0.7,1.4]}, cargado en compute().
- Anadir el gate de evidencia-insuficiente (facet 23): si el pais tiene <3 listas ortogonales en la mayoria de estratos, emitir `confidence='insufficient_lists'` EN VEZ de certificar ~0% (indistinguible de pais genuinamente vacio -- sealing_hole #3).

#### (d) Riesgo adversarial concreto
- DE/FR/IT/PT (ecosistema delgado): la mayoria de estratos caen a K<3 -> no identified -> el sello rehusa correctamente, pero 0.95 es inalcanzable SIN senal de que necesita recalibracion vs pais genuinamente vacio (break #9, sealing_hole #3).
- Si `ci_high` se SUBESTIMA (cota dependence-robust insuficiente -facet 3-, o dependencia de orden >2 fuera del class-model), entonces coverage_lower = n_obs/ci_high se sesga al ALZA -> el estrato sella indebidamente. Toda la garantia anti-maquillaje descansa en que ci_high sea una cota superior real.
- Trampa de auto-consistencia (sealing_hole #1): en un pais nuevo con 2-3 listas ruidosas correlacionadas el MSE puede ser internamente consistente (coverage_lower>=0.95) pero muy sesgado; el sello certifica por auto-consistencia porque ningun censo externo puede vetar (facet 9 no construida).
- Ruido (marketplaces disfrazados de listas): si listas no-ortogonales entran, n_hat se sesga a la baja, coverage_lower a la alza -> sello falso.

#### (e) Criterio de sellado + verificacion multi-via
- Criterio: el predicado de sello debe (1) usar SOLO coverage_lower (jamas coverage_point), (2) exigir identified, (3) exigir finito.
- Via 1 (unit determinista): `test_coverage_lower_uses_upper_bound` (test_exhaustiveness.py:143-149) prueba coverage_lower == n_obs/ci_high exacto.
- Via 2 (invariante de servido): `test_mse_lower_bound_invariant_holds_everywhere` (test_api_exhaustiveness.py:48-59) -> coverage_lower<=coverage_point<=1 en CADA fila.
- Via 3 (adversarial): `test_not_falsely_sealed_when_coverage_below_threshold` (test_api_exhaustiveness.py:61-72) -> sealed ==> coverage_lower>=threshold.
- Via 4 (property-based, nivel inalcanzable): para TODO (n_obs,n_hat,ci_low,ci_high) generado con ci_high>=n_hat>=n_obs, asertar coverage_lower<=coverage_point y (sealed ==> coverage_lower>=threshold).

#### (f) Herramienta NEXT-LEVEL
- PRIMARIA: **in-toto** (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:643]. Emite una atestacion firmada que liga {git SHA, content-hashes de todo input} -> {coverage_lower, CI, N_hat por estrato}, anclada a un transparency log Sigstore/rekor. Convierte el sello de AFIRMACION a CERTIFICADO no-repudiable re-verificable por terceros sin confiar en nosotros -- el techo inalcanzable para un criterio de sello [VERIFIED NEXT-LEVEL.md:140-146].
- ADYACENTE: **dga** (Bayesian Model Averaging, GPL>=2) https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127] -- hace coverage_lower honesto ante la incertidumbre de seleccion-de-modelo (cuantil 2.5% del posterior promediado en vez de un solo modelo BIC), cerrando de raiz el riesgo "ci_high subestimado -> sello falso". **Great Expectations** (Apache-2.0) https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167] -- contrato de datos PRE-sello: el estrato falla CERRADO (rehusa sellar) cuando sus precondiciones estadisticas se violan.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 18 — Merge probabilistico Splink + resolucion locale-aware

> **Ficha 360**
>
> **Costura** — Normalizadores ES-shaped al atomo: _SUFFIX (splink_merge.py:31-34) hornea formas legales espanolas (S.L./S.A.U./S.C./C.B.); _fold (:47-51) ASCII-fold destructivo NFKD (ss-eszett->'', CJK->''); _digits (:74-78) toma ultimos-9-digitos (heuristica ES); block_on('municipality_code') (:165) asume INE 5-digit (migration 0001 CHAR(5)); name_prefix=nm[:4] (:107) asume script latino. DSN hardcodeado heredado de capture.py:17. El esqueleto Fellegi-Sunter + invariante never-finer-than-resolved (:198-219) es country-invariante.
>
> **Fix** — Insertar anyascii ANTES del fold en _norm_name; tabla de sufijos legales por pais en countries/<CC>/identity/legal_suffixes.txt (default-ES=actual); reemplazar _digits last-9 por python-phonenumbers E.164 (despachar ES al path actual para byte-identidad); reemplazar blocking name_prefix por blocking semantico LaBSE/BGE-M3 + pgvector ANN; parametrizar anchura de block_on('municipality_code') via geo pack schema. Todo degrada gracioso hoy (guard splink_available :37-44, fallback resolved); el peligro es perdida silenciosa de recall.
>
> **Adversarial** — JP (break #7): JaroWinkler+name_prefix sobre kanji/kana casi inutil, _fold colapsa CJK a '' -> over-merge de todos los dealers JP de un muni a UNA unidad o under-merge None; degrada SILENCIOSAMENTE (recall menor->m menor->CI ancho->nada sella). DE: nombres compuestos+eszett ('Weissenfels'->'weienfels'). FR/PT: diacriticos + 9-digit colisionando con ES bajo clave last-9. block_on('municipality_code') asume INE-5. Ruido: marketplaces con phone/website compartido over-mergean dealers distintos via ExactMatch.
>
> **Sellado** — Criterio: (1) ES byte-identidad (mismos clusters/claves sin re-key); (2) invariante never-finer (output Splink es refinamiento/superset de v_dealer_resolved, union-find con resolved lo impone :201-219); (3) recall lift medido con falso-merge ~0. Multi-via: unit goldens _norm_name/_host/_digits + union-find transitivo (test_exhaustiveness.py:188-202); ortogonal refinamiento/superset vs red determinista; regresion no-Latina (CJK no colapsa a '' ni over-merge); guard de contaminacion cross-pais (muni/geo blocking + single-country).
>
> **Herramienta NEXT-LEVEL** — PRIMARIA anyascii (ISC) https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:329,482]: transliterador sin deps que cierra el doble-fallo CRITICO de fold CJK/diacriticos (ss-eszett->ss, kanji->romaji), commercial-clean vs GPL unidecode. STACK locale-aware: libpostal (MIT) https://github.com/openvenues/libpostal [NEXT-LEVEL.md:345,474]; LaBSE (Apache-2.0) https://huggingface.co/sentence-transformers/LaBSE [:458] blocking semantico 109 idiomas; python-phonenumbers (Apache-2.0) https://github.com/daviddrysdale/python-phonenumbers [:466] E.164 ~250 regiones; python-stdnum (LGPL-2.1) https://github.com/arthurdejong/python-stdnum [:490]; Splink (MIT) https://github.com/moj-analytical-services/splink [:401,450] model.json certificable.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/exhaustiveness/splink_merge.py:37-44` -> `splink_available()` con `@lru_cache(maxsize=1)`: try `import splink` -> True/except->False [VERIFIED].
- `splink_merge.py:31-34` -> `_SUFFIX` regex: formas legales ESPANOLAS (s l u | s a u | s l l | s l | s a | s c p | s c | c b | sociedad limitada | sociedad anonima | unipersonal) [VERIFIED].
- `splink_merge.py:47-51` -> `_fold`: NFKD + descarta combining marks (ASCII-fold destructivo) [VERIFIED].
- `splink_merge.py:54-62` -> `_norm_name`: lower -> _fold -> _NONAL (puntuacion a espacio) -> colapsa WS -> _SUFFIX strip -> colapsa [VERIFIED].
- `splink_merge.py:65-71` -> `_host`: extrae hostname, quita www [VERIFIED].
- `splink_merge.py:74-78` -> `_digits`: quita no-digitos, toma los ULTIMOS 9 (`d[-9:] if len(d)>=9`) [VERIFIED].
- `splink_merge.py:81-116` -> `_load_dealers`: SELECT entity WHERE `kind::text IN DEALER_KINDS`; name=COALESCE(trade_name,legal_name); name_prefix=nm[:4] [VERIFIED].
- `splink_merge.py:119-123` -> `_resolved_map`: entity_ulid->resolved_ulid desde v_dealer_resolved [VERIFIED].
- `splink_merge.py:126-145` -> `_UF` union-find, raiz = id menor (determinista) [VERIFIED].
- `splink_merge.py:160-176` -> SettingsCreator dedupe_only; blocking `block_on('municipality_code','name_prefix')`, `block_on('phone')`, `block_on('website_host')`; comparisons `JaroWinklerAtThresholds('name',[0.92,0.82])` + ExactMatch muni/phone/website [VERIFIED].
- `splink_merge.py:180-189` -> training: estimate_probability_two_random_records_match, estimate_u_using_random_sampling(max_pairs=3_000_000), EM en muni+name_prefix y phone [VERIFIED].
- `splink_merge.py:198-219` -> UNION-find de la relacion Splink CON el resolved map (invariante never-finer-than-v_dealer_resolved) [VERIFIED].
- Importa `DEALER_KINDS, DSN` de capture (`capture.py:17` DSN HARDCODEADO `...cardeep_dev_only@localhost:5433...`; `capture.py:19-29` DEALER_KINDS) [VERIFIED].
- `tests/test_exhaustiveness.py:188-193` -> `_norm_name('AUTOMOCION del Oeste, S.L.')=='automocion del oeste'`, `_host('https://www.AutoX.es/stock')=='autox.es'`, `_digits('+34 911-22-33-44')=='911223344'`; `:196-202` union-find transitivo [VERIFIED].

#### (b) Mecanismo al atomo
La unidad de captura para el MSE debe ser el dealer FISICO; el dedup determinista (v_dealer_resolved) deja duplicados cross-source partidos -> m pequeno -> CI ancho -> nada sella (splink_merge.py:1-8). Splink aprieta el overlap via Fellegi-Sunter sobre DuckDB: el blocking genera pares candidatos (muni+PREFIJO de nombre de 4 chars, phone, website_host -- block on PREFIJO, no nombre completo, para que JaroWinkler puntue pares fuzzy de nombre completo DENTRO del bloque, :104-107,164-165); las comparisons puntuan cada par; EM entrena los pesos m/u DESDE LOS DATOS (:184-189); predict@0.9 -> cluster. Luego el invariante critico (:198-219): UNION de la relacion de equivalencia Splink con el resolved map via union-find, asi la unidad de captura es la componente conexa de AMBOS -> NUNCA mas fina que v_dealer_resolved (mas fina BAJARIA el overlap). Persiste discovery_splink_cluster, consumido por capture.build(unit='splink'). Guard de ausencia: splink_available() (:37-44) -> si Splink falta, el caller cae al resolved unit sin romper.

#### (c) Costura ES->generico + fix exacto
Los normalizadores estan ES-shaped AL ATOMO:
1. `_SUFFIX` (:31-34) hornea formas legales ESPANOLAS. DE GmbH/AG/UG, FR SARL/SAS, IT S.r.l./S.p.A., PT Lda./S.A. NO se quitan -> 'Mueller Autos GmbH' vs 'Mueller Autos' no normalizan-igual.
2. `_fold` (:47-51) es ASCII-fold DESTRUCTIVO via NFKD: aleman ss-eszett -> '' pierde 'ss' ('Strasse'->'strae'), y CJK kanji/kana -> '' (colapso total).
3. `_digits` (:74-78) toma ULTIMOS-9-digitos -- heuristica ES (numeros nacionales de 9 digitos); FR/PT tambien 9-digit -> falso-merge cross-border; DE/IT longitud variable -> clave equivocada.
4. `block_on('municipality_code')` (:165) asume el codigo INE de 5 digitos (migration 0001 municipality CHAR(5)); otros paises tienen otra anchura/forma.
5. name_prefix=nm[:4] (:107) asume script latino donde 4 chars discriminan; inutil para CJK.
Fix exacto:
- Insertar transliteracion **anyascii** ANTES del fold ASCII en _norm_name (y en el identity-path) -- no-destructiva (ss preservado, CJK->romaji).
- Reemplazar el regex `_SUFFIX` ES por una tabla de sufijos por pais en pack (countries/<CC>/identity/legal_suffixes.txt), default-ES=lista actual.
- Reemplazar el hack `_digits` last-9 por **python-phonenumbers** E.164 completo (consciente del calling-code), despachando ES al path actual para byte-identidad.
- Reemplazar el blocking name_prefix por blocking semantico multilingue (**LaBSE/BGE-M3** + pgvector ANN) -> recall country-proof sin listas de tokens por locale.
- Parametrizar la anchura de block_on('municipality_code') via el schema del geo pack (facet 18/20).
Todo degrada HOY de forma graciosa (guard :37-44, fallback a resolved); el peligro es perdida SILENCIOSA de recall, no un crash.

#### (d) Riesgo adversarial concreto
- JP (break #7): JaroWinkler+name_prefix sobre kanji/kana es casi inutil; _fold colapsa CJK a '' -> o over-merge de todos los dealers JP de un muni a UNA unidad, o under-merge None. Degrada SILENCIOSAMENTE (recall menor -> m menor -> CI ancho -> nada sella), sin excepcion.
- DE: nombres compuestos + eszett; 'Weissenfels'->'weienfels' under-merge.
- FR/PT: diacriticos + telefonos de 9 digitos colisionando con ES bajo la clave last-9.
- block_on('municipality_code') asume INE-5 -> mal-bloquea donde la forma del codigo muni difiere.
- Ruido: listings de marketplace con phone/website_host compartido pueden OVER-merge dealers distintos via el blocking phone/website + ExactMatch, arrastrando entidades no relacionadas a un cluster.

#### (e) Criterio de sellado + verificacion multi-via
- Criterio: (1) ES byte-identidad -- re-correr el merge sobre corpus ES da los mismos clusters/claves (sin re-key ES). (2) invariante never-finer -- el output Splink es refinamiento-o-superset de v_dealer_resolved, jamas parte un merge determinista (union-find con resolved lo impone, :201-219). (3) recall lift medido con falso-merge cerca de cero.
- Via 1 (unit): goldens _norm_name/_host/_digits (test_exhaustiveness.py:188-193); transitividad union-find (test:196-202).
- Via 2 (ortogonal): los clusters Splink deben ser relacion de refinamiento/superset con la red determinista (NEXT-LEVEL Splink verification).
- Via 3 (regresion no-Latina): un fixture CJK/cirilico NO debe colapsar a '' ni over-merge dealers distintos (anyascii verification).
- Via 4 (contaminacion cross-pais): cada par candidato pasa muni/geo blocking + invariante single-country.

#### (f) Herramienta NEXT-LEVEL
- PRIMARIA: **anyascii** (ISC) https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:329,482] -- transliterador data-driven sin dependencias que cierra el doble-fallo CRITICO de fold CJK/diacriticos nombrado en el riesgo (ss-eszett->ss, kanji->romaji), commercial-clean a diferencia del GPL unidecode [VERIFIED NEXT-LEVEL.md:479-485].
- STACK locale-aware (la elevacion completa): **libpostal** (MIT) https://github.com/openvenues/libpostal [VERIFIED NEXT-LEVEL.md:345,474] parser de direcciones estadistico multilingue (100+ paises) para normalizacion locale-aware de muni/direccion; **LaBSE** (Apache-2.0) https://huggingface.co/sentence-transformers/LaBSE [VERIFIED NEXT-LEVEL.md:458] blocking semantico de 109 idiomas reemplazando name_prefix, recall country-proof sin tuning por locale; **python-phonenumbers** (Apache-2.0) https://github.com/daviddrysdale/python-phonenumbers [VERIFIED NEXT-LEVEL.md:466] port de Google libphonenumber, E.164 completo para ~250 regiones reemplazando el hack last-9; **python-stdnum** (LGPL-2.1) https://github.com/arthurdejong/python-stdnum [VERIFIED NEXT-LEVEL.md:490] claves registrales/VAT validadas con digito de control (50 paises); **Splink** (MIT) https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:401,450] el propio motor ya cableado, cuya elevacion es el model.json exportable EM-entrenado como artefacto certificable auto-recalibrante.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 19 — Esquema de almacenamiento MSE + persistencia append-only

> **Ficha 360**
>
> **Costura** — Esquema SINGLE-TENANT: sin country_code en discovery_capture ni exhaustiveness_estimate (0048:36-44,55-74); province_code char(2) cabe ES INE pero trunca AGS DE 5-digit y colisiona ES '01'(Alava) con FR '01'(Ain) (break #1); v_exhaustiveness_seal (0048:82-106) es 'latest build GLOBAL' sin particion por pais (break #6); PK e indices (:43,46-49) single-tenant; DSN hardcodeado en migrate.py:15 y capture.py:17 (cardeep_dev_only). Las shapes y la mecanica append-only/idempotente (_persist DELETE-by-build seal.py:171-174, sentinelas :191-193) son reusables.
>
> **Fix** — ALTER discovery_capture/exhaustiveness_estimate ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES' (backfill byte-estable), ensanchar province_code char(2)->region_code text; anadir country_code a PK e indices y al DELETE/INSERT de _persist; migrar v_exhaustiveness_seal de 'latest global' a DISTINCT ON (country_code) ORDER BY country_code, created_at DESC en el MISMO cambio (facet 21); rollback country-scoped DELETE WHERE build_run_id AND country_code (sealing_hole #4); leer os.environ.get('CARDEEP_DSN') en migrate.py/capture.py como ya hace discover.py/harvest_dealer.py.
>
> **Adversarial** — Sentinelas enmascaran patologia: ci_high inf->1e18 y coverage nan->0 (seal.py:191-193) pueden hacer pasar un estrato degenerado por dato valido; una suma de n_hat podria arrastrar 1e18. ALTER ADD COLUMN DEFAULT 'ES' es byte-estable pero si la vista/endpoint (facet 21) no migra a latest-por-pais en el mismo cambio, pais #2 rompe servido silenciosamente (risk #8). Sin predicado country no hay DELETE limpio de solo-DE con Kreis truncados (sealing_hole #4). char(2) trunca codigos no-ES en el INSERT (DE 5-digit, FR '971' 3-char) antes del fix -> corrupcion.
>
> **Sellado** — Criterio: (1) idempotente (re-correr build_run_id reemplaza limpio, DELETE-by-build seal.py:171-174); (2) historia append-only preservada como serie temporal; (3) tras tenancy fix, build DE byte-aislado de ES y rollback borra solo DE. Multi-via: (1) aplicar 0048 dos veces -> schema inalterado, sha256 estable (migrate.py ON CONFLICT :31); (2) backfill country_code='ES' deja filas/vistas sin cambio; (3) escribir ES+DE -> vista devuelve ambos y DELETE country='DE' deja ES intacto; (4) re-correr build desde inputs hash-pineados reproduce coverage_lower byte-identico.
>
> **Herramienta NEXT-LEVEL** — PRIMARIA DVC (Apache-2.0) https://github.com/iterative/dvc [VERIFIED NEXT-LEVEL.md:151]: versionado content-addressed de los INPUTS del sello (census CSV, membresias de lista, matriz de captura) -> cada build_run_id reconstruible bit-a-bit; cierra el hueco de que append-only preserva OUTPUTS pero no un snapshot reproducible de INPUTS (sin lo cual la serie de coverage_lower para saturacion es drift disfrazado). ADYACENTE in-toto (Apache-2.0) https://github.com/in-toto/in-toto [:643] atesta inputs->outputs tamper-evident; OpenLineage (Apache-2.0) https://github.com/OpenLineage/OpenLineage [:159] linaje fuente->lista->bucket->estrato->nacional.

#### (a) Verificacion de code_hints [VERIFIED]
- `migrations/0048_discovery_capture.sql:22-28` -> `discovery_list` (list_key PK, orthogonality_class NOT NULL, description, is_orthogonal default true, created_at) [VERIFIED].
- `0048:36-44` -> `discovery_capture` (resolved_ulid, list_key REFERENCES discovery_list, province_code char(2), segment text, captured_at, build_run_id, **PRIMARY KEY (resolved_ulid, list_key, build_run_id)**) [VERIFIED].
- `0048:46-49` -> indices ix_discovery_capture_stratum(build_run_id,province_code,segment) y ix_discovery_capture_list(build_run_id,list_key) [VERIFIED].
- `0048:55-74` -> `exhaustiveness_estimate` (id bigserial PK, build_run_id, province_code char(2) NULL=>national, segment text NULL=>all, k_lists, n_obs, n_hat, ci_low, ci_high, coverage_point, coverage_lower, method, confidence, seal_threshold, sealed, external_ref, diagnostics jsonb, created_at) [VERIFIED].
- `0048:82-106` -> vista `v_exhaustiveness_seal` con WITH latest AS (SELECT build_run_id FROM exhaustiveness_estimate ORDER BY created_at DESC LIMIT 1) -- "latest build GLOBAL", SIN particion por pais [VERIFIED].
- `pipeline/exhaustiveness/seal.py:165-216` -> `_persist`: DELETE WHERE build_run_id (:171-174, idempotente); INSERT por seal (:180-198); SENTINELAS ci_high inf->1e18 (:191), coverage_point/lower nan->0.0 (:192-193); fila nacional province NULL segment NULL (:199-214) [VERIFIED].
- `pipeline/exhaustiveness/migrate.py:20-38` -> applier: read SQL, sha256 (:22), cur.execute(sql), INSERT schema_migrations(version,filename,sha256) ON CONFLICT (version) DO UPDATE (:27-35); DSN hardcodeado :15 [VERIFIED].

#### (b) Mecanismo al atomo
Append-only por build_run_id es el SUSTRATO temporal. Cada build escribe el conjunto completo de filas por-estrato + UNA fila nacional, llaveado por build_run_id; re-correr un build_run_id es idempotente porque _persist primero DELETEa ese build_run_id (:171-174) y re-inserta -> reemplazo limpio, no duplicado. La PK (resolved_ulid, list_key, build_run_id) (:43) hace la matriz de captura append-only entre builds: la misma entidad capturada por la misma lista en dos builds son dos filas, preservando la serie historica (el insumo del detector de saturacion, facet 24). Las SENTINELAS mapean valores no-finitos a doubles almacenables: ci_high inf->1e18 (estratos de lista unica), coverage nan->0.0 -- asi las columnas DOUBLE PRECISION NOT NULL nunca rechazan un estrato patologico. migrate.py registra la migracion con el sha256 del fichero en schema_migrations (el mismo contrato que toda migracion), asi el schema es content-addressed e idempotente (CREATE IF NOT EXISTS / CREATE OR REPLACE).

#### (c) Costura ES->generico + fix exacto
El esquema reusa las SHAPES verbatim pero es SINGLE-TENANT:
1. NO hay columna country_code en discovery_capture ni exhaustiveness_estimate (:36-44, :55-74). province_code es char(2) -- cabe ES INE '01'..'52' pero TRUNCA AGS aleman (5-digit) y colisionaria ES '01'(Alava) con FR '01'(Ain) en el MISMO estrato (break #1).
2. v_exhaustiveness_seal (:82-106) selecciona "latest build GLOBAL" -- correr build ES y luego DE hace que el servido muestre SOLO DE; ES desaparece (break #6).
3. La PK y los indices (:43,:46-49) asumen single-tenant; un build de pais #2 escribe en la misma tabla sin aislamiento.
4. DSN hardcodeado en migrate.py:15 y capture.py:17 (credencial cardeep_dev_only) -- bloquea correr contra cualquier DB no-default y arrastra la credencial dev a entornos no-dev.
Fix exacto (cirugia multi-tenancy, acoplada con facet 20):
- ALTER discovery_capture / exhaustiveness_estimate ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES' (backfill byte-estable), ensanchar province_code char(2)->region_code text.
- Anadir country_code a TODAS las PK e indices; enhebrarlo por el DELETE y el INSERT de _persist.
- Migrar v_exhaustiveness_seal de "latest global" a DISTINCT ON (country_code) ... ORDER BY country_code, created_at DESC en el MISMO cambio (facet 21) -- si no, pais #2 oculta a los demas silenciosamente.
- Rollback country-scoped: DELETE WHERE build_run_id AND country_code, para borrar limpio un build DE con Kreis truncados sin tocar ES (sealing_hole #4).
- Leer DSN de os.environ.get('CARDEEP_DSN') en migrate.py/capture.py (el resto del pipeline -discover.py/harvest_dealer.py- ya lo hace).

#### (d) Riesgo adversarial concreto
- Las sentinelas enmascaran patologia: ci_high inf->1e18 y coverage nan->0 (:191-193) pueden hacer que un estrato degenerado parezca dato valido aguas abajo; una query que sume n_hat podria arrastrar un 1e18 si una fila no-identificada se cuela en un roll-up.
- ALTER de tablas con datos: ADD COLUMN DEFAULT 'ES' es byte-estable, pero si la vista/endpoint (facet 21) no migra a 'latest por pais' en el MISMO cambio, pais #2 rompe el servido silenciosamente (risk #8).
- Sin predicado country no hay DELETE limpio de solo-DE si un build aleman escribe codigos Kreis truncados junto a filas ES (sealing_hole #4).
- char(2) province_code TRUNCA codigos no-ES en el propio INSERT (DE 5-digit, FR '971'-'976' 3-char) ANTES de que aterrice el fix de tenancy -> corrupcion en escritura.

#### (e) Criterio de sellado + verificacion multi-via
- Criterio: (1) idempotente -- re-correr un build_run_id reemplaza limpio (DELETE-by-build, :171-174). (2) historia append-only preservada -- build_run_ids distintos coexisten como serie temporal. (3) tras el fix de tenancy, un build DE byte-aislado de ES y rollback country-scoped borra solo DE.
- Via 1 (idempotencia de migracion): aplicar 0048 dos veces -> schema inalterado, sha256 estable (migrate.py ON CONFLICT, :31).
- Via 2 (ES byte-identidad): backfill country_code='ES' deja filas/vistas existentes sin cambio.
- Via 3 (aislamiento): escribir builds ES+DE -> v_exhaustiveness_seal devuelve AMBOS (uno por pais) y DELETE WHERE country='DE' deja ES intacto.
- Via 4 (reproducibilidad content-addressed, nivel inalcanzable): re-correr un build_run_id desde inputs hash-pineados reproduce coverage_lower byte-identico.

#### (f) Herramienta NEXT-LEVEL
- PRIMARIA: **DVC** (Apache-2.0) https://github.com/iterative/dvc [VERIFIED NEXT-LEVEL.md:151] -- versionado content-addressed de los INPUTS del sello (CSV de censo, tablas de membresia de lista, la matriz de captura materializada), asi cada build_run_id referencia hashes de contenido inmutables y es reconstruible bit-a-bit. Cierra el hueco exacto donde el append-only-por-build_run_id preserva los OUTPUTS pero NO un snapshot reproducible de INPUTS -- sin lo cual la serie temporal de coverage_lower (saturacion, facet 24) es drift disfrazado de medicion [VERIFIED NEXT-LEVEL.md:148-154].
- ADYACENTE: **in-toto** (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:643] -- atesta {code SHA + content-hashes de inputs}->{outputs}, tamper-evident. **OpenLineage** (Apache-2.0) https://github.com/OpenLineage/OpenLineage [VERIFIED NEXT-LEVEL.md:159] -- linaje extremo-a-extremo: coverage_lower trazable fuente->lista->bucket->estrato->nacional.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 20 — Contrato de test + barrido CI (matematica + pack + por-pais)

> **Ficha 360**
>
> **Costura** — Los tests de contrato-de-pack y API HORNEAN ES: test_exhaustiveness_triangulation_loaded.py asierta >=52 provincias, totales literales 5358/1292/24377 y vocabulario {compraventa,concesionario,desguace} (:22,49-53,76-82); test_api_seal.py/test_province_seal_view.py asumen el doble-sistema ES (52 prov, venta/desguace, umbrales 85/50). La asercion 'otros' NO fabricado (:66-69) codifica el scope-mismatch real (ancla excluye 'otros', n_hat_sum lo incluye, sealing_hole #5). La capa matematica (test:19-149) es country-invariante.
>
> **Fix** — Parametrizar el contrato del ancla en countries/<CC>/census/contract.yaml (expected_regions, national_totals_with_provenance, segment_vocab); onboardar pais = portar su contrato; CI lo corre para cada pack. Partir la suite en country-invariante (matematica, siempre) y por-pais (pack+API parametrizado). Tests country-proof fail-closed: source_key fuera del bucket map FALLA, region_code fuera de la rejilla FALLA, mismatch de segment_vocab FALLA. Anadir test de scope-mismatch (ancla scope==n_hat_sum scope o restar el delta 'otros').
>
> **Adversarial** — Pais con distinto numero de regiones (DE 401 Kreise, FR 101 departements, JP 47 prefecturas) falla los literales '>=52/==52' -- o peor, un pack parcial PASA porque nada asierta el conteo propio del pais. Totales literales 5358/1292/24377 ES-only; pack DE sin analogo FACONAUTO/DGT entra sin validar. Tests de API asumen el doble-sistema ES; regresion de tenancy (facet 20: vista latest-global ocultando pais #2) pasa silenciosa sin barrido API por-pais. Casos-borde locale (IT alfa, PT NNNN-NNN, JP 7-digit, CJK, JPY sobre techo) no cubiertos por goldens by-example (los 11 goldens ES nunca los ven).
>
> **Sellado** — Criterio: (1) cada invariante del sello tiene test CI (matematica+pack+API); (2) la capa matematica corre SIN DB (country-invariante) verde en cada push; (3) onboardar pais incluye portar su contrato de ancla, los tests invariantes quedan byte-identicos. Multi-via: (1) goldens matematicos = oraculo textbook/sintetico (test:19-149); (2) el ancla reconcilia sumas provincia->nacional (test_loaded:85-97); (3) API asierta cota-inferior no 100% fabricado (test_api_exh:48-72); (4) property-based genera inputs locale adversariales y congela contraejemplos como fixtures deterministas.
>
> **Herramienta NEXT-LEVEL** — PRIMARIA Hypothesis (MPL-2.0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320]: property-based convierte los goldens ES by-example en invariantes generados adversarialmente (coverage_lower<=coverage_point; N_hat>=n_obs; sealed==>coverage_lower>=threshold), sintetiza postcodes no-INE/CJK/precios sobre techo que los 11 goldens ES no ven, minimiza al contraejemplo y lo congela como fixture. ADYACENTE Schemathesis (MIT) https://github.com/schemathesis/schemathesis [:828] fuzz del /openapi.json; oasdiff (Apache-2.0) https://github.com/oasdiff/oasdiff [:836] gate de breaking-change; pandera (integra Hypothesis); ranx (MIT) https://github.com/AmenRa/ranx [:756].

#### (a) Verificacion de code_hints [VERIFIED]
- `tests/test_exhaustiveness.py` math units [VERIFIED]: chapman textbook :19-23 (N_hat~=592.24), CI brackets+floor :26-31, rechaza overlap imposible m>n1 :34-36; loglinear->Petersen :42-47, 3-list recupera N verdadero :66-73, dependencia-positiva ENSANCHA-no-sesga :76-90; dependence_robust :96-101 (low==n_obs, high>=0.9*N); dispatcher por k :107-120; sparse->unidentified :123-134, dense->identified :137-140; coverage_lower usa cota superior :143-149; R bridge skip-if-absent :155-185; splink normalisers+union-find :188-202; triangulation verdicts :208-214, carga CSV :217-227.
- `tests/test_exhaustiveness_vector_lists.py` [VERIFIED]: bucket_for V2-V6 :16-25, V3/V4 ortogonales :28-32, V5/V6 NO :35-39, metadata presente :42-47.
- `tests/test_exhaustiveness_triangulation_loaded.py` 8 tests del ancla :29-104 [VERIFIED]: ancla CSV+SOURCE.md presentes :29-37, >=52 anclas :40-45, las 52 provincias :48-55, segmentos dentro del vocabulario del sello + 'otros' NO fabricado :58-69, rollups nacionales (5358 FACONAUTO :77, 1292 DGT CAT :79, 24377 all-segment=CNAE451 23085+DGT 1292 :82) :72-82, sumas por-segmento provincia==nacional :85-97, no-negativos :100-104.
- `tests/test_api_exhaustiveness.py:24-72` [VERIFIED]: envelope+certificate_kind :25-32, grand-national coherente 0<=cov_lower<=cov_point<=1 :34-40, cuatro segmentos con provincias :42-46, invariante cota-inferior en TODA fila :48-59, NO falso-sellado si coverage<threshold :61-72.
- `tests/test_api_seal.py:23-61` [VERIFIED]: envelope ambos segmentos :24-32, venta dist suma 52 :34-36, venta nacional banda canonica 60-110 :38-41, desguace todo SELLADO :43-46, cada provincia verdict valido + consistencia ROUND PG :48-61.
- `tests/test_province_seal_view.py:57-131` (DB-gated) [VERIFIED]: ambos segmentos 52 provincias :59-63, verdicts en set fijo :65-67, venta umbrales 85/50 :69-82, desguace discovery-seal @100 :84-95, coverage_pct=num/den ROUND_HALF_UP :97-112, no-neg/positivo :114-117, venta canonica no-sobreconteo 60-110 :119-126, desguace found>=census :128-131.

#### (b) Mecanismo al atomo
La red de tests SELLA cada faceta volviendo cada invariante del sello una asercion ejecutable en CI, en TRES capas:
1. Matematica country-INVARIANTE (puro-Python, sin DB): los numeros que no se pueden equivocar -- Chapman reproduce el textbook 592.24 (test:19-23), log-lineal recupera N conocido a rel=0.03 (test:66-70), cota dependence-robust>=0.9*N con piso==n_obs (test:96-101), IDENT_CAP sparse->unidentified / dense->identified (test:123-140), y la keystone anti-maquillaje coverage_lower usa la cota SUPERIOR (test:143-149).
2. Contrato de PACK (dato por pais): el ancla presente y bien-formada -- >=52 anclas, las 52 provincias, segmentos dentro de {compraventa,concesionario,desguace} con 'otros' explicitamente NO fabricado (test_loaded:58-69), rollups nacionales EXACTOS a los totales publicados (5358 FACONAUTO, 1292 DGT, 24377=CNAE451 23085+DGT 1292), sumas de provincia reconcilian a nacional.
3. Contrato de API/servido: el envelope sirve la matematica de cota-inferior honestamente -- coverage_lower<=coverage_point<=1 en todas partes (test_api_exh:48-59), ninguna fila sellada con coverage_lower<threshold (:61-72), banda canonica como guard de regresion de sobre-conteo.

#### (c) Costura ES->generico + fix exacto
Los tests de contrato-de-pack y de API HORNEAN ES:
- test_..._loaded.py asierta >=52 provincias, los totales literales 5358/1292/24377, y el vocabulario {compraventa,concesionario,desguace} (test:22,49-53,76-82) -- un pais nuevo necesita su PROPIO contrato de ancla o el ancla entra mal-formada sin que CI lo note.
- test_api_seal.py / test_province_seal_view.py asumen el doble-sistema ES (52 provincias, venta/desguace, umbrales 85/50) -- sin barrido por-pais, una regresion de tenancy (facet 20) pasa silenciosa.
- La asercion 'otros' (test:66-69) codifica el SEAM real de scope-mismatch: el ancla EXCLUYE 'otros' (sin censo externo honesto) mientras el n_hat_sum del sello lo INCLUYE (sealing_hole #5) -- el test fija el lado del ancla pero NADA prueba el desplazamiento del veredicto nacional resultante.
Fix exacto:
- Parametrizar el contrato del ancla: reemplazar las constantes ES por una fixture de expectativas por pais (countries/<CC>/census/contract.yaml: expected_regions, national_totals_with_provenance, segment_vocab). Onboardar un pais = portar su contrato de ancla; CI corre el contrato para CADA pack instalado.
- Partir la suite en country-INVARIANTE (matematica, siempre corre) y por-pais (pack+API, parametrizado sobre packs instalados).
- Anadir los tests country-PROOF como fail-closed: un source_key fuera del bucket map FALLA el build (sin caida silenciosa a MKT), un region_code fuera de la anchura de la rejilla geo FALLA, mismatch de segment_vocab FALLA.
- Anadir el test de scope-mismatch: asertar que la triangulacion nacional compara like-for-like (scope del ancla == scope de n_hat_sum, o el delta 'otros' se resta explicitamente).

#### (d) Riesgo adversarial concreto
- Un pais con distinto numero de regiones (DE 401 Kreise, FR 101 departements, JP 47 prefecturas) falla los literales '>=52 provincias / ==52' -- o peor, un pack parcial PASA porque nada asierta el conteo esperado PROPIO del pais.
- Los totales literales (5358/1292/24377) son ES-only; un pack DE sin analogo FACONAUTO/DGT no tiene contrato de ancla -> el ancla entra sin validar.
- Los tests de API asumen el doble-sistema ES; una regresion de tenancy (facet 20: vista latest-global ocultando pais #2) pasa silenciosa por falta de barrido API por-pais.
- Casos-borde de locale/ruido (postcodes IT alfa, PT NNNN-NNN, JP 7-digit, titulos CJK, precios JPY sobre techo EUR) NO cubiertos por goldens by-example -- exactamente los modos de fallo CRITICAL/HIGH que los 11 goldens ES nunca ven.

#### (e) Criterio de sellado + verificacion multi-via
- Criterio: (1) cada invariante del sello tiene un test ejecutable en CI (matematica + pack + API). (2) la capa matematica corre SIN DB (puro-Python, country-invariante) y verde en cada push. (3) onboardar un pais incluye portar su contrato de ancla al barrido CI; los tests country-invariantes quedan byte-identicos.
- Via 1: los goldens matematicos SON el oraculo textbook/sintetico (test:19-149).
- Via 2: el contrato del ancla reconcilia sumas de provincia a totales nacionales independientemente (test_loaded:85-97).
- Via 3: los tests de API asertan que los numeros servidos obedecen la matematica de cota-inferior, no un 100% fabricado (test_api_exh:48-72).
- Via 4 (property-based, nivel inalcanzable): genera inputs adversariales de locale que los goldens omiten y congela los contraejemplos como fixtures de regresion deterministas.

#### (f) Herramienta NEXT-LEVEL
- PRIMARIA: **Hypothesis** (MPL-2.0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320] -- property-based testing convierte los goldens ES by-example en invariantes GENERADOS adversarialmente (coverage_lower<=coverage_point para TODO input; N_hat>=n_obs; sealed==>coverage_lower>=threshold; parse_money idempotente+currency-tagged; province valido-por-pais-o-escala). Hypothesis sintetiza los separadores mixtos, postcodes no-INE (IT alfa, PT NNNN-NNN, JP 7-dig), titulos CJK y precios sobre techo que los 11 goldens ES nunca ven, MINIMIZA al contraejemplo mas simple, y el caso hallado se congela como fixture de regresion determinista [VERIFIED NEXT-LEVEL.md:317-323].
- ADYACENTE (capa de contrato API): **Schemathesis** (MIT) https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828] -- fuzzing property-based del /openapi.json que FastAPI ya expone. **oasdiff** (Apache-2.0) https://github.com/oasdiff/oasdiff [VERIFIED NEXT-LEVEL.md:836] -- gate de breaking-change para que el contrato API quede generico entre paises. **pandera** (integra Hypothesis) -- el schema como el contrato que el fuzzer ataca; **ranx** (MIT) https://github.com/AmenRa/ranx [VERIFIED NEXT-LEVEL.md:756] para cualquier gate de eval de relevancia/calidad.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 21 — Roll-up nacional honesto + split certified/uncertified

> **Ficha 360**
>
> **Costura** — La logica honest-split (certified=identified, uncertified reportado aparte) es country-INVARIANTE y correcta; la costura es la AUSENCIA de tenencia. `identified` (seal.py:91) opera sobre `seals` de `read_patterns(build_run_id)` (seal.py:70); sin country_code en discovery_capture (faceta 20), un build de pais #2 hace que `n_hat_sum` (seal.py:96) sume N_hat a TRAVES de paises (sealing_hole #2). `compute()` (seal.py:50-58) no recibe country_code y la fila nacional persistida (seal.py:199-214) no lo lleva -> dos sellos nacionales colisionan en exhaustiveness_estimate.
>
> **Fix** — (1) Enhebrar `country_code` en compute(build_run_id, *, country_code, ...) y propagarlo a read_patterns(..., country_code=cc) (WHERE country_code=%s) y a _persist (fila nacional con country_code). (2) `identified`/`unidentified` no cambian de logica - quedan correctos una vez `seals` ya viene country-scoped. (3) Scope-match de la triangulacion nacional (cruza con F13): comparar el anchor (None,None) que excluye 'otros' contra un n_hat_sum restringido a los segmentos censados, no contra el n_hat_sum total con 'otros' (seal.py:147 hoy pasa el total). Depende de F20 para el schema; F6 aporta el threading de la firma y el persist keyed-by-country.
>
> **Adversarial** — DE/FR/IT/PT en DB compartida: ES+DE sin filtro de pais -> n_hat_sum (seal.py:96) suma estratos de ambos a un N_hat global sin sentido (sealing_hole #2). Ruido/sesgo de fuente: la adicion de varianzas (seal.py:103) asume independencia entre-estrato; provincias que comparten un marketplace dominante tienen varianzas correlacionadas -> nat_se subestima el ancho -> nat_ci_high estrecho -> nat_cov_lower infla la certificacion. PT/ecosistema delgado: casi todo cae a uncertified, n_obs_cert minusculo, certifica ~0% sin senal de 'datos delgados' vs '0% real' (cruza F23).
>
> **Sellado** — SELLADO nacional sii nat_cov_lower>=threshold (seal.py:138,211). Multi-via: (1) GOLDEN ES: roll-up reproduce n_obs_cert/n_hat_sum y el split byte-identico pre/post tenencia (cero regresion). (2) Invariante anti-maquillaje: n_obs_uncert reportado APARTE, nat_cov_lower solo con masa certificada. (3) Aislamiento cross-country: build DE no altera la fila nacional ES (n_hat_sum_ES invariante). (4) Composicion: nat_se/nat_ci_high reproducen el CI combinado analitico en estratos sinteticos con N conocido. (5) Monotonia: subir un ci_high de estrato solo puede BAJAR nat_cov_lower.
>
> **Herramienta NEXT-LEVEL** — dga / SparseMSE - censo externo VINCULANTE como margen-conocido (mejora #4, NEXT-LEVEL.md:132-138) [VERIFIED NEXT-LEVEL.md:135] GPL(>=2), EUR0, https://cran.r-project.org/package=dga. Inyecta el ancla censal como total marginal conocido (offset Poisson log(n_external)) -> estratos hoy uncertified obtienen N_hat por mecanismo INDEPENDIENTE -> traslada masa uncertified->certified sin inventar dato. Secundaria: in-toto (mejora #5, NEXT-LEVEL.md:140-146) [VERIFIED NEXT-LEVEL.md:143] Apache-2.0, https://github.com/in-toto/in-toto - atesta inputs->coverage_lower nacional en transparency log (numero no-repudiable).

#### (a) Codigo verificado
- [VERIFIED seal.py:91-92] `identified = [s for s in seals if s.estimate.identified]` y `unidentified = [s for s in seals if not s.estimate.identified]` - el universo se parte por el flag `estimate.identified` (que viene de IDENT_CAP, faceta 4).
- [VERIFIED seal.py:94-96] `n_obs_cert = sum(n_obs for identified)` (94), `n_obs_uncert = sum(n_obs for unidentified)` (95), `n_hat_sum = sum(n_hat for identified)` (96) -> el denominador certificado es la SUMA de N_hat SOLO sobre estratos identificados.
- [VERIFIED seal.py:98-103] varianzas entre-estrato SUMAN: `half_widths = [(ci_high - n_hat) for identified if isfinite]` (98-102), `nat_se = sqrt(sum((hw/1.96)**2))` (103) - asume independencia entre-estrato.
- [VERIFIED seal.py:104-107] `nat_ci_low = max(n_obs_cert, n_hat_sum - 1.96*nat_se)` (104), `nat_ci_high = n_hat_sum + 1.96*nat_se` (105), `nat_cov_point = n_obs_cert/n_hat_sum` (106), `nat_cov_lower = n_obs_cert/nat_ci_high` (107) - la cifra certificante usa la COTA SUPERIOR del CI compuesto.
- [VERIFIED seal.py:110-114] pooled national fit: agrega TODOS los patrones a un solo estimador, marcado UNRELIABLE (solo cross-check de heterogeneidad).
- [VERIFIED seal.py:130-143] el summary separa `national_certified` (scope "identified strata only (overlap pins N down)") de `uncertified` (note "denominator unknown (insufficient overlap) - NOT counted as covered").
- [VERIFIED seal.py:199-214] fila nacional persistida (province NULL, segment NULL), method "stratified_sum", `sealed = clow >= threshold` (211).

#### (b) Mecanismo al atomo
El sello nacional NO promedia ni interpola: descompone el pais en ~200 estratos (provincia x segmento), estima cada uno por captura-recaptura, y SOLO SUMA los que el overlap permite fijar (identified). La masa observada-pero-no-identificable (`n_obs_uncert`) se aparta: su denominador verdadero es DESCONOCIDO, asi que plegarla como "100% cubierta" inflaria la cobertura nacional - la doctrina anti-maquillaje (seal.py:84-90, comentario) lo prohibe estructuralmente. La certificacion nacional es exactamente `n_obs_cert / nat_ci_high`: como `nat_ci_high = n_hat_sum + 1.96*nat_se` crece con cualquier sobre-estimacion de N_hat, sobre-estimar SOLO puede BAJAR la cobertura certificada, jamas subirla falsamente (la propiedad de seguridad central del sello). La suma de varianzas (`nat_se`) es la composicion correcta bajo independencia entre-estrato; el pooled-fit existe como termometro de cuanto se viola esa independencia.

#### (c) Costura ES->generico
La logica honest-split es country-INVARIANTE y correcta tal cual; la costura es la AUSENCIA de tenencia, no la matematica. `identified` (seal.py:91) opera sobre `seals` que vienen de `read_patterns(build_run_id)` (seal.py:70) - sin columna country en discovery_capture (faceta 20), un build de pais #2 escribe en la misma tabla y `n_hat_sum` (seal.py:96) sumaria N_hat a TRAVES de paises (sealing_hole #2). Ademas `compute()` (seal.py:50-58) no recibe country_code y la fila nacional persistida (seal.py:199-214) no lo lleva, asi que dos sellos nacionales colisionan en `exhaustiveness_estimate`.

#### (d) Riesgo adversarial
- (DE/FR/IT/PT en DB compartida) Correr ES y luego DE sin filtro de pais hace que `n_hat_sum` (seal.py:96) sume estratos de ambos paises a un N_hat "global" sin sentido y `nat_cov_lower` mezcle denominadores de dos jurisdicciones (sealing_hole #2).
- (ruido/sesgo de fuente) La adicion de varianzas (seal.py:103) asume independencia entre-estrato; si en un pais nuevo varias provincias comparten el MISMO sesgo de fuente (un unico marketplace dominante visto en todas), las varianzas estan correlacionadas y `nat_se` SUBESTIMA el ancho real -> `nat_ci_high` muy estrecho -> `nat_cov_lower` infla la certificacion nacional.
- (PT/ecosistema delgado) Si casi todo cae a uncertified, `n_obs_cert` es minusculo y el pais certifica ~0% sin senal de que es "datos delgados" y no "0% real" (cruza con F23).

#### (e) Criterio de sellado + verificacion multi-via
SELLADO nacional sii `nat_cov_lower >= threshold` (seal.py:138,211).
1. GOLDEN ES - el roll-up reproduce `n_obs_cert/n_hat_sum` y el split certified/uncertified byte-identico antes/despues del refactor de tenencia (cero regresion).
2. Invariante anti-maquillaje - test que asserta que `n_obs_uncert` se reporta APARTE y que `nat_cov_lower` se computa SOLO con masa certificada (nunca con n_obs_uncert).
3. Aislamiento cross-country - DB sintetica 2-paises: construir DE NO debe alterar la fila nacional de ES (`n_hat_sum_ES` invariante).
4. Propiedad de composicion - sobre estratos sinteticos con N conocido, `nat_se` y `nat_ci_high` reproducen el CI combinado analitico.
5. Monotonia cota-superior - perturbar al alza un `ci_high` de estrato solo puede BAJAR `nat_cov_lower`.

#### (f) Herramienta NEXT-LEVEL
**dga / SparseMSE - censo externo VINCULANTE como margen-conocido** (mejora #4, NEXT-LEVEL.md:132-138) [VERIFIED NEXT-LEVEL.md:135] GPL(>=2), EUR0, https://cran.r-project.org/package=dga. Eleva el split certified/uncertified: inyecta el ancla censal como TOTAL MARGINAL CONOCIDO (offset Poisson log(n_external)) en el ajuste, de modo que estratos hoy uncertified (fallan IDENT_CAP) obtienen N_hat fijado por un mecanismo INDEPENDIENTE (registro/fiscal) -> traslada masa uncertified->certified SIN inventar dato, subiendo el denominador defendible. Secundaria: **in-toto** (mejora #5, NEXT-LEVEL.md:140-146) [VERIFIED NEXT-LEVEL.md:143] Apache-2.0, https://github.com/in-toto/in-toto - atesta {git SHA + content-hashes de inputs} -> {coverage_lower nacional} en un transparency log (Sigstore/rekor), convirtiendo el numero nacional de afirmacion a CERTIFICADO no-repudiable re-verificable por terceros.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 22 — Artefacto censo externo + contrato de provenance

> **Ficha 360**
>
> **Costura** — Artefacto PACK horneado a ES en tres puntos: (1) filename literal `dirce_cnae451.csv` (triangulation.py:27) miente la provenance para cualquier pais (break #10) y CENSUS_DIR/DEFAULT_CSV se bindean a ES en import-time (triangulation.py:32-33); (2) vocabulario de segmentos del CSV {compraventa,concesionario,desguace} es la taxonomia DGT/CNAE espanola; (3) mismatch de scope ESTRUCTURAL: el ancla (None,None) excluye 'otros' (SOURCE.md:123-124) pero seal.compute (seal.py:147) compara n_hat_sum que SI incluye estratos 'otros' (sealing_hole #5).
>
> **Fix** — (1) Renombrar CENSUS_CSV_NAME a un neutro `census.csv`; la provenance vive en countries/<CC>/census/SOURCE.md propio, no en el filename. (2) census_dir(country_code) (paths.py:50-52) y load_external_census(country_code=cc) (triangulation.py:36-50) ya son parametricos - falta que el orquestador pase country_code (F25) y retirar/resolver-por-pais el bind import-time CENSUS_DIR/DEFAULT_CSV (triangulation.py:32-33). (3) Scope-match (F6): comparar (None,None) contra n_hat de los segmentos censados, o emitir ancla 'otros' si el pais tiene censo. (4) Portar el CONTRATO: cada pais aporta su SOURCE.md con [MEDIDO]/[ESTIMADO DECLARADO] y test de ancla; nunca fabricar fila.
>
> **Adversarial** — DE/FR/IT/PT: no existe analogo CNAE-451/FACONAUTO/DGT-CAT - DE Handelsregister+KBA, FR SIRENE+registre, IT Registro Imprese; segmentos y fuentes distintos (break #10). Lector descuidado: compraventa/concesionario ES son [ESTIMADO DECLARADO] (apportionment ratio 0.2605/poblacion, SOURCE.md:65-69,84-86), NO medidos por provincia; tomarlos como techo MEDIDO es sobre-confianza (risk #5). No-UE (JP/MX): sin equivalente, forzar la rejilla de 3 segmentos importa ontologia ajena; fabricar filas rompe la doctrina anti-fabricacion (SOURCE.md:29-33).
>
> **Sellado** — (1) Contrato de 8 tests del ancla (test_exhaustiveness_triangulation_loaded.py): >=52 anclas, vocabulario de segmentos, roll-ups nacionales consistentes, sin negativos, 'otros' no fabricado. (2) Cada cifra del SOURCE.md trazable a formula+URL+tag MEDIDO/ESTIMADO. (3) Cross-check decomposicion: 451+452+453+454=88,621=division-45 (SOURCE.md:55-57) y compraventa+concesionario=venta sin clamping (SOURCE.md:97). (4) Triangulacion ratio en 0.7-1.4 (triangulation.py:75-80). (5) Por pais: contrato de ancla propio en CI (F26).
>
> **Herramienta NEXT-LEVEL** — Panel de anclas MULTIPLES - Eurostat SBS (NEXT-LEVEL.md:188-194) [VERIFIED NEXT-LEVEL.md:191] Reutilizacion libre (Decision 2011/833/EU; atribucion), EUR0, https://ec.europa.eu/eurostat/web/structural-business-statistics: eleva el ancla UNICA a un PANEL por pais (NACE G45.1); consistencia con la banda MAYORITARIA, el desacuerdo = senal de distrust. Complemento dia-uno: GLEIF LEI Golden Copy (NEXT-LEVEL.md:172-178) [VERIFIED NEXT-LEVEL.md:175] CC0 1.0, EUR0, https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy - espina registral global, refresco diario. Pack auto-verificado: Frictionless Framework (NEXT-LEVEL.md:337) [VERIFIED NEXT-LEVEL.md:337] MIT, EUR0, https://github.com/frictionlessdata/frictionless-py - Table Schema valida el CSV como contrato de datos por pais.

#### (a) Codigo/data verificado
- [VERIFIED countries/ES/census/dirce_cnae451.csv:1] header `province_code,segment,n_external`; filas `01,compraventa,85` / `01,concesionario,37` / `01,desguace,9` (provincia INE char(2) x 3 segmentos censados).
- [VERIFIED SOURCE.md:16-29] cada cifra etiquetada [MEDIDO] (conteo directo) o [ESTIMADO DECLARADO] (apportionment de un total nacional real via ratio publicado): compraventa/concesionario = [ESTIMADO DECLARADO] (26-27), desguace = [MEDIDO] (28), 'otros' = OMITIDO (29, "no honest EUR0 census found -> no anchor emitted").
- [VERIFIED SOURCE.md:59-61] `ratio_451/45 = 23,085/88,621 = 0.2605`; `venta_prov = round(cnae45_prov * 0.2605)`.
- [VERIFIED SOURCE.md:75] FACONAUTO = 5,358 instalaciones (concesionario universe); [VERIFIED SOURCE.md:103] DGT CAT = 1,292 (desguace, MEDIDO, per-provincia, query verificada a 52 filas).
- [VERIFIED SOURCE.md:116-121] anclas nacionales: (,compraventa)=17,362 / (,concesionario)=5,358 / (,desguace)=1,292 / (,)=24,377.
- [VERIFIED SOURCE.md:123-127] el ancla all-segment (None,None)=24,377 EXCLUYE deliberadamente 'otros' -> es techo sobre los tres segmentos censados, NO sobre el N_hat total que tambien suma estratos 'otros'.
- [VERIFIED triangulation.py:27] `CENSUS_CSV_NAME = "dirce_cnae451.csv"` - filename ES-especifico aunque el comentario (26) lo declara "country-agnostic"; [VERIFIED triangulation.py:32-33] `CENSUS_DIR/DEFAULT_CSV` se bindean a ES en import-time.

#### (b) Mecanismo al atomo
El censo es la UNICA verdad externa que puede refutar el N_hat: construido por un mecanismo DISTINTO al scrape (registro fiscal/asociativo), provincia x segmento, con cada cifra honestamente etiquetada medida-vs-declarada. La doctrina anti-fabricacion es el corazon: donde no hay censo EUR0 honesto ('otros'), NO se escribe fila - el seam reporta `no_anchor` (triangulation.py:73) en vez de inventar un numero. El SOURCE.md no es documentacion decorativa: es el CONTRATO de provenance que liga cada n_external a una formula + URL + tag, con procedimiento de refresco (SOURCE.md:130-140). La decomposicion es internamente consistente por construccion: `compraventa = max(0, venta - concesionario)` (SOURCE.md:91), y 451(23,085)+DGT(1,292)=24,377 = techo registral (SOURCE.md:121); cross-check 451+452+453+454=88,621=division-45 (SOURCE.md:55-57).

#### (c) Costura ES->generico
El artefacto es PACK (cero codigo) pero esta horneado a ES en tres puntos: (1) el filename literal `dirce_cnae451.csv` (triangulation.py:27) miente la provenance para cualquier pais (break #10); (2) el vocabulario de segmentos del CSV {compraventa,concesionario,desguace} es la taxonomia DGT/CNAE espanola; (3) el mismatch de scope ESTRUCTURAL - el ancla (None,None) excluye 'otros' (SOURCE.md:123-124) pero `seal.compute` (seal.py:147) compara `n_hat_sum` que SI incluye estratos 'otros' (sealing_hole #5), desplazando el veredicto nacional en paises cuya cuota 'otros' difiera de ES.

#### (d) Fix exacto
1. Renombrar `CENSUS_CSV_NAME` a un neutro `census.csv` (o `dealer_census.csv`); la provenance vive en el `countries/<CC>/census/SOURCE.md` propio de cada pais, no en el filename.
2. `census_dir(country_code)` (paths.py:50-52) ya resuelve el dir per-pais y `load_external_census(country_code=cc)` (triangulation.py:36-50) ya es parametrico - solo falta que el orquestador pase country_code (cruza con F25) y retirar el bind import-time de `CENSUS_DIR/DEFAULT_CSV` a ES (triangulation.py:32-33) o resolverlos por pais.
3. Scope-match (cruza con F6): comparar el ancla (None,None) contra el n_hat de los tres segmentos censados, o emitir un ancla 'otros' cuando el pais tenga censo para ello.
4. Portar el CONTRATO: cada pais aporta su propio SOURCE.md con sus [MEDIDO]/[ESTIMADO DECLARADO] y su test de ancla; NUNCA fabricar una fila para rellenar la rejilla.

#### (e) Riesgo adversarial
- (DE/FR/IT/PT) No existe analogo CNAE-451/FACONAUTO/DGT-CAT - DE usa Handelsregister + KBA, FR usa SIRENE + registre, IT usa Registro Imprese; el vocabulario de segmentos y las fuentes son otros (break #10).
- (ruido/lector descuidado) compraventa/concesionario ES son [ESTIMADO DECLARADO] (apportionment por ratio 0.2605 / poblacion), NO medidos por provincia (SOURCE.md:65-69, 84-86); un consumidor que los tome como techo MEDIDO sobre-confia en una banda modelada (risk #5).
- (no-UE) En JP/MX no hay equivalente y forzar la rejilla de 3 segmentos importa una ontologia ajena; fabricar filas por completar la grid rompe la doctrina anti-fabricacion (SOURCE.md:29-33).

#### (e/f) Criterio de sellado + verificacion multi-via
1. Contrato de 8 tests del ancla (test_exhaustiveness_triangulation_loaded.py) - >=52 anclas, vocabulario de segmentos, roll-ups nacionales consistentes, sin negativos, 'otros' no fabricado.
2. Cada cifra del SOURCE.md trazable a formula+URL+tag [MEDIDO]/[ESTIMADO DECLARADO].
3. Cross-check de la decomposicion nacional: 451(23,085)+452+453+454=88,621=division-45 (SOURCE.md:55-57) y compraventa+concesionario=venta por provincia sin clamping (SOURCE.md:97).
4. Triangulacion ratio en banda 0.7-1.4 (triangulation.py:75-80).
5. Por pais: su PROPIO contrato de ancla portado al barrido CI (cruza con F26).

#### (f) Herramienta NEXT-LEVEL
**Panel de anclas de triangulacion MULTIPLES - Eurostat SBS** (NEXT-LEVEL.md:188-194) [VERIFIED NEXT-LEVEL.md:191] Reutilizacion libre (Decision 2011/833/EU; atribucion), EUR0, https://ec.europa.eu/eurostat/web/structural-business-statistics. Eleva el ancla UNICA ES a un PANEL de denominadores independientes por pais (Eurostat SBS NACE G45.1 conteo de establecimientos); el sello debe ser consistente con la banda MAYORITARIA, no con un CSV; el DESACUERDO entre anclas se vuelve senal de distrust, no promedio silencioso. Complemento dia-uno para CUALQUIER pais: **GLEIF LEI Golden Copy** (NEXT-LEVEL.md:172-178) [VERIFIED NEXT-LEVEL.md:175] CC0 1.0 (dominio publico, comercial OK, sin atribucion), EUR0, https://www.gleif.org/en/lei-data/gleif-golden-copy/download-the-golden-copy - espina registral CC0 global, refresco diario, sin escribir adaptador de registro nacional. Para hacer el PACK auto-verificado: **Frictionless Framework** (NEXT-LEVEL.md:337) [VERIFIED NEXT-LEVEL.md:337] MIT, EUR0, https://github.com/frictionlessdata/frictionless-py - Table Schema que valida el CSV de censo (tipos, rangos, vocabulario de segmentos) como contrato de datos por pais.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 23 — Llave de estrato multi-tenant (country_code + region text)

> **Ficha 360**
>
> **Costura** — ES-binding estructural, no de logica: (1) province_code char(2) (0048:39,58) trunca AGS aleman 5-dig, DOM frances '971'-'976' 3-char, y colisiona ES'01'(Alava)/FR'01'(Ain) en el mismo estrato (break #1); (2) compute() sin country_code (seal.py:50-58) -> la orquestacion no puede pasar pais (F25, break #2); (3) read_patterns sin country (capture.py:160-167) -> dos paises mezclan patrones; (4) v_exhaustiveness_seal latest-global (0048:82-88) -> el ultimo build oculta el sello de los demas (F21); (5) load_external_census defaultea a ES (triangulation.py:38, paths.py:22).
>
> **Fix** — Migracion unica additive + backfill: ALTER TABLE discovery_capture ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES'; ALTER COLUMN province_code TYPE text (rename -> region_code); PK (country_code, resolved_ulid, list_key, build_run_id) e indices con country_code prefijo; identico en exhaustiveness_estimate. Firmas: compute(build_run_id, *, country_code, ...) y read_patterns(build_run_id, *, country_code, ...) con WHERE country_code=%s; _persist escribe country_code en cada fila + la nacional. v_exhaustiveness_seal -> DISTINCT ON (country_code) ... ORDER BY country_code, created_at DESC (F21). region_code = ISO 3166-2 text. Rollback: DELETE WHERE country_code=:cc AND build_run_id=:id.
>
> **Adversarial** — DE: AGS Kreis 5-dig / 16 Bundeslander no caben en char(2) -> truncamiento silencioso; FR: DOM '971'-'976' 3-char truncados, ES'01' colisiona con FR'01' (break #1). IT 107 / JP 47 / MX 32: cardinalidad y ancho de codigo propios; caps ES-calibrados (MAX<52) misfire. Migracion: ADD COLUMN DEFAULT 'ES' byte-estable, PERO si vistas/endpoint (F21) no migran a 'latest por pais' en el MISMO cambio, rompen silenciosamente al entrar pais #2 (risk #8). Rollback: sin predicado country, un build DE con codigos Kreis truncados junto a ES no se borra limpio (sealing_hole #4).
>
> **Sellado** — (1) GOLDEN ES: ADD COLUMN DEFAULT 'ES' + widen deja el build ES byte-estable (mismos seals, misma fila nacional, mismo coverage_lower). (2) Aislamiento 2-paises: build DE escribe SOLO country_code='DE'; DELETE WHERE country_code='DE' borra exactamente esas filas, ES intacto. (3) Serving cross-pais: tras build DE, v_exhaustiveness_seal sigue devolviendo el sello ES (DISTINCT ON country_code). (4) Sin truncamiento: region_code text round-trips Kreis 5-char / DOM 3-char. (5) Caps country-proof: caps derivados de ISO 3166-2 reproducen el cap ES (52) y casan DE/FR/IT/JP/MX.
>
> **Herramienta NEXT-LEVEL** — pycountry - ISO 3166-2 subdivision authority (NEXT-LEVEL.md:527-533) [VERIFIED NEXT-LEVEL.md:530] LGPL-2.1, EUR0, https://github.com/pycountry/pycountry. Eleva region_code text y los caps ES-calibrados a DATOS auto-pineados: conteo y ancho-de-codigo de subdivisiones de primer nivel de cada pais (DE 16, FR 101, IT 107, MX 32, JP 47, ES 52) salen del dataset iso-codes, alimentando un seal-manifest por pais (geo_unit_width, KNOWN_REAL_MAX_*) en vez de sentinelas Spain-shaped. Uso build/config-time (no hot-path) -> LGPL no-issue; alternativa estricta-permisiva: iso3166 (MIT, countries-only) + JSON crudo de iso-codes para subdivisiones (NEXT-LEVEL.md:531) [VERIFIED NEXT-LEVEL.md:531].

#### (a) Codigo verificado
- [VERIFIED 0048_discovery_capture.sql:39] `province_code char(2)` en discovery_capture (stratum dim 1); [VERIFIED :58] `province_code char(2)` en exhaustiveness_estimate - NINGUNA columna country en ninguna tabla.
- [VERIFIED 0048:43] PK `(resolved_ulid, list_key, build_run_id)` - sin country; [VERIFIED :46-47] indice de estrato `(build_run_id, province_code, segment)` - sin country.
- [VERIFIED 0048:82-88] `v_exhaustiveness_seal` = "latest build GLOBAL" (`ORDER BY created_at DESC LIMIT 1`) - sin particion por pais.
- [VERIFIED seal.py:50-58] `compute(build_run_id, *, dsn, threshold, include_mkt, r_crosscheck, external_census)` - SIN parametro country_code; [VERIFIED seal.py:68-69] `external_census = triangulation.load_external_census()` auto-carga el censo ES por defecto.
- [VERIFIED capture.py:160-167] `read_patterns(build_run_id, *, dsn, include_mkt, province_code, segment)` - filtra province/segment pero SIN country.
- [VERIFIED paths.py:22] `DEFAULT_COUNTRY = "ES"`; [VERIFIED triangulation.py:38] `load_external_census(path=None, country_code=DEFAULT_COUNTRY)` - la firma ya es parametrica pero defaultea a ES.

#### (b) Mecanismo al atomo
La tenencia es la dimension EXTERNA del estrato que hoy no existe en NINGUNA tabla. El estrato real es (country_code, region_code, segment) pero el schema solo modela (province_code char(2), segment): un build de pais #2 escribiria en `discovery_capture`/`exhaustiveness_estimate` sin aislamiento, y como province_code es CHAR(2) cualquier codigo no-ES de >2 chars se TRUNCA. Peor: ES '01' (Alava) y FR '01' (Ain) colisionan en el MISMO estrato (break #1). La cirugia es ATOMICA - schema + lectura + escritura + rollback en UN cambio - porque hoy la dimension pais no existe en ninguna capa y dos paises colisionan estructuralmente. Backfill `country_code='ES'` es byte-estable (ADD COLUMN DEFAULT 'ES' no reescribe los datos ES).

#### (c) Costura ES->generico
Todo el ES-binding es estructural, no de logica: (1) `province_code char(2)` (0048:39,58) trunca AGS aleman 5-dig, DOM frances '971'-'976' 3-char, y colisiona ES'01'/FR'01'; (2) `compute()` sin country_code (seal.py:50-58) -> la orquestacion no puede pasar pais (cruza con F25, break #2); (3) `read_patterns` sin country (capture.py:160-167) -> dos paises mezclan patrones; (4) `v_exhaustiveness_seal` latest-global (0048:82-88) -> el ultimo build oculta el sello de los demas paises (cruza con F21); (5) `load_external_census` defaultea a ES (triangulation.py:38, paths.py:22).

#### (d) Fix exacto
Migracion unica additive + backfill: `ALTER TABLE discovery_capture ADD COLUMN country_code char(2) NOT NULL DEFAULT 'ES'`, `ALTER ... ALTER COLUMN province_code TYPE text` (rename logico -> region_code), recomponer PK `(country_code, resolved_ulid, list_key, build_run_id)` e indices con country_code prefijo; identico en exhaustiveness_estimate. Firmas: `compute(build_run_id, *, country_code, ...)` (seal.py) y `read_patterns(build_run_id, *, country_code, ...)` (capture.py) con `WHERE country_code=%s`; `_persist` escribe country_code en cada fila + la nacional. `v_exhaustiveness_seal` -> `DISTINCT ON (country_code) ... ORDER BY country_code, created_at DESC` (cruza con F21). region_code vocabulario = ISO 3166-2 text en vez de CHAR(2) INE. Rollback: `DELETE WHERE country_code=:cc AND build_run_id=:id`.

#### (e) Riesgo adversarial
- (DE) AGS de Kreis 5-dig / 16 Bundeslander no caben en char(2) -> truncamiento silencioso; (FR) DOM '971'-'976' 3-char truncados, y ES'01'(Alava) ≡ FR'01'(Ain) colisionan en el mismo estrato (break #1).
- (IT 107 province / JP 47 prefecturas / MX 32 estados) cada pais tiene cardinalidad y ancho de codigo propios; los caps ES-calibrados (MAX < 52) misfire.
- (riesgo de migracion) ADD COLUMN DEFAULT 'ES' es byte-estable, PERO si las vistas/endpoint (F21) no migran a "latest por pais" en el MISMO cambio, romperian silenciosamente al entrar pais #2 (risk #8).
- (rollback) Sin predicado country, un build DE que escribio codigos Kreis truncados junto a filas ES no se puede borrar limpio (sealing_hole #4).

#### (e) Criterio de sellado + verificacion multi-via
1. GOLDEN ES - `ADD COLUMN DEFAULT 'ES'` + widen deja el build ES byte-estable (mismos seals, misma fila nacional, mismo coverage_lower).
2. Aislamiento 2-paises - build DE con codigos Kreis escribe SOLO country_code='DE'; `DELETE WHERE country_code='DE'` borra exactamente esas filas, ES intacto.
3. Serving cross-pais - tras un build DE, `v_exhaustiveness_seal` sigue devolviendo el sello ES (DISTINCT ON country_code).
4. Sin truncamiento - region_code text round-trips un Kreis 5-char / DOM 3-char sin perdida.
5. Caps country-proof - los caps por pais derivados de ISO 3166-2 reproducen el cap ES (52) y casan DE/FR/IT/JP/MX independientemente.

#### (f) Herramienta NEXT-LEVEL
**pycountry - ISO 3166-2 subdivision authority** (NEXT-LEVEL.md:527-533) [VERIFIED NEXT-LEVEL.md:530] LGPL-2.1, EUR0, https://github.com/pycountry/pycountry. Eleva el region_code text y los caps ES-calibrados a DATOS auto-pineados: el conteo y ancho-de-codigo de las subdivisiones de primer nivel de CADA pais (DE 16, FR 101, IT 107, MX 32, JP 47, ES 52) salen del dataset estandar iso-codes, alimentando un seal-manifest por pais (geo_unit_width, KNOWN_REAL_MAX_*) en vez de sentinelas Spain-shaped que misfire para todo pais no-ES. Uso build/config-time (no hot-path), asi LGPL es no-issue; alternativa estricta-permisiva: **iso3166** (MIT, countries-only) + el JSON crudo de iso-codes para subdivisiones (NEXT-LEVEL.md:531) [VERIFIED NEXT-LEVEL.md:531].

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 24 — Canal R de verificacion ortogonal (Rcapture + LCMCR)

> **Ficha 360**
>
> **Costura** — La matematica del canal R ya es pais-agnostica (consume freqs, cero literales ES); la costura es el ENTORNO. _R_CANDIDATES (estimators_r.py:29-33), _RHOME_CANDIDATES (:36-39) y _RTOOLS_BIN (:40) hardcodean rutas de la maquina del owner (C:\Users\elias\R-portable, C:\Program Files\R\R-4.6.0, C:\rtools45) [VERIFIED]; en CI o cualquier otro host resuelven a nada => r_available()=False => la 2a via se evapora en silencio para TODO pais, ES incluido. Ademas crosscheck es advisory (seal.py:78-81 solo escribe diagnostics), nunca vincula el sello.
>
> **Fix** — Leer entorno ANTES de los candidatos hardcodeados: os.environ.get('CARDEEP_RSCRIPT')/R_HOME/RTOOLS_BIN como primer candidato en r_executable() y _configure_r_env(), espejando discover.py/harvest_dealer.py que ya usan os.environ.get('CARDEEP_DSN'). Instalar R en CI (imagen rocker o setup-r action) para que el puente este VIVO. Pinear Rcapture/LCMCR/SparseMSE en un lockfile renv. Hacer el crosscheck VINCULANTE al menos como downgrade: agree=False debe degradar confidence y aflorar en el veredicto nacional, no quedar en el jsonb diagnostics.
>
> **Adversarial** — DE/FR/IT/PT (fuentes delgadas) es donde mas importa la 2a via y donde hoy esta dormida (risk #6): el pais certifica sin confirmacion independiente y nadie lo nota porque la ausencia es graciosa. crosscheck detecta divergencia (agree=False) pero NO bloquea => estrato con 2x de desacuerdo se sella igual. Rutas hardcodeadas rompen en host no-owner (sello no-verificado indistinguible del verificado). maxorder=2 (mse.R:35) es punto-ciego compartido Python+Rcapture: dependencia de 3 listas no se modela en ninguno y el crosscheck verde no significa nada. Ruido: par marketplace-espejo fingiendo ortogonalidad => ambos comen el mismo freqs falso => crosscheck verde, sello falso.
>
> **Sellado** — Sello de la faceta: 2a via VIVA en CI (r_available()=True en el host) Y VINCULANTE (agree=False degrada confidence + aflora al veredicto). Multi-via: (1) test_r_bridge_recovers_known_n (tests:155-165) rcapture recupera N=1000 rel0.05 + crosscheck agree=True, hoy SKIP sin R; (2) test_r_crosscheck_flags_divergence (tests:180-185) fake 5000 vs 1000 => agree=False, UNICO test R que corre sin R instalado; (3) test_rpy2_inprocess_lcmcr (tests:168-177) LCMCR recupera N=1000 rel0.10. Cierre: job CI con R instalado para que via1/via3 ejecuten en vez de skip, + test de propagacion del distrust al rollup nacional.
>
> **Herramienta NEXT-LEVEL** — SparseMSE (CRAN, GPL>=2) — https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]: estimador de primera clase para estratos de solapamiento CERO (el fallo no-ES exacto), corre bajo el mismo bridge Rscript (estimators_r.py:95-129), devuelve intervalo finito donde el log-lineal degenera, degrada graceful sin R. Trio 2a-via con dga (Bayesian model averaging, CRAN GPL>=2, https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127]) + el LCMCR ya presente, sobre el mismo freqs => el sello deja de depender de UN modelo BIC. EUR0.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/exhaustiveness/estimators_r.py:26` `_MSE_R = pathlib.Path(__file__).resolve().parent / "r" / "mse.R"` [VERIFIED].
- `:29-33` `_R_CANDIDATES` HARDCODEA la maquina del owner: `C:\Users\elias\R-portable\bin\x64\Rscript.exe`, `...\bin\Rscript.exe`, `C:\Program Files\R\R-4.6.0\bin\x64\Rscript.exe` [VERIFIED].
- `:36-40` `_RHOME_CANDIDATES` (`C:\Users\elias\R-portable`, `C:\Program Files\R\R-4.6.0`) + `_RTOOLS_BIN = r"C:\rtools45\usr\bin"` [VERIFIED].
- `:43-61` `_configure_r_env()` setea `R_HOME` + antepone R/Rtools al PATH (idempotente) para que rpy2 importe [VERIFIED].
- `:64-73` `rpy2_available()` (lru_cache) intenta `import rpy2.robjects`, False ante cualquier excepcion [VERIFIED].
- `:76-83` `r_executable()` (lru_cache) recorre candidatos y cae a `shutil.which("Rscript")` [VERIFIED].
- `:86-87` `r_available()` = `r_executable() is not None`; `:90-92` `r_status()` = "available (exe)" o "pendiente entorno R (Rscript not found)" [VERIFIED].
- `:95-129` `run_mse(freqs, timeout=180)`: si `exe is None or not freqs` -> `None`; `k=len(primer patron)`; payload `{"k":k,"patterns":[list(p)+[int(f)]]}`; escribe temp JSON; `subprocess.run([exe, mse.R, tmp], capture_output, text, timeout)`; `returncode!=0` -> `{"status":"r_error","stderr":stderr[-500:]}`; parsea la ULTIMA linea de stdout como JSON; `except (Timeout, JSONDecode, IndexError)` -> `{"status":"r_error","exc":...}`; `finally` borra el temp [VERIFIED].
- `:132-172` `lcmcr_rpy2(freqs, samples=8000, burnin=5000)`: rpy2 in-process, `K=5`, `seed=20260620`, `buffer_size=10000`, `thinning=20`; devuelve `{n_hat=median, ci_low=p2.5, ci_high=p97.5, method:'lcmcr_rpy2'}` [VERIFIED].
- `:175-193` `crosscheck(python_n_hat, r_result, tol=0.25)`: sin rcapture o con error -> `{agree:None, reason:'no_r_estimate'}`; si no, `rel = abs(r_n - python_n_hat)/max(python_n_hat,1.0)`; `agree = rel <= tol` [VERIFIED].
- `pipeline/exhaustiveness/r/mse.R:15-19` `requireNamespace("Rcapture"|"LCMCR")` + `library(jsonlite)` [VERIFIED].
- `mse.R:31-49` Rcapture: `closedpMS.t(mat, dfreq=TRUE, maxorder=2, stopiflong=FALSE)`, elige min-BIC, `ci = abundance +/- 1.96*stderr` [VERIFIED].
- `mse.R:51-71` LCMCR: `lcmCR(df, tabular=FALSE, K=5, a_alpha=0.25, b_alpha=0.25, seed=20260620, buffer_size=10000, thinning=20)` + `lcmCR_PostSampl(burnin=5000, samples=8000)`; mediana + cuantiles 2.5/97.5 [VERIFIED].
- `mse.R:73` `cat(toJSON(out, auto_unbox=TRUE, digits=6))` — el JSON es la ULTIMA linea de stdout (contrato con run_mse) [VERIFIED].
- Integracion `pipeline/exhaustiveness/seal.py:78-81`: `if r_crosscheck and s.estimate.identified and s.estimate.k_lists >= 3:` -> `run_mse(freqs)` + `crosscheck(...)` -> `s.estimate.diagnostics["r_crosscheck"] = cc` [VERIFIED].
- Tests `tests/test_exhaustiveness.py:155-165` `test_r_bridge_recovers_known_n` (skip si `not r_available()`; rcapture n_hat ~1000 rel0.05; cc agree True); `:168-177` `test_rpy2_inprocess_lcmcr` (skip si `not rpy2_available()`); `:180-185` `test_r_crosscheck_flags_divergence` (fake R 5000 vs 1000 -> agree False) [VERIFIED].

#### (b) Mecanismo al atomo
Dos estimadores construidos por MECANISMO distinto al log-lineal Python, sobre el MISMO input `freqs` (patron-de-captura -> frecuencia, all-zero excluido):
1. **Rcapture::closedpMS.t** (mse.R:35) — frecuentista log-lineal con SELECCION DE MODELO sobre interacciones par-a-par (`maxorder=2`), elige min-BIC; `N_hat=abundance`, CI Wald `abundance +/- 1.96*stderr`. Es 2a opinion de la MISMA familia (log-lineal) pero con la busqueda de modelo independiente de R. `stopiflong=FALSE` fuerza que corra con >=5 listas en vez de rehusar.
2. **LCMCR** (mse.R:62-65) — Bayesiano de CLASES LATENTES (Manrique-Vallier), `K=5` clases, prior Dirichlet-process (`a_alpha=b_alpha=0.25`), ROBUSTO a heterogeneidad que el log-lineal no modela. Posterior: mediana + cuantiles 2.5/97.5. Mecanismo GENUINAMENTE distinto (mezcla latente, no log-lineal).
El puente: `run_mse` lanza Rscript por estrato (subprocess, JSON ida/vuelta via temp file); `lcmcr_rpy2` mantiene R residente in-process para batch (evita spawnear Rscript por estrato). Ambos seed 20260620 = reproducible. `crosscheck` compara `python_n_hat` vs Rcapture: `|rel diff| > 0.25` => `agree=False` (distrust). Ausencia-graciosa: `r_available()` False (sin Rscript) => callers conservan pure-Python, `r_status='pendiente entorno R'`, sin fallo ni pausa (estimators_r.py:9-11 docstring lo declara doctrina).

**ATOMO CRITICO — el crosscheck es ADVISORY, no GATE.** `_seal_one` (seal.py:39-47) computa `sealed` PURAMENTE de `coverage_lower>=threshold AND identified`. El bloque R (seal.py:78-81) corre DESPUES de que `_seal_one` ya decidio el sello (linea 77) y SOLO adjunta `cc` a `diagnostics["r_crosscheck"]`. El crosscheck NUNCA muta `sealed`. Un `agree=False` (divergencia 2x entre Python y R) queda sepultado en el jsonb `diagnostics` y el estrato SE SELLA igual. [VERIFIED seal.py:77 -> 78-81].

#### (c) Costura ES->generico
La matematica del canal R YA es pais-agnostica: consume un dict de patrones, cero literales ES. La costura es el ENTORNO, no la estadistica:
- `_R_CANDIDATES` (:29-33), `_RHOME_CANDIDATES` (:36-39) y `_RTOOLS_BIN` (:40) hardcodean rutas de la maquina del owner. En CI o cualquier otro host resuelven a nada => `r_available()=False` => la 2a via DESAPARECE en silencio para TODO pais (incluido ES).
- **Fix exacto:** leer de entorno ANTES de los candidatos hardcodeados — `os.environ.get("CARDEEP_RSCRIPT")` / `R_HOME` / `RTOOLS_BIN` — espejando `discover.py`/`harvest_dealer.py` que ya usan `os.environ.get('CARDEEP_DSN')`. Instalar R en CI (imagen rocker o `setup-r` action) para que el puente este VIVO, no dormido. Pinear versiones (Rcapture, LCMCR, SparseMSE) en un lockfile `renv` para reproducibilidad byte-estable del 2a-via.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT (fuentes delgadas):** es EXACTAMENTE donde la 2a via mas importa (el log-lineal es menos fiable con pocas listas) y sin embargo R es OPCIONAL y hoy dormido (risk #6): el pais certifica con CERO confirmacion independiente y nadie lo nota porque la ausencia es graciosa.
- **Divergencia no-bloqueante:** `crosscheck` DETECTA (agree=False) pero NO bloquea; un estrato donde Python y Rcapture difieren 2x se sella igual y el distrust queda en diagnostics, jamas en el veredicto ni el endpoint.
- **Rutas hardcodeadas:** un operador DE corriendo el sello obtiene `r_available()=False` y un sello NO verificado, indistinguible de uno verificado en la salida.
- **Punto-ciego compartido:** `maxorder=2` (mse.R:35) capa Rcapture a interacciones par; una dependencia de 3 listas que comparten sesgo de fuente queda sin modelar por AMBOS (Python y Rcapture) — que el crosscheck concuerde no significa nada porque comparten la limitacion.
- **Ruido (marketplaces disfrazados):** un par espejo del mismo registro fingiendo ortogonalidad infla overlap; Rcapture CONCORDARIA con Python (ambos comen el mismo freqs falso-ortogonal) => crosscheck verde, sello falso.

#### (e) Criterio de sellado + verificacion multi-via
- **Criterio de sello de la faceta:** la 2a via debe estar (1) VIVA en CI (`r_available()=True` en el host CI) y (2) ser VINCULANTE al menos como DOWNGRADE de confianza — `agree=False` debe degradar confidence y aflorar en el veredicto, no solo en diagnostics.
- **Via 1 (textbook):** `test_r_bridge_recovers_known_n` (tests:155-165) — celdas independientes N=1000 => Rcapture n_hat~1000 (rel 0.05) Y crosscheck `agree=True`. HOY SKIP si R ausente (el hueco de dormancia).
- **Via 2 (guard de divergencia):** `test_r_crosscheck_flags_divergence` (tests:180-185) — fake R 5000 vs Python 1000 => `agree=False`. Es el UNICO test R que corre SIN R instalado (logica pura). [VERIFIED].
- **Via 3 (LCMCR mecanismo-independiente):** `test_rpy2_inprocess_lcmcr` (tests:168-177) — LCMCR recupera N=1000 (rel 0.10), `method='lcmcr_rpy2'`. Skip sin rpy2.
- **Cierre:** job CI con R instalado para que via1/via3 EJECUTEN (no skip) + test de que `agree=False` propaga a un flag de distrust en el veredicto nacional.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**SparseMSE** (CRAN, GPL>=2) — https://cran.r-project.org/package=SparseMSE [VERIFIED NEXT-LEVEL.md:119]. Anade un estimador de PRIMERA CLASE para estratos con CERO solapamiento par — el fallo no-ES exacto (DE/IT/PT con solo GEO+OEM => K<3 => Chapman 'low' / observed-only inf-CI). SparseMSE (Chan-Silverman-Vincent 2019) maneja la no-existencia del MLE, parametros en -inf y la no-identificabilidad, devolviendo un intervalo FINITO donde el log-lineal Python degenera. Corre bajo el MISMO bridge Rscript que ya existe (`estimators_r.py:95-129`), sin infra nueva, degrada graceful si R ausente. Pareja con **dga** (Bayesian model averaging, CRAN GPL>=2, https://cran.r-project.org/package=dga [VERIFIED NEXT-LEVEL.md:127]) y el LCMCR ya presente => TRIO de 2a via (sparse / model-averaging / latente) sobre el mismo `freqs`, de modo que el sello deja de depender de UN modelo elegido por BIC. Ambos EUR0.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 25 — Ontologia de tipos de dealer + colapso a segmentos

> **Ficha 360**
>
> **Costura** — Taxonomia horneada en TRES sitios: Python (_SEGMENT + DEALER_KINDS, capture.py:19-46), el ENUM DB entity_kind (0005:13-17) e implicitamente la escalera kind_source (0005:34-39). Un pais con kinds distintos debe editar codigo motor Y hacer ALTER TYPE del ENUM. Hallazgo [VERIFIED]: DEALER_KINDS (9) es subconjunto estricto del ENUM (11); 'agente_oficial' y 'plataforma' estan en el ENUM pero NO en DEALER_KINDS => filtrados por WHERE e.kind IN (capture.py:72,88), nunca entran al MSE (exclusion de scope NO declarada). 6/9 kinds colapsan a 'otros'; solo compraventa/concesionario/desguace son sellables de 1a clase.
>
> **Fix** — Externalizar a pack countries/<CC>/taxonomy.yaml o tabla seg_map(country_code,kind,segment,include) con loader default-ES que reproduce capture.py:32-42 byte-identico. DEALER_KINDS pasa a SELECT DISTINCT kind FROM seg_map WHERE country_code=:cc AND include; segment_for carga el dict del pack. Ensanchar el ENUM entity_kind a superconjunto (o text+FK-a-pack) para anadir kinds sin ALTER TYPE. kind_source queda motor-invariante. agente_oficial/plataforma deben ser include/exclude DELIBERADO por pais, no omision silenciosa.
>
> **Adversarial** — DE/FR/IT con kinds sin analogo ES (Vertragshaendler vs freier Haendler; mandataire/agent) => fork de motor (break #5). 'desguace' como segmento sellado es regulatorio ES (DGT CAT): un pais sin esa categoria sella algo inexistente o fabrica su denominador. 'otros' (segment_for fallback, capture.py:46) absorbe en silencio cualquier kind no mapeado => segmento relevante de otro pais invisible. agente_oficial excluido: en un pais donde el canal agente-de-marca es grande, esa masa se cae del MSE (infra-conteo indistinguible de ausencia). Ruido: 'plataforma' excluido es correcto en ES pero tira dealers fisicos mal-clasificados en otro pais.
>
> **Sellado** — Sello: rejilla de segmentos = hecho de pack, motor reproduce ES byte-identico, cada kind del ENUM/pack con include/exclude+mapeo EXPLICITO (cero 'otros' silencioso). Multi-via: (1) golden ES — cargar taxonomy.yaml reproduce DEALER_KINDS+_SEGMENT exacto (diff test vs literales); (2) completitud — assert que cada valor del ENUM entity_kind (0005:13-17) esta en seg_map o en exclusion explicita, test que HOY fallaria para agente_oficial/plataforma aflorando la decision oculta; (3) contrato de pack — seg_map validado por Table Schema (kind in ENUM, segment in {sellable}U{otros}) en bootstrap, falla la carga ante kind/segmento foraneo.
>
> **Herramienta NEXT-LEVEL** — Frictionless Framework (frictionless-py, Table Schema) (MIT, EUR0) — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]: declarar seg_map como Table Schema con tipos + enum sobre segment (vocabulario sellable) + enum/FK sobre kind (entity_kind conocido), validado en bootstrap ANTES de construir captura; kind/segmento foraneo FALLA con mensaje claro en vez de colapsar a 'otros'. Aplica COUNTRY-PROOF a la ingesta de taxonomia. Alternativas [VERIFIED NEXT-LEVEL.md:338,168,584]: Pandera, Great Expectations (contrato PRE-sello), Pydantic (seg_map tipado en CI). EUR0, pip-puras.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/exhaustiveness/capture.py:19-29` `DEALER_KINDS` = 9-tupla: `compraventa, concesionario_oficial, desguace, garaje, subasta, importador, cadena, rent_a_car_vo, oem_vo_portal` [VERIFIED].
- `capture.py:32-42` `_SEGMENT` dict: `compraventa->compraventa`, `concesionario_oficial->concesionario`, `desguace->desguace`, y `garaje/subasta/importador/cadena/rent_a_car_vo/oem_vo_portal -> "otros"` [VERIFIED].
- `capture.py:45-46` `segment_for(kind) = _SEGMENT.get(kind, "otros")` [VERIFIED].
- `capture.py:72` y `:88` `WHERE e.kind::text IN %s` con `DEALER_KINDS` — define el UNIVERSO de captura [VERIFIED].
- `capture.py:111` `seg = segment_for(kind) if kind else "otros"` en `build()` — etiqueta la dim-2 de cada fila de captura [VERIFIED].
- `migrations/0005_types_and_guards.sql:12-18` `CREATE TYPE entity_kind AS ENUM(...)` 11 valores: `concesionario_oficial, agente_oficial, compraventa, garaje, desguace, rent_a_car_vo, subasta, importador, oem_vo_portal, plataforma, cadena` [VERIFIED].
- `0005:11,16` `'cadena'` marcado DEPRECATED / read-only ("never newly assigned") [VERIFIED].
- `0005:34-39` `kind_source` ENUM = escalera de precedencia: `registral, oem_locator, legal_census, curated_brandlist > classifier > platform_label` (de donde vino el kind autoritativo) [VERIFIED].

**HALLAZGOS [VERIFIED]:**
1. `DEALER_KINDS` (9, capture.py:19-29) es SUBCONJUNTO ESTRICTO del ENUM `entity_kind` (11, 0005:13-17). Dos valores del ENUM — **`agente_oficial`** y **`plataforma`** — NO estan en `DEALER_KINDS` => filtrados por `WHERE e.kind::text IN %s` (capture.py:72,88) => NUNCA entran al universo de captura / MSE. `agente_oficial` (agente oficial de marca) es discutiblemente un punto de venta; su exclusion silenciosa es una decision de scope NO declarada.
2. `'cadena'` es DEPRECATED en el ENUM (0005:16) pero SIGUE en `DEALER_KINDS` (capture.py:26) y mapea a `'otros'` (capture.py:39) — filas deprecadas aun fluyen a captura.
3. 6 de 9 kinds colapsan a `'otros'` (capture.py:37-41): garaje, subasta, importador, cadena, rent_a_car_vo, oem_vo_portal. Solo 3 segmentos son sellables de primera clase: `compraventa, concesionario, desguace`. `'otros'` es cajon-de-sastre, NO un segmento sellable limpio.

#### (b) Mecanismo al atomo
La dim-2 del estrato (el eje segmento) se define en DOS capas: el ENUM DB `entity_kind` (0005:13-17, el universo de kinds legales) y el colapso Python `_SEGMENT` (capture.py:32-42, kind->segmento). `build()` (capture.py:111) llama `segment_for(kind)` para etiquetar el segmento de cada fila de captura; `read_patterns` agrupa por `(province, segment)`; el MSE corre por estrato `(province, segment)`. Asi `_SEGMENT` gobierna DIRECTAMENTE la rejilla sobre la que se estima y se sella N_hat. Tres segmentos sellables (compraventa/concesionario/desguace) + `'otros'` cajon. El kind se asigna aguas-arriba por la escalera `kind_source` (0005:34-39): registral/oem_locator/legal_census/curated_brandlist vence a classifier vence a platform_label — i.e. el kind autoritativo viene del registro/OEM-locator/censo-legal, NO de una etiqueta de marketplace.

#### (c) Costura ES->generico
La taxonomia esta HORNEADA en tres sitios — Python (`_SEGMENT`, `DEALER_KINDS` en capture.py), el ENUM DB (`entity_kind` en 0005) e implicitamente la escalera `kind_source`. Un pais nuevo con kinds de punto-de-venta distintos debe EDITAR codigo motor Y el ENUM (un `ALTER TYPE`). **Fix exacto:**
- Externalizar a PACK de pais: `countries/<CC>/taxonomy.yaml` o tabla `seg_map(country_code, kind, segment, include)` con loader default-ES que reproduce capture.py:32-42 BYTE-identico.
- `DEALER_KINDS` pasa a `SELECT DISTINCT kind FROM seg_map WHERE country_code=:cc AND include`.
- `segment_for` pasa a dict cargado del pack (no literal Python).
- El ENUM `entity_kind` debe ensancharse a SUPERCONJUNTO (o reemplazarse por `text` + FK-a-pack) para que un pais anada kinds tipo `agente_oficial` SIN `ALTER TYPE`.
- La escalera `kind_source` queda motor-invariante (es regla de precedencia, no hecho de pais).
- CRITICO: `agente_oficial`/`plataforma` deben ser un include/exclude DELIBERADO por pais, no una omision silenciosa de `DEALER_KINDS`.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT:** un pais cuya ontologia de punto-de-venta tiene kinds sin analogo ES (DE 'Vertragshaendler' vs 'freier Haendler'; FR 'mandataire'/'agent') debe editar el ENUM + Python; hoy no hay ruta de pack => fork de motor (break #5).
- **'desguace' como segmento sellado** es regulatorio ES (DGT Centros Autorizados de Tratamiento): un pais sin esa categoria legal sella un segmento que no existe, o peor fabrica un denominador para el.
- **'otros' por defecto** (segment_for fallback, capture.py:46) absorbe en SILENCIO cualquier kind no mapeado: un segmento relevante de otro pais cae a 'otros' y nunca se sella como estrato propio => su cobertura es invisible.
- **agente_oficial excluido** (no esta en DEALER_KINDS): en un pais donde el canal agente-de-marca es gran parte de los puntos de venta, esa masa se cae del MSE entera => infra-conteo del denominador, indistinguible de ausencia genuina.
- **Ruido:** excluir 'plataforma' es correcto en ES (es agregador, no punto fisico) pero en un pais donde filas 'plataforma' son dealers fisicos mal-clasificados, la exclusion tira puntos reales.

#### (e) Criterio de sellado + verificacion multi-via
- **Criterio de sello:** la rejilla de segmentos es HECHO de pack, el motor reproduce ES byte-identico, y CADA kind del ENUM/pack tiene include/exclude + mapeo de segmento EXPLICITO (ningun 'otros' silencioso para un kind relevante del pais).
- **Via 1 (golden ES):** cargar `countries/ES/taxonomy.yaml` debe reproducir `DEALER_KINDS` (capture.py:19-29) y `_SEGMENT` (capture.py:32-42) EXACTAMENTE — test de diff del dict cargado vs los literales actuales.
- **Via 2 (completitud):** assert de que CADA valor del ENUM `entity_kind` (0005:13-17) esta en el `seg_map` del pais O en una lista de exclusion explicita — ningun valor del ENUM cae en silencio a 'otros'. HOY este test FALLARIA para `agente_oficial`/`plataforma` (excluidos por omision), aflorando la decision oculta.
- **Via 3 (contrato de pack):** el `seg_map` validado por Table Schema (tipos; `kind` in ENUM; `segment` in {set sellable} U {otros}) en bootstrap; un kind fuera del ENUM del pais o un segmento fuera del vocabulario FALLA la carga.

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Frictionless Framework (frictionless-py, Table Schema)** (MIT, EUR0) — https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:337]. Declarar el pack de taxonomia del pais (`seg_map`: kind, segment, include) como un Table Schema frictionless con tipos, constraint `enum` sobre `segment` (el vocabulario sellable) y constraint enum/FK sobre `kind` (debe ser un `entity_kind` conocido). Validar el pack en el BOOTSTRAP del pais ANTES de construir una sola fila de captura — un kind fuera de la ontologia del pais o un segmento fuera del set permitido FALLA la validacion con mensaje claro, en vez de colapsar en silencio a 'otros'. Aplica la doctrina COUNTRY-PROOF ('que la maquina la imponga y la pruebe sola') a la INGESTA de la taxonomia. Alternativas [VERIFIED NEXT-LEVEL.md:338,168,584]: Pandera, Great Expectations (el contrato de datos PRE-sello que ademas chequea 'vocabulario del census casa los segmentos'), Pydantic (seg_map como CONTRATO TIPADO en CI). Todas EUR0, pip-puras, CI-runnable.

[↑ Índice de facetas](#índice-de-facetas)

---

### Faceta 26 — Vista de serving + endpoints API (latest-por-pais)

> **Ficha 360**
>
> **Costura** — La superficie de serving es single-tenant POR CONSTRUCCION. v_exhaustiveness_seal (0048:82-106) usa CTE latest = ORDER BY created_at DESC LIMIT 1 (un build_run_id global) y no hay columna country_code en ninguna tabla (0048:39,58) para particionar [VERIFIED]. report.coverage_report (report.py:15-46) y /geo/exhaustiveness (geo.py:147-221) leen esa vista; /geo/seal (geo.py:92-144) lee v_province_seal, tambien sin pais. Ningun endpoint acepta parametro country. Tras un build DE con created_at mas nuevo, el sello ES desaparece de toda la superficie.
>
> **Fix** — 1) Schema: anadir country_code a exhaustiveness_estimate (dep faceta 20) y province_code->region_code text. 2) Vista: reescribir v_exhaustiveness_seal de 'ORDER BY created_at DESC LIMIT 1' a 'DISTINCT ON (country_code) ... ORDER BY country_code, created_at DESC' para que el ultimo build de cada pais sobreviva. 3) Endpoint: query param country (default pais home del deploy) + WHERE country_code=:cc en geo.py:168-172 y report.py:20-28. 4) Cache key: incluir country efectivo para que /geo/ES nunca sirva el cuerpo de /geo/DE. Los cuatro en el MISMO cambio que la columna country_code o la vista rompe en silencio al entrar pais #2.
>
> **Adversarial** — Build ES luego DE => v_exhaustiveness_seal muestra SOLO DE (created_at mas nuevo, LIMIT 1) => /geo/exhaustiveness y coverage_report sirven DE; el sello ES se evapora del producto (break #6), sin error. Bleed cross-pais: sin filtro, un consumidor pidiendo ES recibe numeros DE; cobertura es senal competitiva AUTHED (geo.py:161) => particion mal hecha FILTRA el denominador de un pais a otro (CRITICAL). Cache (geo.py:103,163) con clave sin pais sirve respuesta DE a peticion ES tras el flip. No-UE: region_code que desborda char(2) (DE AGS 5-dig, FR DOM '971' 3-char) escribe truncado y los estratos colisionan.
>
> **Sellado** — Sello: cada pais sirve su propio ultimo sello; ninguna carrera de created_at oculta un pais tras otro; endpoint country-scoped, bleed mecanicamente imposible. Multi-via: (1) golden coexistencia — builds ES+DE en una DB, /geo/exhaustiveness?country=ES da headline ES y ?country=DE da DE, ambos presentes (patron test_country_coexistence.py:416-458); (2) fuzz bleed — Schemathesis con hook de pais asertando que toda respuesta con dimension pais trae SOLO ese pais; (3) frescura/aislamiento — vista como IMMV con PK(country_code), sembrar DE en txn revertida no toca ES; (4) estabilidad — oasdiff: anadir pais es aditivo, 0 breaking changes.
>
> **Herramienta NEXT-LEVEL** — Schemathesis (schemathesis/schemathesis, MIT, EUR0) — https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828]: fuzzing property-based del schema OpenAPI de FastAPI, auto-detecta 500s + violaciones de contrato + fuga cross-country con hook de pais; ataca directo el leak CRITICAL de la faceta. Trio-sustrato: pg_ivm (sraoss/pg_ivm, PostgreSQL License, https://github.com/sraoss/pg_ivm [VERIFIED NEXT-LEVEL.md:764]) mantiene v_exhaustiveness_seal como IMMV con PK(country_code); souin (darkweak/souin, MIT, https://github.com/darkweak/souin [VERIFIED NEXT-LEVEL.md:780]) cache de borde con clave por pais; oasdiff (Apache-2.0, https://github.com/oasdiff/oasdiff [VERIFIED NEXT-LEVEL.md:836]) gatea el contrato country-generico. EUR0.

#### (a) Verificacion de code_hints [VERIFIED]
- `migrations/0048_discovery_capture.sql:82-106` `v_exhaustiveness_seal`: `WITH latest AS (SELECT build_run_id FROM exhaustiveness_estimate ORDER BY created_at DESC LIMIT 1) SELECT e.* ... JOIN latest l ON l.build_run_id = e.build_run_id` [VERIFIED] — "ultimo build GLOBAL", `LIMIT 1`, SIN columna pais.
- `0048:39` `discovery_capture.province_code char(2)`; `:58` `exhaustiveness_estimate.province_code char(2)` — NO existe `country_code` en NINGUNA tabla [VERIFIED].
- `pipeline/exhaustiveness/report.py:15-46` `coverage_report()`: `SELECT ... FROM v_exhaustiveness_seal ORDER BY (province_code IS NULL) DESC, n_obs DESC`; separa national (`province_code is None AND segment is None`) vs strata; devuelve `{national, strata, n_strata}` [VERIFIED].
- `services/api/routers/geo.py:92-144` `/geo/seal`: lee `v_province_seal` (registral 0042+0043), segmenta venta/desguace, `RATE_EXPENSIVE`, `require_api_key`, cacheado [VERIFIED].
- `geo.py:147-221` `/geo/exhaustiveness`: lee `v_exhaustiveness_seal` `ORDER BY segment NULLS FIRST, province_code NULLS FIRST`; la fila grand-national (`segment None AND prov None`) es el headline `_cert`; arma `by_segment`; expone `build_run_id` + `generated_at` como provenance re-ejecutable; AUTHED ("coverage scale is a competitive signal", geo.py:161); cacheado EXPENSIVE [VERIFIED].

**HALLAZGO [VERIFIED]:** la superficie de serving es single-tenant POR CONSTRUCCION. El CTE `latest` de `v_exhaustiveness_seal` (`ORDER BY created_at DESC LIMIT 1`, 0048:87) elige UN `build_run_id` global. No hay `country_code` (0048:39,58) para particionar. Asi, tras un build DE con `created_at` mas nuevo, `latest` elige el `build_run_id` DE y el sello ES DESAPARECE de `v_exhaustiveness_seal`, por tanto de `report.coverage_report` (report.py:25) Y de `/geo/exhaustiveness` (geo.py:171). Ningun endpoint acepta parametro de pais. `/geo/seal` lee otra vista (`v_province_seal`) tambien SIN pais.

#### (b) Mecanismo al atomo
Tres capas de serving, todas leyendo "ultimo build":
1. **`v_exhaustiveness_seal`** (0048:82-106) — la vista SQL: CTE latest-global (`LIMIT 1`) + proyeccion de columnas de `exhaustiveness_estimate`.
2. **`report.coverage_report`** (report.py:15-46) — lector Python: SELECT de la vista, split `(NULL,NULL)=national` vs strata, devuelve `{national, strata, n_strata}`.
3. **`/geo/exhaustiveness`** (geo.py:147-221) — endpoint async: fetch de la vista, arma `{certificate, method, build_run_id, generated_at, national, by_segment}`; la fila `(segment NULL, province NULL)` es el certificado headline; authed porque la escala de cobertura es senal competitiva; cacheado EXPENSIVE. `/geo/seal` (geo.py:92-144) es la superficie PARALELA registral sobre `v_province_seal`.
El headline lleva `build_run_id` + `created_at` como provenance re-ejecutable; honesto-por-construccion (un estrato delgado reporta `coverage_lower~0 sealed=false`, geo.py:160).

#### (c) Costura ES->generico
La vista es el punto unico que debe volverse por-pais. **Fix exacto:**
1. **Schema:** anadir `country_code` a `exhaustiveness_estimate` (dependencia faceta 20) y ensanchar `province_code -> region_code text`.
2. **Vista:** reescribir `v_exhaustiveness_seal` de `ORDER BY created_at DESC LIMIT 1` a `DISTINCT ON (country_code) ... ORDER BY country_code, created_at DESC` para que el ultimo build de CADA pais sobreviva independiente.
3. **Endpoint:** anadir query param `country` (default = pais home del deploy, back-compat) y filtro `WHERE country_code=:cc` en geo.py:168-172 y report.py:20-28.
4. **Cache key:** incluir el country efectivo para que `/geo/ES/...` jamas sirva el cuerpo de `/geo/DE/...` (el leak de cache.py).
Los cuatro deben aterrizar en el MISMO cambio que la columna `country_code` (faceta 20) o la vista rompe en silencio al entrar pais #2.

#### (d) Riesgo adversarial concreto
- **Build ES luego DE => la vista muestra SOLO DE** (created_at mas nuevo, LIMIT 1) => `/geo/exhaustiveness` y `coverage_report` sirven DE; el sello ES se EVAPORA de la superficie de producto (break #6). Sin error — la consulta ES devuelve filas DE o el headline cambia de pais en silencio.
- **Bleed cross-pais:** sin filtro de pais, un consumidor pidiendo cobertura ES recibe numeros DE; la cobertura es senal competitiva AUTHED (geo.py:161) => una particion mal hecha FILTRA el denominador de un pais al consumidor de otro (CRITICAL).
- **Cache:** `try_cache_get` (geo.py:103,163) con clave sin pais serviria una respuesta DE cacheada a una peticion ES tras el flip de build.
- **No-UE/ruido:** un pais cuyo `region_code` desborda char(2) (DE AGS 5-dig, FR DOM '971' 3-char) escribe codigos truncados en la misma columna; la vista JOINea a traves de ellos y los estratos colisionan/colapsan.

#### (e) Criterio de sellado + verificacion multi-via
- **Criterio de sello:** cada pais sirve SU propio ultimo sello; ninguna carrera de `created_at` puede ocultar un pais tras otro; el endpoint es country-scoped y el bleed cross-pais es mecanicamente imposible.
- **Via 1 (golden coexistencia):** sembrar builds ES y DE en una DB, assert de que `/geo/exhaustiveness?country=ES` devuelve el headline ES y `?country=DE` el DE, AMBOS presentes (patron `test_country_coexistence.py:416-458` referenciado en NEXT-LEVEL.md:767).
- **Via 2 (fuzz de bleed):** Schemathesis property-based con hook de pais que asserta que toda respuesta con dimension pais trae SOLO ese pais (NEXT-LEVEL.md:831).
- **Via 3 (frescura/aislamiento):** la vista como IMMV con PK(country_code) — sembrar DE en txn revertida no cambia los conteos ES (NEXT-LEVEL.md:767).
- **Via 4 (estabilidad de contrato):** gate oasdiff — anadir pais es aditivo, 0 breaking changes (NEXT-LEVEL.md:839).

#### (f) Herramienta NEXT-LEVEL (nivel inalcanzable)
**Schemathesis** (schemathesis/schemathesis, MIT, EUR0) — https://github.com/schemathesis/schemathesis [VERIFIED NEXT-LEVEL.md:828]. Fuzzing property-based dirigido por el schema OpenAPI que FastAPI ya expone: genera miles de casos por endpoint auto-detectando 500s, respuestas que violan el contrato, y — con check stateful + hook de pais — fuga cross-country. Ataca DIRECTO el riesgo CRITICAL de la faceta 21 (cobertura de un pais filtrada al consumidor de otro) asertando que toda respuesta con dimension pais trae SOLO ese pais (NEXT-LEVEL.md:831). Trio-sustrato que vuelve "latest-por-pais" auto-fresco + anti-leak: **pg_ivm** (sraoss/pg_ivm, PostgreSQL License, https://github.com/sraoss/pg_ivm [VERIFIED NEXT-LEVEL.md:764]) para mantener `v_exhaustiveness_seal` como matview incremental con PK(country_code) de aislamiento; y **souin** (darkweak/souin, MIT, https://github.com/darkweak/souin [VERIFIED NEXT-LEVEL.md:780]) para una cache de borde cuya clave incluye el country efectivo (cierra el leak cache.py). **oasdiff** (Apache-2.0, https://github.com/oasdiff/oasdiff [VERIFIED NEXT-LEVEL.md:836]) gatea el invariante de contrato country-generico. Todas EUR0.

[↑ Índice de facetas](#índice-de-facetas)

---

## Mejoras a nivel inalcanzable (EUR0, priorizadas)
Ordenadas por **palanca/esfuerzo** (todas €0, sin GPU; el techo es que ningún equipo humano las sostiene a mano build a build):

| # | Mejora | Efecto | Esfuerzo | Cierra |
|---|---|---|---|---|
| 1 | **Encender `unit='splink'` por default + canal R/LCMCR nacional**, persistidos como diagnóstico permanente | Splink recupera solapes (m↑→CI↓→`coverage_lower`↑); LCMCR N̂ menos sesgado bajo heterogeneidad | **S** (ya in-tree, apagado) | refuerza g3, 2.ª vía |
| 2 | **Censo externo VINCULANTE:** inyectar `n_external` como celda-marginal/margen-conocido en el ajuste Fienberg (población parcialmente conocida) para PIN-ear N en estratos no-identificados | Traslada masa **uncertified→certified** con mecanismo independiente; sube el denominador defendible **sin inventar** | **L** | **H1** (el open item central) |
| 3 | **Auto-hospedar SearXNG** (meta-buscador €0) para activar la lista **DORK** (búsqueda programática de dominios propios del dealer), hoy dormida | +1 señal genuinamente ortogonal en **todos** los estratos → K↑ → CI↓ → `coverage_lower`↑; **cross-border** (no-ES también) | **M** | g2, **B3/P2** |
| 4 | **Detector de saturación:** persistir `coverage_lower` (y ancho del intervalo) por build; declarar "no queda nada que encontrar" **solo** cuando la cota inferior deja de subir | Convierte "exhaustividad" de afirmación a **propiedad medida** del intervalo que encoge — la única definición honesta de 100% | **M** | doctrina (H) |
| 5 | **Más listas ortogonales €0** (Wikidata, OpenCorporates open data, páginas amarillas espejadas, Google Business cuota libre) como nuevas listas MSE | Cada mecanismo distinto reduce dependencia entre listas y aprieta el bound dependence-robust | **L** | B3/P2 |
| 6 | **Peso de identificabilidad continuo** en vez del corte duro `IDENT_CAP=5.0`: ponderar el estrato de bajo solape (info parcial con su incertidumbre real) en vez de tirarlo a uncertified | Recupera información hoy descartada; roll-up nacional con mezcla ponderada y varianza propagada | **M** | refina B9/H3 |
| 7 | **Estratificación por heterogeneidad más fina** (urbano/rural, tamaño de municipio) para cumplir mejor el supuesto Fienberg de homogeneidad intra-estrato | Reduce sesgo por dependencia de listas → intervalo más estrecho | **M** | calidad del sello |

> Todas exigen el **músculo determinista 24/7 + reproducibilidad por build**; ninguna es trabajo manual. Es el "censo de mecanismos" que ninguna persona sostiene — el listón de §00-MASTER.

---

## Riesgos / open items
1. **DOBLE SISTEMA DE SELLO conviviendo** (registral `v_province_seal` ~80,5% vs estadístico `v_exhaustiveness_seal` ~37,7%): miden cosas distintas (techo registral DIRCE vs **cota inferior** MSE). `geo.py` los sirve como `/geo/seal` y `/geo/exhaustiveness` separados, pero **la narrativa pública debe declarar que el INTERVALO MSE es la verdad de exhaustividad** y el registral es solo contraste. [ASSUMED cifras punto-en-el-tiempo]
2. **NUMERADOR AMBIGUO no resuelto (OPEN ITEM central):** `v_servable_dealer` define el punto-venta canónico pero **NO está cableado**; mientras tres scopes (~54,6k / geo / ~18,3k) sigan vivos, toda fracción es atacable. [VERIFIED `0056:6-9,26-37`]
3. **ANCLA NO VINCULANTE (OPEN ITEM):** la triangulación se reporta pero no acota N̂ ni gatea el sello [VERIFIED `seal.py:42-47`]; R + triangulación lo DETECTAN, no lo BLOQUEAN. Regla operativa: no sellar con `n_hat_high`.
4. **INPUTS MSE NO FIABLES:** la recon indica solo **4/25 adaptadores** pasaron por `harvest_run` [ASSUMED]; muchas listas infra-pobladas → el 37,7% puede ser cobertura real baja **o** listas vacías. Hasta alimentar las 7 listas no se distingue "no cubierto" de "no observado por esa lista". (Palanca g1.)
5. **`[ESTIMADO DECLARADO]` en el ancla ES:** `compraventa`/`concesionario` del censo son **apportionment** de totales nacionales (ratio `0.2605`, FACONAUTO 5358 por población), no medidos por provincia [VERIFIED `load_denominator_provincia.py:38`]; `SOURCE.md` lo declara, pero un lector descuidado podría tomarlo como medido.
6. **DEPENDENCIA DE ENTORNO para el 2.º canal:** R (Rcapture/LCMCR) y Splink son **opcionales y hoy dormidos**; sin ellos la verificación por 2.ª vía se reduce a la triangulación, debilitando la garantía anti-sesgo. (Nivel Inalcanzable #1 los enciende.) [VERIFIED guard graceful `seal.py:78`]
7. **ESTADO PUNTO-EN-EL-TIEMPO:** 37,7% y 80,5% provienen de recon/`liveseal` con el **stack caído**; **no re-ejecutables ahora**. Cualquier afirmación de progreso debe re-correr `cli.py` contra la DB viva primero. [ASSUMED]
8. **MIGRACIÓN `country_code` es `ALTER` de tablas con datos:** aunque `ADD COLUMN DEFAULT 'ES'` es byte-estable, `v_exhaustiveness_seal` y `geo.py` asumen "último build global" y **romperían en silencio** al entrar el 2.º país si no se migran a "último build por `country_code`" **en el mismo cambio** (B1+B6+H4 son un solo bloque atómico). [VERIFIED `0048:82-88`]
