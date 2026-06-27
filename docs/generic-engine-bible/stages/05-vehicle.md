# Etapa 5 · Vehículo — Biblia (capítulo **v2 PROFUNDO**)
> **v2:** integra los **25 sub-proyectos institucionales (360 por faceta)** — ver [Sub-proyectos institucionales](#indice-subproyectos). La estructura v1 (Misión · Lo que existe · Motor/Pack · Costuras · Diseño genérico · Onboarding · Sellado · Veredicto adversarial · Mejoras · Riesgos) se conserva intacta; el bloque profundo se añade tras el Veredicto.
> Estado adversarial: **NEEDS_REWORK** (el inquisidor rompe el diseño: `holds=false`). Fuente: Wave 1 (path:línea verificado, releído byte a byte esta sesión). Stack vivo **CAÍDO** (PG `:5433` cerrado): toda cifra DB es **punto-en-el-tiempo**, no medición viva — los anti-FP checks DB-backed no son ejecutables ahora, solo lo verificable por función-pura y por lectura de esquema/código.

---

## Misión
Convertir el flujo de listings crudos en el **inventario físico canónico** y su **huella histórica viva**: un coche físico = una fila canónica (sin importar en cuántas plataformas aparezca), más una línea de tiempo append-only de los 5 cambios que importan (alta, baja, precio, foto, km). La etapa **no toca `cdp_code` ni identidad de país**: opera sobre identificadores opacos (`vehicle_ulid`, `entity_ulid`) y atributos físicos (make/model/year/km/price/foto). La dimensión país le entra por **una sola arista de JOIN** (`entity.country_code`), y ahí está exactamente el problema que el inquisidor destapa.

El veredicto es claro y se asume sin maquillaje: **el motor de Vehículo es ~95% country-agnóstico por construcción, pero el 5% restante —el dedup y el saneo— es country-BLIND, no country-aware.** El esquema ya hizo la identidad geo compuesta (`0052`/`0053`); la lógica de la etapa **no la consume**. Este capítulo integra cada rotura con su resolución de diseño o, donde no cierra a €0 hoy, la declara OPEN ITEM con causa y gate.

---

## Lo que existe HOY (verificado)

- **Snapshot de inventario `vehicle`**: PK opaca `vehicle_ulid`, FK `entity_ulid`, `UNIQUE (entity_ulid, deep_link)`, columna `photo_hash` para Δfoto, `currency CHAR(3) NOT NULL DEFAULT 'EUR'`. **NO porta `cdp_code` ni `country_code`** → la etapa es country-blind por construcción; la dimensión país solo es derivable vía `entity_ulid → entity.country_code`. [VERIFIED `migrations/0003_vehicles_events.sql:4-26` (PK :5, currency :14, photo_hash :18); `migrations/0052_country.sql:36-38` (vehicle deliberadamente sin country_code, derivable vía entity)]
- **Timeline append-only `vehicle_event`**: `CHECK (event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE'))`, `old_value`/`new_value` JSONB, nunca UPDATE/DELETE. Es la huella histórica universal. [VERIFIED `migrations/0003_vehicles_events.sql:33-46` (CHECK 5 tipos :37-38)]
- **Dedup determinista det-v1** (union-find path-halving + union-by-rank) sobre coches físicos, **sin mutar ninguna fila `vehicle`**. Canonical = `first_seen` más antiguo, tiebreak `ulid` asc. Escritura idempotente (DELETE `RUN_ID` + rewrite en una transacción). [VERIFIED `pipeline/identity/cluster_vehicles.py:197-231` (UnionFind), `:493-501` (_select_canonical), `:598-606` (_write_to_pg idempotente)]
- **Signal A (foto-URL exacta = mismo coche, suficiente sola)** con 3 guards: normalización de URL (quita query/slash/sufijos resize, `:145-163`), high-collision `K=12` que excluye fotos catálogo/placeholder (`:338-347`, `K` declarado `:97`), guard km=0/NULL stock-nuevo sin VIN (`:365-367`), guard cross-generación >2 años / >50k km = foto catálogo (`:372-373`). [VERIFIED `pipeline/identity/cluster_vehicles.py`]
- **Signal B (firma cross-entity)** = `exact(make,model,year,km)` + price ±2% + misma `province_code` + **distinto `entity_ulid`** + mismo título normalizado. Guards: non-null-price (`:426`), km=0/NULL (`:415-417`), same-entity nunca fusiona (`:441-442`), corroboración por título (`:444-447`). Clave de bloque en `:397`. [VERIFIED `pipeline/identity/cluster_vehicles.py`; `PRICE_TOL_PCT=0.02` :83]
- **Overlay no destructivo + gate VAM cero-confianza**: `vehicle_cluster_run` + `vehicle_cluster`; `vam_verified BOOLEAN NOT NULL DEFAULT FALSE`; la vista `v_canonical_vehicle` solo sirve el último run con `vam_verified=TRUE`. [VERIFIED `migrations/0023_vehicle_cluster.sql:21-48` (vam_verified :31), `:57-76` (vista filtra TRUE :73)]
- **Auto-checks anti-falso-positivo**: 0 fusiones cross-province (Check 1), 0 clusters gigantes >20 (Check 2), cobertura exactamente-una-vez (Check 3), singletons con `match_signal='none'` (Check 4). [VERIFIED `pipeline/identity/cluster_vehicles.py:834-909`]
- **`diff_vehicle` (función pura, sin I/O)**: emite PRICE/KM/PHOTO_CHANGE; promoción NULL→válido; sanea en frontera (junk→None→no evento); PHOTO_CHANGE content-aware por pHash Hamming con **fallback** a comparación de string `photo_url`; devuelve `[]` si nada cambió (cero falsos). [VERIFIED `pipeline/delta.py:290-360` (PRICE :319-324, KM :329-334, PHOTO pHash-aware :346-358, fallback string :353)]
- **`emit_change_deltas` / `reconcile_gone` / `emit_gone_events` / `delta_guard`**: emisión landing-time compartida (DRY) para re-vistos (`_BULK_REFRESH_VEHICLES` price/km/photo_url `:378-385`); baja de stale source-scoped gateada por coverage + cap de fracción >50% (`reconcile_gone:146-283`, coverage gate :188-201, cap :230, txn :245, status guard :264-266); GONE en timeline inmutable idempotente (`emit_gone_events:110-143`, dedup :134-138); probe declarado ≥0.95 / fallback previous ≥0.50 sin default-allow silencioso (`delta_guard.should_emit_gone:66-141`). [VERIFIED]
- **Core pHash DCT 64-bit FREE** (PIL+numpy+scipy+blake2b stdlib, sin dependencia nueva): `hash_image_bytes`, `hamming`, `is_phash` (guard contra junk), fetch inyectado. `PHASH_HAMMING_MAX=10` **declarado ASSUMED / sin calibrar**. [VERIFIED `pipeline/delta_photo.py:64-101`; constante + nota ASSUMED :33-34]
- **Saneo numérico en frontera**: `PRICE_MAX=5_000_000`, `KM_MAX=1_500_000` (centinela Wallapop), `YEAR_MIN=1900`, cross-field año×km. Umbrales calibrados sobre corpus **ES/EUR** (techo real ~€3.6M Bugatti). [VERIFIED `pipeline/price_sanity.py:49-53,56-124`]
- **Watermark de over-count cross-platform** (sample-verify, doctrina ±dup_ci): `photo_hash` poblado en **0 vehículos** → única fusión lícita hoy = VIN-exact (18 filas cross-platform de 17.730 con VIN-17); el over-count material **~131.8K** (weak key make+model+year+km+price+province) se **mide y se sirve con cota**, NO se fusiona. VAM por 2 vías (SQL GROUP BY vs Python) coinciden al 0.09%. [VERIFIED `scripts/cross_platform_dedup_watermark.py:11-31` (doctrina/cifras), `:59` (VIN-17), `:154-185` (VAM 2 vías), `:212` (subject_key='ES_national')]
- **Batería de tests de la etapa** (todos presentes): `test_cluster_vehicles.py`, `test_delta.py`, `test_delta_guard.py`, `test_delta_photo.py`, `test_delta_photo_branch.py`, `test_emit_gone_events.py`, `test_reconcile_gone_coverage.py`, `test_gone_guard_adoption.py`, `test_country_coexistence.py`, `test_country_golden.py`. [VERIFIED `ls tests/`]

---

## Motor (invariante, reusado byte-idéntico por país)
Lo que **NO cambia** entre países (la maquinaria es física, no nacional):

| Pieza | Por qué es invariante | Evidencia |
|---|---|---|
| Union-find det-v1 + canonical por `first_seen` + escritura overlay idempotente | Opera sobre `vehicle_ulid` opacos; ningún país lo altera | `cluster_vehicles.py:197-231,493-501,598-606` |
| **Signal A** (foto-URL / pHash) | Una foto CDN compartida ES el mismo coche **con independencia de la frontera** → global por diseño; sus guards (high-collision K, cross-generación, km=0-sin-VIN) matan los falsos de catálogo sin necesitar país | `cluster_vehicles.py:309-376` |
| **Algoritmo** de Signal B (blocking + ±2% + corroboración título + cross-entity-only) | El método es invariante; **solo cambia el grano de las claves** (ver pack) | `cluster_vehicles.py:382-456` |
| `diff_vehicle` (5 tipos, NULL→válido, saneo frontera, PHOTO pHash-aware) | Per-vehículo, ya country-blind | `delta.py:290-360` |
| `emit_change_deltas` / `reconcile_gone` / `emit_gone_events` / `delta_guard` | Per-source y per-vehículo; gating por coverage y fracción; cero wiring per-país en los conectores | `delta.py:110-446`, `delta_guard.py:66-141` |
| Core pHash DCT + hamming + is_phash + fetch inyectado | Matemática pura, €0, agnóstica de país | `delta_photo.py:64-126` |
| Esquema `vehicle` + `vehicle_event` + overlay `vehicle_cluster(_run)` + vista `v_canonical_vehicle` con gate `vam_verified` | Una sola migración (`0003`+`0023`) sirve a todos los países; `vehicle` no necesita `country_code` (derivable vía entity) | `0003`, `0023`, `0052:36-38` |
| Doctrina de cierre: over-merge < under-merge, strong-key (VIN OR pHash≤6+firma), residual servido con ±dup_ci, VAM cero-confianza | Universal | `watermark:11-31`, `0023:31` |

> **Matiz capital (lo que el inquisidor convierte en rotura):** el diseño afirma que «la cualificación por país vive en el constructor de aristas, no en el esquema». Es la **intención correcta**, pero el código **aún no la implementa**: el constructor de aristas no carga ni usa país. El motor es invariante; la *cualificación por país que lo haría seguro* todavía no está escrita.

---

## Pack por país (lo que cada país aporta para esta etapa)
Lo que el diseño dice que basta aportar (y lo que el inquisidor demuestra que **falta**):

1. **Código de unidad geo** en `entity` para el grano del guard «misma unidad geo» de Signal B (ES = INE 2-dígitos en `entity.province_code`; un país aporta su código administrativo en la misma columna, ya cualificada por `(country_code,code)` tras `0053`).
2. **Moneda** por país en `vehicle.currency` (ya existe, `DEFAULT 'EUR'`): los conectores la fijan; necesaria para que ±2% y PRICE_CHANGE comparen **dentro de una sola moneda**.
3. **Calibración de saneo de precio** si la moneda/mercado difiere: `PRICE_MAX` por moneda (KM_MAX y year son físicos → se heredan).
4. **Opcional**: extensión de `_CANON` (make_normalizer) con alias/grafías locales (el fallback verbatim ya es seguro).

> **El pack DECLARADO es insuficiente** (ver Veredicto): faltan, como mínimo, **(a)** la inyección de `country_code` en los *consumidores* de dedup/delta, **(b)** la moneda en el block_key + `PRICE_MAX` por moneda, **(c)** normalización de título consciente de script, **(d)** centinelas de odómetro + unidad de distancia por plataforma, **(e)** aplicabilidad de VIN por país, **(f)** un hook de override por país para las constantes calibradas en ES, **(g)** la especificación de ancho/granularidad del grano geo, y **(h)** geografía de muestra VAM + `subject_key` por país.

---

## Costuras ES-hardcoded → fix

| Location | Issue | Fix |
|---|---|---|
| `cluster_vehicles.py:397` (block_key) + carga `:242-258` (SELECT `e.province_code`, **sin** `e.country_code`, **sin** WHERE de país) | La clave de bloque de Signal B es country-blind: `(make,model,year,km,province)`. Tras `0053`, ES-`28` y DE-`28` coexisten; dos coches de países distintos con misma firma+título+precio caen en el **mismo bloque** y se fusionan cross-frontera. Latente hoy (solo hay filas ES) → **dispara en el país #2**. | Cargar `e.country_code` y anteponerlo: `block_key=(country_code,make,model,year,km,province)`. Cualificar Check 1 por `(country_code,province_code)`. Coste **S**, aditivo, **enviar ANTES del país #2**. |
| `cluster_vehicles.py:178-189` (`_prices_within_tolerance`) + `:430`; `delta.py:319` (PRICE_CHANGE). `currency` no leído en dedup/delta | Comparación de precio **currency-blind**: 8000 GBP ≈ 8000 EUR pasaría el ±2% de firma; el payload de PRICE_CHANGE no registra moneda. | `currency` en el block_key (mismo bloque ⇒ misma moneda, el fix más barato) + assert de misma moneda antes del ±2%; registrar `currency` en `old/new_value` del PRICE_CHANGE. |
| `cluster_vehicles.py:734` (`[('28','Madrid'),('08','Barcelona')]`) | El muestreo de validación VAM **hardcodea provincias ES**. Scaffold de reporte, no core, pero rompe la genericidad del informe por país. | Parametrizar las provincias de muestra (top-2 por inventario, computado) por país. |
| `price_sanity.py:49,51,53` (PRICE_MAX/KM_MAX/YEAR_MIN) | Umbrales calibrados sobre corpus ES/EUR (techo Bugatti €3.6M). Otra moneda/mercado necesita su techo. | `PRICE_MAX` → config per-país/per-moneda; KM_MAX y year quedan como límites físicos. Mantener Law I (under-correct over mis-correct). |
| `make_normalizer.py:19-40` (`_CANON`) | Mapa canónico anclado a la distribución ES (top-70 tokens, 2026-06-15) y a títulos en script latino. | Permitir extensión de `_CANON` por país (alias locales). El fallback verbatim ya es seguro → extensión aditiva, nunca regresiva. |
| `delta.py:378-385` (`_BULK_REFRESH_VEHICLES`) + `wallapop_wholesale.py:980-988` (`_BULK_INSERT_VEHICLES`, sin photo_hash). `grep photo_hash` = **0 escritores** en `pipeline` | `photo_hash` **no tiene ruta de escritura en ningún país**: ni el INSERT ni el REFRESH lo pueblan. El strong-key pHash y el PHOTO_CHANGE content-aware quedan **inertes** (over-count ~131.8K). No es ES-puro: es **hueco global** que bloquea el plan pHash country-agnóstico. | Añadir `photo_hash` a las listas de columnas de INSERT y REFRESH + writer de backfill gateado por governor (egress per-host). Es el plan pHash €0. |
| `delta_photo.py:34` (`PHASH_HAMMING_MAX=10`) vs `watermark:14` (pHash≤6) | Dos constantes distintas y **sin calibrar** para «misma imagen»: 10 (recompresión, delta) y 6 (identidad mismo-coche, strong-key). Ambas ASSUMED. | Calibrar ambas contra un set etiquetado de fotos (cosechado gratis en el scrape). Separar las dos semánticas (recompresión vs identidad); no reutilizar una por la otra. |

---

## Diseño genérico A→Z (la abstracción country-proof)

La etapa ya es ~95% country-agnóstica porque opera sobre identificadores opacos y atributos físicos, nunca sobre `cdp_code`. El diseño genérico **no reescribe ES**; introduce un `CountryProfile` y **cualifica el único punto donde el código asume implícitamente "un solo país"**.

**Abstracción.** Un `CountryProfile` =
```
{
  geo_unit_column,    # p.ej. entity.province_code (ES = INE 2 dígitos)
  geo_unit_level,     # provincia | región | estado | cantón | Kreis ...
  geo_unit_width,     # ancho del código (ES = CHAR(2)); decisión explícita
  currency,           # ES = 'EUR'
  price_ceiling,      # PRICE_MAX por moneda (ES = 5_000_000)
  make_aliases,       # extensión de _CANON (opcional)
  title_norm_policy,  # script-aware (latino | CJK | mixto); ss/diacríticos
  odometer_sentinels, # set por plataforma + unidad (km | millas)
  vin_applicable,     # VIN-17 | chasis-JDM-no-VIN | NOM-001 ...
  calibration         # K, resize-regex, PHASH_HAMMING_MAX, PRICE_TOL_PCT, spans
}
```
Por defecto `CountryProfile(ES) = {province_code, provincia, CHAR(2), EUR, 5M, _CANON actual, latino, {wallapop:1.5M km}, VIN-17, {K:12, tol:0.02, hamming:10}}` → **la ruta ES queda byte-idéntica** (lo verifican los goldens de `cdp_code` y la prueba de coexistencia DE-rollback). Un país nuevo solo rellena su perfil.

**Interfaces (los puntos de cualificación, en orden):**
1. **Edge-builder de Signal B**: la clave pasa de `(make,model,year,km,province)` a `CountryFirmaKey=(country_code,currency,geo_unit,make,model,year,km)` y **exige misma moneda antes del ±2%**. Con esto, el supuesto «el mismo coche físico nunca cruza frontera y siempre está en una moneda» deja de ser cierto **por accidente** (solo hay ES) y pasa a estar **garantizado estructuralmente**. `_load_vehicles` añade `e.country_code` al SELECT (scope de país opcional).
2. **Signal A** se queda **GLOBAL a propósito**: una foto CDN compartida es el mismo coche con independencia de la frontera; sus guards ya matan los falsos de catálogo.
3. **`diff_vehicle`, `emit_change_deltas`, `reconcile_gone`, `emit_gone_events`, `delta_guard`** se quedan **byte-idénticos** (per-vehículo / per-source, ya country-blind); el único añadido es registrar `currency` en el payload de PRICE_CHANGE.

**Estructura de datos.** El índice de bloqueo se reescribe de `dict[tuple] → list` a `dict[CountryFirmaKey] → list`; el union-find, la selección canonical y la escritura del overlay **no se tocan**. El overlay es universal y produce un **único espacio canónico**, con la cualificación por país viviendo dentro del edge-builder, no en el esquema.

**Esquema.** **Cero migraciones nuevas** para cubrir un país en lo tocante a `vehicle`: no necesita `country_code` (derivable vía entity, `0052:36-38`), evitando reescribir 2.3M filas. (Excepción acotada: el **ancho** del grano geo — ver rotura #7.)

**Plan pHash €0.** Añadir la ruta de escritura de `photo_hash` (INSERT+REFRESH) + backfill gateado por el **governor por-host** (token bucket de egress); las fotos ya descargadas en el scrape se hashean inline a coste cero de red adicional. Código idéntico para todo país.

**Guard "misma provincia" generalizado.** Se expresa como «misma unidad geo de nivel N» paramétrico: ES sella a provincia (INE), pero el grano es un campo del `CountryProfile`. El guard cross-province de los anti-FP checks se reexpresa como **cross-`(country, geo_unit)`**.

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)
1. Asegurar que las filas `entity` del país portan `country_code` (`0052` aplicada) y un código de unidad geo en `province_code` (o la columna del `CountryProfile`), y que `0053` (PK geo compuesta `(country_code,code)`) está aplicada para que los códigos colisionen cross-frontera sin violar PK.
2. Fijar `vehicle.currency` para los conectores del país (el ingest la escribe; override si ≠ EUR).
3. Si moneda/mercado difieren, añadir `PRICE_MAX` del país al `CountryProfile`; KM_MAX y year se heredan (físicos). Declarar el set de centinelas de odómetro + unidad de distancia de las plataformas del país.
4. Declarar `title_norm_policy` (latino / CJK / mixto) y `vin_applicable` del país. Opcional: extender `_CANON`.
5. Ejecutar `cluster_vehicles` **con la firma ya cualificada** por `(country_code,currency,geo_unit)`. Verificar los anti-FP checks **POR PAÍS**: 0 fusiones cross-`(country,geo_unit)`, 0 clusters >20, cobertura exactamente-una-vez.
6. Los conectores del país ya invocan `emit_change_deltas` / `reconcile_gone` / `emit_gone_events` **sin cambios**: cero wiring de delta per-país.
7. (Cuando aterrice el plan pHash) ejecutar el backfill gateado por governor para los hosts del país; mismo código, tokens de egress per-host. Re-calibrar `PHASH_HAMMING_MAX` y el umbral del watermark para el país.
8. Gatear `vehicle_cluster_run.vam_verified=TRUE` tras VAM del Director sobre el muestreo de 20 pares **del país** (geografía de muestra parametrizada, no `28/08`); solo entonces `v_canonical_vehicle` sirve ese run.

---

## Sellado + verificación multi-vía + rollback

**SELLADO de la etapa (definición):**
- **(a)** run det-v1 completado con **todos** los anti-FP checks en OK: 0 cross-`(country,geo_unit)`, 0 clusters gigantes >20, cobertura exactamente-una-vez (`clustered == available`), singletons con `match_signal='none'`. [`cluster_vehicles.py:834-909`]
- **(b)** over-count residual de weak-key **medido y bloqueado** como ±dup_ci en el ledger de verificación, **nunca fusionado en silencio**. [`watermark:26-31`]
- **(c)** `vehicle_cluster_run.vam_verified=TRUE` tras VAM del Director sobre el muestreo de 20 pares, y **solo entonces** `v_canonical_vehicle` lo sirve. [`cluster_vehicles.py:757-824`, `0023:70-76`]
- **(d)** integridad de delta: re-vistos emiten **solo** cambios reales (`diff_vehicle` devuelve `[]` si nada cambió → cero eventos falsos), y GONE solo bajo coverage-gate (`reconcile_gone` min_coverage + cap de fracción + `verdict != REFUTED`).

**Verificación por 2ª vía ortogonal:**
- El conteo de dedup se valida por **dos agrupaciones independientes** — SQL GROUP BY vs dict de Python — que coinciden al **0.09%**. [`watermark:154-185`]
- La coexistencia de país se prueba con un **seed DE in-transaction que hace ROLLBACK** afirmando byte-identidad de ES, más la query directa ES-`28`/DE-`28` sobre `geo_province`. [VERIFIED `tests/test_country_coexistence.py:315` (rollback byte-idéntico), `:333-348` (coexistencia ES/DE), `:133-136` (`country_code` NO entra en la pre-imagen del `canonical_key`)] + goldens de `cdp_code` (`test_country_golden.py`).
- Para el motor en sí, la vía ortogonal es la **IDEMPOTENCIA**: recomputar union-find (DELETE+rewrite del mismo `RUN_ID`) debe dar clusters idénticos, y la fila-cuenta del overlay == vehículos `available` (Check 3).

**Rollback:**
- El overlay es **no destructivo**: rollback de `0023` hace DROP de vista+tablas; las filas `vehicle` quedan intactas. [`0023:78-81`]
- Las fusiones VIN-exact del watermark escriben su estado-previo completo a JSON en `.backups/` y son idempotentes/reversibles. [`watermark:33-39`]
- El serving **degrada con gracia**: sin run `vam_verified` → `v_canonical_vehicle` vacía → se sirven filas `vehicle` crudas con ±dup_ci.
- **Rollback de país**: borrar filas geo `country_code <> 'ES'` y revertir `0053` — pero **CLEAN ONLY mientras no existan filas geo no-ES** (un PK de columna única sobre `code` no puede sostener ES-28 y DE-28 a la vez). [VERIFIED `migrations/0053_country_onboarding.sql:176-181`]

---

## Veredicto adversarial: roturas → resolución
> Mandato: **ninguna rotura se oculta**. Cada `break` / `missing_pack` / `sealing_hole` del inquisidor lleva su resolución de diseño (cómo cierra para DE/FR/IT/PT/no-UE) o, si no cierra a €0 hoy, **OPEN ITEM con causa y gate**.

Muchas roturas comparten **una sola raíz** (el dedup/saneo no consume la identidad compuesta que crearon `0052`/`0053`). Se agrupan por fix.

### FIX-A · Cualificar toda la cadena por país (cierra B#1, B#2, B#6; pack #1, #8; holes #1, #3, #4) — €0, effort S–M, **GATE: enviar ANTES del país #2**
- **B#1 [CRITICAL] DE/FR/IT/PT — falso-merge transfronterizo.** `cluster_vehicles.py` no tiene **ninguna** referencia a `country_code`; `_load_vehicles` carga todos los países sin filtro (`:258`) y selecciona solo `e.province_code` (`:255`); `block_key` clava la provincia desnuda de 2 chars (`:397`). `0053:2-4` **prueba en vivo** que `code='28'` colisiona ES vs DE; el dedup **reintroduce** la colisión en la capa app. Un VW Golf ES-28 y otro DE-28, mismo year/km, precio ±2% (ambos EUR, `0003:14`), título ASCII igual → se fusionan cruzando frontera.
  - **Resolución:** `CountryFirmaKey=(country_code,currency,geo_unit,make,model,year,km)` + cargar `e.country_code`. Un coche físico **nunca** cruza frontera → la cualificación convierte el invariante *accidental* (solo hay ES) en **estructural**. Cierra idéntico para los 4 eurozona y para no-UE.
- **B#2 [CRITICAL] — agujero de sellado, Check 1 country-blind.** `HAVING COUNT(DISTINCT e.province_code) > 1` (`:852`): un cluster ES-28 + DE-28 tiene `COUNT(DISTINCT province_code)=1` → el check **PASA** y certifica falsamente «0 fusiones cross-province». Ningún check cuenta `DISTINCT country_code`.
  - **Resolución:** reexpresar Check 1 como `COUNT(DISTINCT (country_code, province_code)) > 1` **y** añadir un **Check 0 dedicado: `COUNT(DISTINCT country_code) > 1` ⇒ FAIL duro** (el invariante "0 fusiones cross-PAÍS" que hoy no existe). Sin esto el sello miente entre fronteras.
- **B#6 [HIGH] — agujero en la medición, watermark country-blind.** `_FUZZY_FLOOR_BASE` agrupa por `e.province_code` desnudo (`:159/:171`) y la fila de ledger fija `subject_key='ES_national'` (`:212`); en BD multipaís mezcla pares ES-28/DE-28, **infla ±dup_ci** con fantasmas transfronterizos y etiqueta mal el verdict.
  - **Resolución:** añadir `country_code` al GROUP BY del fuzzy-floor y emitir **un `subject_key` por país** (`{cc}_national`). La cota servida pasa a ser **certificable por país**.
- **pack #1, #8 / holes #3, #4** quedan cubiertos por lo anterior + parametrizar la geografía de muestra VAM (`:734`, top-2 por inventario del país) y el `subject_key`.

### FIX-B · Moneda y techo de precio por moneda (cierra B#3; pack #2) — €0, effort S
- **B#3 [CRITICAL] MX/JP — `PRICE_MAX=5M` es magnitud EUR.** En JPY un coche normal vale ¥6M–¥40M (~37k–250k EUR) y **supera el techo** → `sanitize_price → None` (`price_sanity.py:64-66`). En `diff_vehicle`, `new_price=None` ⇒ PRICE_CHANGE **nunca dispara** y `emit_change_deltas` hace `COALESCE(NULL, v.price)` (`delta.py:379`) → precio servido **congelado**; en clustering el guard non-null-price (`cluster_vehicles.py:426`) **tira cada coche JPY** de Signal B. Delta + Signal B quedan ciegos para el inventario japonés normal. México (MXN ~18–20/EUR) solo rompe en gama alta.
  - **Resolución:** `PRICE_MAX` por moneda en el `CountryProfile` (JPY ~¥800M, MXN ~$100M, etc.); `currency` en el block_key (FIX-A) garantiza que el ±2% compara dentro de una moneda. KM_MAX y year se heredan (físicos). Cierra para no-UE.

### FIX-C · Normalización de título consciente de script (cierra B#4 para eurozona; OPEN parcial para JP; pack #3) — €0, effort M
- **B#4 [HIGH] JP — `_normalize_title` NFKD → `encode('ascii','ignore')` (`cluster_vehicles.py:173-174`)** vacía kanji/katakana/hiragana a `''` → retorna `None` → la corroboración de Signal B `ta and tb and ta==tb` (`:446`) **falla** (Signal B muerto, under-merge) **o** un residuo latino corto (letra de grado + año en dígitos fullwidth que NFKD pasa a ASCII) **falso-corrobora**. También pierde `ß` (eszett) y parte de diacríticos en DE/FR/PT (más leve).
  - **Resolución (DE/FR/IT/PT — CIERRA):** el daño en script latino es **under-merge conservador** (pierde corroboración, no fabrica falso-merge — la doctrina over-merge<under-merge lo tolera) salvo el riesgo de falso-positivo por residuo corto, que el `geo_unit` + precio±2% del bucket ya acotan. Una `title_norm_policy` que preserve diacríticos (NFKC + mapa `ß→ss`, ç/ñ/ü conservados) elimina el under-merge. Para eurozona cierra.
  - **OPEN ITEM (JP/CJK):** una normalización que **no colapse CJK a `None`** exige una política de título CJK real (segmentación/transliteración) que hoy no existe. **Causa:** el guard es Latin-script-only por construcción. **Gate:** hasta tener `title_norm_policy=CJK`, Signal B en Japón se apoya **solo** en pHash (FIX-D/plan pHash) y el residual se sirve como ±dup_ci. No se vende como cerrado.

### FIX-D · VIN aplicable por país (cierra B#5 para MX/eurozona; OPEN para JP; pack #5) — €0, effort S (gating) + dep. pHash
- **B#5 [HIGH] JP — strong-key VIN inaplicable.** `watermark:59` exige `length(vin_ref)=17` + charset WMI ISO-3779, que **excluye** el número de chasis JDM (*sha-dai-bango*, no es VIN de 17). Con `photo_hash` en 0 filas, **Japón no tiene ninguna vía de auto-merge lícita** → el 100% del duplicado cross-platform debe servirse como ±dup_ci. México (VIN NOM-001 de 17) sí encaja.
  - **Resolución (MX/eurozona — CIERRA):** `vin_applicable` en el `CountryProfile` gatea el brazo VIN explícitamente (no lo deja silenciosamente vacío); MX y los 4 eurozona usan VIN-17 → brazo activo.
  - **OPEN ITEM (JP):** la única strong-key que le queda a Japón es **pHash**, que depende del backfill de `photo_hash` (ver FIX-E). **Causa:** chasis JDM ≠ VIN-17 **y** `photo_hash` 0% poblado. **Gate:** plan pHash €0. Mientras tanto, Japón se sirve honestamente con cota ±dup_ci ancha. Declarado, no maquillado.

### FIX-E · Ruta de escritura de `photo_hash` + calibración (cierra el hueco global; desbloquea JP; pack #6 parcial; hole #5 parcial) — €0, effort M, **dep. de egress gateado**
- **Hueco global (no ES-puro):** `grep photo_hash` = **0 escritores** en `pipeline`; ni `_BULK_INSERT_VEHICLES` (`wallapop_wholesale.py:980-988`) ni `_BULK_REFRESH_VEHICLES` (`delta.py:378-385`) lo pueblan → strong-key pHash y PHOTO_CHANGE content-aware **inertes**; over-count ~131.8K servido como ±dup_ci ancho.
  - **Resolución:** añadir `photo_hash` a INSERT y REFRESH + backfill gateado por governor (egress per-host), hasheando inline las fotos ya descargadas. Código idéntico para todo país. Desbloquea la strong-key pHash (incluida la de Japón) y el PHOTO_CHANGE real.
  - **OPEN parcial:** `PHASH_HAMMING_MAX=10` (`delta_photo.py:33-34`) y el umbral del watermark `≤6` (`watermark:14`) están **ASSUMED**. Calibrarlos exige el set etiquetado + `photo_hash` poblado. **Gate:** este backfill. Hasta entonces, ambas constantes se usan con la etiqueta ASSUMED visible.

### FIX-F · Centinelas de odómetro + unidad de distancia por plataforma (cierra B#8; pack #4) — €0, effort S–M
- **B#8 [MEDIUM] MX/JP — `KM_MAX=1.5M` y la lógica de centinela "odómetro sin fijar" son específicos de Wallapop/ES** (`price_sanity.py:51,69-83`; el `>=` se calibró para matar el default 1.5M de la API de Wallapop). Plataformas extranjeras codifican km-desconocido distinto (p.ej. 999,999) → pasa el gate y contamina edad/km. Además el motor asume kilómetros (rompe en mercados de millas).
  - **Resolución:** `odometer_sentinels` (set por plataforma) + `distance_unit` (km|millas) en el `CountryProfile`. KM_MAX se mantiene como límite **físico**; el centinela 1.5M se mueve a config por-plataforma; millas se normalizan a km en frontera. Cierra para MX/JP/UK.

### FIX-G · Ancho/granularidad del grano geo (cierra B#7 con decisión de pack; pack #7) — €0 en código, **GATE: ESQUEMA si se ensancha CHAR**
- **B#7 [MEDIUM] DE Kreis / FR ultramar — el grano geo es `CHAR(2)`.** `geo_province.code CHAR(2)` y `entity.province_code CHAR(2)` (`0001_geo.sql:5,13`); `geo_municipality.code CHAR(5)` (`:19`). Un país cuyo grano de primer nivel necesita >2 chars **no cabe**: Kreis alemán (5 díg), departamento ultramar francés `'971'`–`'976'` (3). Forzar DE a 16 Bundesländer (2 díg) hace el bucket «misma provincia» de Signal B enorme → más colisiones de misma-firma colapsan (over-merge).
  - **Resolución:** `geo_unit_width` y `geo_unit_level` explícitos en el `CountryProfile`. Dos vías: **(i)** elegir el nivel de sellado del país a un grano que quepa en el ancho disponible, o **(ii)** ensanchar `geo_province.code`/`entity.province_code` a `VARCHAR`/`CHAR(n)` en la **migración de onboarding del país** — mecánica **ya demostrada** por `0053` (swap de PK + reescritura de los 6 FKs, reversible). El acoplamiento "grano grueso ⇒ over-merge" se mitiga porque Signal A (foto/pHash) **no depende del grano geo** y Signal B exige título + precio±2% **además** del bucket → el grano grueso aumenta candidatos pero los guards de corroboración filtran. Cierra para DE/FR con decisión de ancho en onboarding.
  - **Gate:** el ensanche de columna es **FK-breaking** (toca esquema servido) → es reversible pero entra por la puerta ESQUEMA de `cover(CC)`, no se hace en caliente.

### HOLE-#2 · Clustering global de una sola pasada (la decisión arquitectónica de la etapa) — €0, effort M
- **Rotura:** clustering global sin filtro de país (`cluster_vehicles.py:258`) + reescritura global idempotente (`:598-606`): un país **no se puede sellar / VAM-muestrear / revertir de forma independiente**. Onboarding del país #2 **re-clusteriza y re-toca el espacio canónico ES ya certificado**, acoplando el gate `vam_verified` (`0023:31`) de cada país a una única corrida global.
  - **Resolución (recomendada, cerrada por diseño):** **particionar el clustering por `country_code`** — `_load_vehicles` toma un scope de país opcional, y cada país obtiene su propio `cluster_run_id`. El union-find y el overlay **ya son per-run**: basta el scope + un run por país. Así cada país se sella / VAM / revierte **independiente**, alineado con la state machine `cover(CC)` (`SEALED` por país). Signal A cross-país (una foto CDN compartida entre dos países) es **rarísimo** y se preserva con un pase global **separado y acotado** (o se trata como excepción declarada), no como el camino por defecto. Decisión **reversible y de diseño** (no toca esquema), por eso se cierra aquí con recomendación; la única validación pendiente es confirmar empíricamente que la cobertura de Signal A cross-país es despreciable antes de partir el pase — y ese dato se mide gratis en el primer run multipaís.

### Síntesis del veredicto
> Cada rotura B#/Hole se diseca átomo a átomo en su **sub-proyecto institucional** correspondiente — ver [Sub-proyectos institucionales (360 por faceta)](#indice-subproyectos) (B#1→Faceta 8, B#2→Faceta 22, B#3→Facetas 9/11, B#4→Faceta 10, B#5→Facetas 19/25, B#6→Facetas 20/23, B#7→Faceta 24, B#8→Faceta 11, Hole #2→Facetas 5/3, pHash→Facetas 12/13).
| Rotura | Severidad | Estado | Gate |
|---|---|---|---|
| B#1 falso-merge transfronterizo | CRITICAL | **CIERRA** (FIX-A) | enviar antes del país #2 |
| B#2 Check 1 ciego a país | CRITICAL | **CIERRA** (FIX-A) | enviar antes del país #2 |
| B#3 PRICE_MAX en EUR | CRITICAL | **CIERRA** (FIX-B) | — |
| B#4 título Latin-only | HIGH | **CIERRA eurozona** / OPEN JP | título CJK |
| B#5 VIN inaplicable JP | HIGH | **CIERRA MX/UE** / OPEN JP | plan pHash |
| B#6 watermark ciego a país | HIGH | **CIERRA** (FIX-A) | enviar antes del país #2 |
| B#7 grano geo CHAR(2) | MEDIUM | **CIERRA** (FIX-G) | ESQUEMA si ensancha |
| B#8 centinela km Wallapop/ES | MEDIUM | **CIERRA** (FIX-F) | — |
| Hole #2 clustering global | — | **CIERRA** (partición por país) | validar Signal A cross-país |
| pHash inerte / constantes ASSUMED | — | **OPEN** | plan pHash + egress gateado |

---

<a id="indice-subproyectos"></a>

## Sub-proyectos institucionales (360 por faceta)

Esta etapa no es una pieza: es un **sistema de 25 sub-proyectos institucionales**, cada uno tratado a 360° (átomo a átomo) como exige el mandato. Lo de arriba es el mapa; **esto es el territorio**. Cada faceta se desmonta con el **mismo esquema fijo** para que nadie se pierda (funnel impecable):

- **(a) code_hints [VERIFIED path:línea]** — el átomo de código real, releído byte a byte.
- **(b) Mecanismo al átomo** — qué hace y por qué, sin maquillaje.
- **(c) Costura ES→genérico** — dónde el molde ES (o el hueco global) vive en el byte.
- **(d) Riesgo adversarial** — cómo rompe en DE/FR/IT/PT/no-UE, con causa concreta.
- **(e) Sellado + verificación multi-vía** — ≥2 vías ortogonales, fail-closed.
- **(f) Herramienta NEXT-LEVEL** — la palanca €0 battle-tested que lo eleva.
- **Resolución condensada** — la ficha accionable (Costura · Fix · Adversarial · Sellado · Herramienta).

> **Doctrina heredada del MASTER y honrada en cada faceta:** over-merge < under-merge · VAM cero-confianza (ningún número sin quórum ≥2 vías ortogonales) · residual servido con su cota **±dup_ci**, nunca fusionado en silencio · **€0** de cimiento · «antes confesar un hueco que vender una mentira». Los **open items se declaran con causa y gate**, no se ocultan.

> **Cómo leer la cabecera de cada faceta:** la línea en cita (`>`) bajo el título es el **estado de batalla** — rotura ligada (B#/Hole del Veredicto), severidad y gate. `CIERRA` = resuelto por diseño a €0; `OPEN` = hueco honesto con causa+gate; `país-agnóstico` = el mecanismo ya es invariante, la costura (si la hay) es de inputs/escala.

### Índice navegable (25 sub-proyectos por familia)

**A · Sustrato de datos (esquema + huella histórica)**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **1** | [Esquema snapshot de inventario (tabla `vehicle`)](#faceta-1) | Sustrato universal · sin rotura de país propia |
| **2** | [Timeline append-only de eventos (`vehicle_event`)](#faceta-2) | Append-only · hueco de escala/payload (no ES-puro) |

**B · Motor de resolución y gate de sello**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **3** | [Motor de resolución union-find determinista](#faceta-3) | Motor invariante (país-agnóstico) |
| **4** | [Overlay no-destructivo + gate VAM cero-confianza](#faceta-4) | Gate cero-confianza |
| **5** | [Aislamiento del sello por país (scoping + revertibilidad independiente)](#faceta-5) | Hole #2 — CIERRA por diseño (partición del clustering por `country_code`) |

**C · Señales de identidad física**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **6** | [Signal A: identidad por foto-URL](#faceta-6) | Calibración ES (K=12, regex resize) |
| **7** | [Signal B: firma cross-entity (algoritmo de emparejamiento)](#faceta-7) | Mecanismo país-agnóstico |
| **8** | [Cualificación país+geo del matching (fusión transfronteriza)](#faceta-8) | B#1 CRITICAL — CIERRA (FIX-A) |

**D · Normalización y saneo en frontera**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **9** | [Dimensión moneda end-to-end (FX)](#faceta-9) | B#3 CRITICAL — CIERRA (FIX-B) |
| **10** | [Normalización de título consciente de script/locale](#faceta-10) | B#4 HIGH — CIERRA eurozona / OPEN JP (`title_norm_policy=CJK`) |
| **11** | [Saneo numérico en frontera (price/km/year + cross-field)](#faceta-11) | B#3 + B#8 — CIERRA (FIX-B / FIX-F) |
| **21** | [`make_normalizer`: taxonomía canónica de marca](#faceta-21) | Costura = datos + tokenizer |

**E · Foto perceptual (pHash)**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **12** | [Núcleo pHash DCT 64-bit + calibración de umbrales](#faceta-12) | Umbrales ASSUMED — OPEN (calibración) |
| **13** | [`photo_hash`: ruta de escritura + backfill gateado por governor](#faceta-13) | Hueco GLOBAL (no ES-puro) — OPEN (plan pHash €0) |

**F · Delta y bajas (timeline vivo)**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **14** | [`diff_vehicle`: motor de delta puro](#faceta-14) | País-agnóstico |
| **15** | [`emit_change_deltas`: emisión DRY landing-time (re-vistos)](#faceta-15) | DRY país-agnóstico |
| **16** | [`reconcile_gone`: baja de stale source-scoped + coverage-gate](#faceta-16) | País-agnóstico |
| **17** | [`emit_gone_events`: baja en timeline para conectores edge-set](#faceta-17) | Hueco GLOBAL |
| **18** | [`delta_guard`: probe de completitud declared/previous](#faceta-18) | Ratios país-agnósticos |

**G · Strong-keys e identidad fuerte**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **19** | [VIN como strong-key (identidad fuerte + decode)](#faceta-19) | B#5 HIGH — CIERRA MX/UE / OPEN JP (chasis JDM ≠ VIN-17) |
| **25** | [Guard km=0 / stock nuevo (no-colapso de unidades distintas)](#faceta-25) | Guard país-blind |

**H · Medición, sello y grano geo**

| # | Sub-proyecto | Estado de batalla |
|---|---|---|
| **20** | [Watermark de over-count + ledger ±dup_ci](#faceta-20) | B#6 HIGH — CIERRA (FIX-A) |
| **22** | [Anti-FP sealing checks (4 checks + cross-país)](#faceta-22) | B#2 CRITICAL — CIERRA (FIX-A) |
| **23** | [Medición & muestra VAM (20-pares + province sample)](#faceta-23) | Muestra 28/08 ES hardcode — CIERRA (parametrizar por país; pack #8) |
| **24** | [Geo-grain: ancho y granularidad de la unidad geo](#faceta-24) | B#7 MEDIUM — CIERRA (FIX-G) |

> El **cuerpo va en orden numérico 1→25** (predecible); el índice de arriba es la **lente temática**. Cada faceta cierra con un back-link [⇧ Índice].

---

<a id="faceta-1"></a>

### Faceta 1 — Esquema snapshot de inventario (tabla `vehicle`)

> **Sustrato universal · sin rotura de país propia.** Hosts del molde `currency CHAR(3) DEFAULT 'EUR'` y del over-count estructural del `UNIQUE(entity_ulid,deep_link)`. País entra por una sola arista (`entity.country_code`).

#### (a) code_hints verificados al atomo
- [VERIFIED migrations/0003_vehicles_events.sql:4] `CREATE TABLE IF NOT EXISTS vehicle (`.
- [VERIFIED :5] `vehicle_ulid TEXT PRIMARY KEY` — PK opaca, byte-determinista, **sin** dimension pais embebida.
- [VERIFIED :6] `entity_ulid TEXT NOT NULL REFERENCES entity(entity_ulid) ON DELETE CASCADE` — la **UNICA** arista a la dimension pais (el coche hereda pais via `entity.country_code`).
- [VERIFIED :7] `deep_link TEXT NOT NULL` — URL per-vehiculo (la otra mitad de la clave de unicidad).
- [VERIFIED :8-19] atributos fisicos: `title, make, model, year INT, km INT, price NUMERIC(12,2)`, `currency CHAR(3) NOT NULL DEFAULT 'EUR'` [:14], `fuel, transmission, photo_url`, `photo_hash TEXT` [:18] (comentario "perceptual hash for delta photo detection"), `vin_ref`.
- [VERIFIED :20] `recipe_version INT`.
- [VERIFIED :21-22] `status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available','gone'))`.
- [VERIFIED :23-24] `first_seen / last_seen TIMESTAMPTZ NOT NULL DEFAULT now()`.
- [VERIFIED :25] `UNIQUE (entity_ulid, deep_link)` — materializa "un listing por (dealer, URL)".
- [VERIFIED :28-30] tres indices: `idx_vehicle_entity (entity_ulid)`, `idx_vehicle_status (entity_ulid, status)`, `idx_vehicle_available (entity_ulid) WHERE status='available'` (parcial).
- [VERIFIED migrations/0052_country.sql:36-38] item (d) explicito: `country_code` **NO** se anade a `vehicle` (2,311,202 filas) — "vehicle.country is derivable via vehicle.entity_ulid -> entity.country_code"; FASE-0 deja el geo backbone + entity como **unica** fuente de la dimension pais (YAGNI; evita un rewrite de 2.3M filas).
- [VERIFIED pipeline/platform/_core/sql.py:12-23] `BULK_INSERT_VEHICLES` inserta **14 columnas** (`vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, fuel, transmission, photo_url, vin_ref, status`) — **NO escribe `currency`** (confia en el `DEFAULT 'EUR'`) ni `photo_hash` (columna inerte); `ON CONFLICT (entity_ulid, deep_link) DO NOTHING` [:22] (la otra cara del UNIQUE).

#### (b) Mecanismo al atomo
La fila `vehicle` es el **sustrato universal**: identidad opaca (`vehicle_ulid`), una sola arista de pais (`entity_ulid` -> `entity.country_code`), y atributos puramente fisicos. La tabla es **country-blind por construccion**: ningun byte de ella sabe de Espana salvo dos moldes -- `currency CHAR(3) DEFAULT 'EUR'` y el techo `NUMERIC(12,2)`. El `UNIQUE(entity_ulid, deep_link)` define la granularidad "una fila = un (dealer, anuncio)". Esto choca a proposito con el modelo logico "un coche fisico = una fila canonica + N aristas": el mismo coche anunciado en 2 plataformas son 2 `entity_ulid` distintos -> 2 `deep_link` -> **2 filas** -> over-count estructural (~131.8K segun el insumo) que NO resuelve esta faceta (la miden/colapsan facetas 19/20/22). `photo_hash` existe pero esta 0% poblada -> el strong-key perceptual esta **inerte** (la ruta de escritura es faceta 13).

#### (c) Costura ES -> generico
Tres moldes ES viven en el esquema, con tres tratamientos distintos:
1. **country_code fuera de vehicle** (correcto, mantener): la decision 0052:36-38 es la pieza generica clave -- el pais entra por `entity`, asi onboardear el pais #2 **no reescribe 2.3M filas**. Tripwire: jamas anadir `country_code` a `vehicle`.
2. **currency CHAR(3) DEFAULT 'EUR'** (molde ES, arreglar): los conectores no la fijan (`BULK_INSERT_VEHICLES` no la incluye), asi que **todo** mercado hereda EUR en silencio.
3. **photo_hash inerte** (global, no ES-puro): poblarla es faceta 13; el esquema ya la tiene (no hay migracion pendiente).

#### (d) Riesgo adversarial concreto
- **No-UE / no-EUR (UK GBP, JP JPY, PL PLN)**: el conector que no fije `currency` produce filas con `'EUR'` heredado -> aguas abajo (faceta 9) `8000 GBP` compara como `8000 EUR`. CRITICAL latente.
- **JP**: `NUMERIC(12,2)` aguanta la magnitud JPY (hasta 9,999,999,999.99) -- el techo numerico NO es el problema; el problema es `price_sanity.PRICE_MAX=5_000_000` (faceta 11) que nula un coche JPY normal.
- **DE/FR/IT/PT (EUR)**: inocuo HOY para la moneda (mismo EUR), pero el over-count del `UNIQUE` cruza fronteras igual si las facetas 8/22 no separan por pais.

#### (e) Sellado + verificacion multi-via
- **Via 1 (golden de invariante)**: tras 0052/0053, toda fila ES queda byte-identica (la migracion 0053 es un relabel 1:1 ES; ningun `cdp_code`/atributo cambia).
- **Via 2 (autoridad de dimension)**: cada `vehicle.currency` ∈ ISO 4217 y consistente con el `country_code` de su `entity` (o mercado declarado multi-moneda) -- no `'EUR'` por defecto silencioso.
- **Via 3 (cota, no punto)**: el over-count del `UNIQUE` se sirve como `+/-dup_ci` POR PAIS (faceta 20), nunca un contador inflado mudo.
- **Via 4 (tripwire)**: assert de CI "vehicle NO tiene columna country_code" (el detonante del rewrite de 2.3M).

#### (f) Herramienta NEXT-LEVEL
**pycountry** (ISO 3166-1/-2 + **ISO 4217** currency data) — LGPL-2.1, €0 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]. Eleva la columna `currency CHAR(3) DEFAULT 'EUR'` de molde-ES a **dimension validada por autoridad**: en la frontera del conector se valida `currency ∈ ISO 4217` y `country_code ∈ ISO 3166-1`, de modo que un mercado no-EUR no puede heredar 'EUR' en silencio. Uso build/config-time (no hot-path) -> LGPL es no-issue [VERIFIED :532]. Complemento de contrato de esquema: **Frictionless Framework** (Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED :337] para versionar la forma de la fila `vehicle` como contrato de datos auto-verificado y aditivo por pais.

#### Resolución condensada — Faceta 1

- **Costura (ES→genérico):** country_code se mantiene FUERA de vehicle (la unica arista de pais es entity_ulid->entity.country_code, decision 0052:36-38) para no reescribir 2.3M filas. Los dos moldes ES residuales: (1) currency CHAR(3) DEFAULT 'EUR' que BULK_INSERT_VEHICLES (_core/sql.py:12-23, 14 cols) NO fija -> todo mercado hereda EUR; (2) NUMERIC(12,2) y el techo de saneo asociado moldeados a EUR. photo_hash existe (0003:18) pero 0% poblada (ruta = faceta 13). El UNIQUE(entity_ulid, deep_link):25 materializa 2 filas para el mismo coche en 2 plataformas (over-count estructural ~131.8K).
- **Fix:** 1) NUNCA anadir country_code a vehicle (mantener derivacion via entity; tripwire de CI). 2) Hacer que los conectores ESCRIBAN currency explicitamente: anadir currency a la lista de columnas de BULK_INSERT_VEHICLES (_core/sql.py:13-14) y validarla contra ISO 4217 en frontera, en vez de confiar en el DEFAULT 'EUR'. 3) Dejar la poblacion de photo_hash a la faceta 13 (writer + backfill). 4) MANTENER el UNIQUE y MEDIR el over-count por pais (facetas 20/22), nunca colapsarlo a ciegas ni anadir country_code para 'arreglarlo'.
- **Adversarial:** Un conector no-EUR (UK/JP/PL) que no fije currency inserta filas con 'EUR' heredado -> 8000 GBP ~ 8000 EUR aguas abajo (faceta 9), CRITICAL latente. NUMERIC(12,2) aguanta la magnitud JPY; el dano JP real es PRICE_MAX=5M (faceta 11) nulando coches normales, no el ancho de columna. DE/FR/IT/PT son inocuos para moneda (EUR comun) pero su over-count cruza frontera si 8/22 no separan por pais. Anadir country_code a vehicle dispararia el rewrite de 2.3M filas.
- **Sellado multi-vía:** Via 1: tras 0052/0053 toda fila ES byte-identica (relabel 1:1). Via 2: cada vehicle.currency ∈ ISO 4217 y coherente con entity.country_code (sin EUR por defecto mudo). Via 3: over-count del UNIQUE servido como +/-dup_ci POR PAIS (faceta 20), nunca contador inflado silencioso. Via 4: assert de CI 'vehicle no tiene columna country_code' (detonante del rewrite 2.3M).
- **Herramienta NEXT-LEVEL:** pycountry (ISO 3166-1/-2 + ISO 4217 currency data) — LGPL-2.1 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530]. De-moldea currency CHAR(3) DEFAULT 'EUR' a dimension validada por autoridad ISO 4217 en frontera del conector (uso build/config-time -> LGPL no-issue, :532). Complemento: Frictionless Framework (Table Schema) — MIT — https://github.com/frictionlessdata/frictionless-py [VERIFIED :337] para versionar la fila vehicle como contrato de datos.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-2"></a>

### Faceta 2 — Timeline append-only de eventos (`vehicle_event`)

> **Append-only · hueco de escala/payload (no ES-puro).** Falta `UNIQUE` de GONE + ENUM/partición (Mejora P3); payload sin `currency`.

#### (a) Verificacion de code_hints [VERIFIED]
- `migrations/0003_vehicles_events.sql:33-42` — tabla `vehicle_event`: `event_ulid TEXT PRIMARY KEY` (:34); FKs `vehicle_ulid`/`entity_ulid` con `ON DELETE CASCADE` (:35-36); `event_type TEXT NOT NULL CHECK (event_type IN ('NEW','GONE','PRICE_CHANGE','PHOTO_CHANGE','KM_CHANGE'))` (:37-38); `old_value JSONB` + `new_value JSONB` (:39-40); `observed_at TIMESTAMPTZ NOT NULL DEFAULT now()` (:41). [VERIFIED]
- Indices: `idx_event_vehicle` (:44), `idx_event_entity_time (entity_ulid, observed_at)` (:45), `idx_event_type` (:46). [VERIFIED]
- **NO existe `UNIQUE(vehicle_ulid,event_type)`** ni ninguna UNIQUE secundaria — leida la definicion entera 33-46. [VERIFIED]
- **NO hay particionado** — es `CREATE TABLE`, no `PARTITION BY observed_at`. [VERIFIED ausencia]
- `event_type` es **CHECK textual sobre TEXT**, no ENUM. El next_level (promover a ENUM + particionar por `observed_at`) **no existe hoy**. [VERIFIED ausencia]
- **Append-only de facto**: los TRES unicos escritores son INSERT puro y no hay UPDATE/DELETE de `vehicle_event` en el pipeline:
  - `_INSERT_GONE_EVENT` (`pipeline/delta.py:94-98`) — `INSERT ... VALUES (...,'GONE',$4::jsonb,NULL)`. [VERIFIED]
  - `_BULK_INSERT_DELTA_EVENTS` (`pipeline/delta.py:369-376`) — bulk unnest de PRICE/KM/PHOTO_CHANGE. [VERIFIED]
  - `BULK_INSERT_EVENTS` (`pipeline/platform/_core/sql.py:46-52`) — bulk NEW. [VERIFIED]
- **La dedup de GONE vive SOLO en codigo** (no en el esquema):
  - `emit_gone_events` (`delta.py:134-138`): `SELECT 1 FROM vehicle_event WHERE vehicle_ulid=$1 AND event_type='GONE' LIMIT 1` antes de insertar -> `continue` si ya existe. [VERIFIED]
  - `reconcile_gone` (`delta.py:264-266`): si `_MARK_GONE` devuelve `"UPDATE 0"` (carrera/re-run) -> `continue` sin emitir el GONE. [VERIFIED]

#### (b) El mecanismo al atomo
La tabla es el **libro mayor inmutable** de la huella historica: una fila por transicion observada de un coche. `old_value`/`new_value` JSONB capturan el antes/despues semantico (p.ej. `{"price": 1752.0}` -> `{"price": 1.0}`). El `observed_at DEFAULT now()` ancla la flecha del tiempo; el orden del timeline es por `observed_at` (de ahi `idx_event_entity_time`). El PK `event_ulid` es opaco (ULID monotono-lexicografico), country-blind por construccion: la tabla nunca mira `country_code`, solo cuelga de `vehicle_ulid`/`entity_ulid`. La inmutabilidad no esta IMPUESTA por el motor (no hay trigger anti-UPDATE ni revocacion de privilegios); es una **convencion respetada por los escritores**. El CHECK de 5 valores es la unica validacion de dominio: un `event_type` fuera de la lista es rechazado a nivel fila, pero el coste es un re-parse textual del literal en cada INSERT y un plan que no puede usar el dominio como ENUM ordenado.

#### (c) La costura ES->generico
El esquema YA es ~100% pais-agnostico: opera sobre ULIDs opacos + JSONB + timestamps, sin un solo literal ES/EUR en la DDL. Las tres costuras reales son de ESCALA y de PAYLOAD, no de pais:
1. **Falta de UNIQUE** -> la idempotencia de GONE es responsabilidad de cada emisor; un cuarto escritor (un conector nuevo de pais #2) que ignore el patron de dedup duplica GONE en un log que se asume inmutable. Es un hueco GLOBAL que se agrava al multiplicar conectores por pais.
2. **`event_type` textual + tabla sin particionar** -> a escala de serving (timeline pan-EU de millones de filas/pais) el CHECK textual y el heap unico degradan barrido y vacuum.
3. **Payload PRICE_CHANGE sin `currency`** -> `diff_vehicle` (`delta.py:319-324`) emite `old_value={"price":...}`, `new_value={"price":...}` SIN moneda; en multi-moneda el evento es ambiguo (8000 GBP vs 8000 EUR indistinguibles al servir el historico). Acopla con la faceta 9 (FX).

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT (multi-conector)**: cada pais suma conectores; sin `UNIQUE(vehicle_ulid,event_type)` la garantia "una sola baja por coche" depende de que CADA emisor replique el `SELECT 1 ... LIMIT 1`. Un emisor edge-set descuidado (estilo group_subastas) duplica GONE -> el timeline "inmutable" miente sobre cuantas bajas hubo (audit P4 ya conto 1.823 bajas silenciosas por el fallo simetrico).
- **No-UE / escala JP**: timeline de millones de eventos/pais sobre heap unico -> `idx_event_entity_time` crece sin particion; los barridos por ventana temporal (serving del historico) escanean particiones inexistentes.
- **Ruido multi-moneda**: un PRICE_CHANGE de un coche JP/UK servido junto a uno ES es numericamente ambiguo sin `currency` en el payload.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado** = (1) invariante append-only PROBADO mecanicamente: ningun camino del pipeline emite UPDATE/DELETE sobre vehicle_event; (2) idempotencia de GONE garantizada por esquema (indice parcial UNIQUE) ademas de por codigo; (3) `event_type` migrado a ENUM y tabla particionada por `observed_at` sin perder los 5 valores vivos en produccion; (4) payload de cambio de precio porta `currency`.
- **Via 1 (test)**: property-based — generar secuencias arbitrarias de (NEW, re-seen, GONE, re-run, carrera) y asertar invariantes: jamas dos GONE para el mismo `vehicle_ulid`; jamas un evento muta/desaparece; el conteo de GONE == coches retirados distintos.
- **Via 2 (ortogonal, DB)**: `SELECT vehicle_ulid, COUNT(*) FROM vehicle_event WHERE event_type='GONE' GROUP BY 1 HAVING COUNT(*)>1` debe devolver 0 filas en produccion (auditoria directa, independiente del codigo emisor).
- **Via 3 (adversarial)**: introducir deliberadamente un emisor que NO dedup-ee y confirmar que el indice parcial `UNIQUE` lo RECHAZA a nivel motor (fail-closed), no que pase silencioso.
- **Via 4 (migracion)**: el cambio CHECK->ENUM y la particion deben dejar `SELECT count(*) , event_type` byte-identico antes/despues (cero perdida, additive).

#### (f) Herramienta NEXT-LEVEL que lo eleva
**Hypothesis** (property-based testing) — MPL-2.0, EUR0=True — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320]. Eleva la inmutabilidad y la no-duplicacion de GONE de "convencion respetada por los escritores" a **invariante probado por maquina**: Hypothesis genera y MINIMIZA el contraejemplo (la secuencia mas simple de emisiones que duplica una baja o muta el log), y el contraejemplo hallado se congela como regression-fixture determinista [VERIFIED NEXT-LEVEL.md:323]. Cierra exactamente el hueco "la dedup vive solo en codigo". Complementos verificados: **in-toto** (Apache-2.0, https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:143]) para hacer el log tamper-evident y atestiguable por terceros; **sraoss/pg_ivm** (PostgreSQL License, https://github.com/sraoss/pg_ivm [VERIFIED NEXT-LEVEL.md:764]) para servir frescura O(celdas) derivada del timeline sin REFRESH. La particion por `observed_at` y el indice parcial UNIQUE son DDL nativa de Postgres (no requieren dependencia externa).

#### Resolución condensada — Faceta 2

- **Costura (ES→genérico):** El esquema es country-blind por construccion (ULIDs+JSONB+timestamps, cero literal ES/EUR en migrations/0003:33-46). Las costuras son de ESCALA y PAYLOAD, no de pais: (1) falta UNIQUE(vehicle_ulid,event_type) -> idempotencia de GONE delegada a cada emisor (delta.py:134-138, :264-266), se agrava al multiplicar conectores por pais; (2) event_type CHECK textual + heap sin particionar degradan a escala de serving pan-EU; (3) payload PRICE_CHANGE sin currency (delta.py:319-324) es ambiguo en multi-moneda.
- **Fix:** 1) Anadir indice parcial UNIQUE sobre (vehicle_ulid) WHERE event_type='GONE' (idempotencia en el motor, no solo en codigo). 2) Migrar event_type TEXT+CHECK -> ENUM de los 5 valores vivos + convertir vehicle_event a tabla particionada por RANGE(observed_at), additive y byte-identica en conteos. 3) Anadir currency al payload JSONB de PRICE_CHANGE en diff_vehicle (acopla con faceta 9). Ninguno toca country_code: la tabla sigue colgando de vehicle_ulid/entity_ulid.
- **Adversarial:** Multi-conector DE/FR/IT/PT: sin UNIQUE, un emisor edge-set que no replique el SELECT 1...LIMIT 1 duplica GONE en un log asumido inmutable (audit P4: 1.823 bajas silenciosas por el fallo simetrico). Escala no-UE/JP: timeline de millones de eventos/pais sobre heap unico sin particion degrada barrido/vacuum y los indices por ventana temporal. Ruido multi-moneda: PRICE_CHANGE sin currency es numericamente ambiguo al servir historico mixto GBP/EUR/JPY.
- **Sellado multi-vía:** Sellado = append-only probado (ningun UPDATE/DELETE en el pipeline) + idempotencia GONE por esquema + ENUM/particion sin perdida + currency en payload. Multi-via: (1) property-based sobre secuencias arbitrarias de emision (jamas 2 GONE/coche, jamas mutacion); (2) auditoria DB ortogonal GROUP BY HAVING COUNT(*)>1 == 0 filas; (3) adversarial: emisor sin dedup RECHAZADO por el indice UNIQUE (fail-closed); (4) migracion CHECK->ENUM+particion deja conteos byte-identicos.
- **Herramienta NEXT-LEVEL:** Hypothesis (property-based testing) — MPL-2.0, EUR0=True — https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320]. Prueba+minimiza el contraejemplo que rompe la inmutabilidad/no-duplicacion y lo congela como golden, elevando la dedup de 'solo-codigo' a invariante de maquina. Complementos: in-toto (Apache-2.0, https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:143]) para log tamper-evident; sraoss/pg_ivm (PostgreSQL License, https://github.com/sraoss/pg_ivm [VERIFIED NEXT-LEVEL.md:764]) para frescura servida sin REFRESH.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-3"></a>

### Faceta 3 — Motor de resolución union-find determinista

> **Motor invariante (país-agnóstico).** Acopla Hole #2 (partición por país) y la escala O(n²) intra-bloque.

#### (a) code_hints VERIFICADOS
- `pipeline/identity/cluster_vehicles.py:197-231` [VERIFIED] clase `UnionFind`: `_init` :204-207 (parent[x]=x, rank=0), `find` :209-214 con **path-halving** explicito `self._parent[x]=self._parent[self._parent[x]]` :212, `union` :216-224 **union-by-rank** (compara rank :220-221, promueve :223-224), `components()` :226-231 (agrupa por `find(node)`).
- `_select_canonical` :493-501 [VERIFIED]: `min(members, key=...)` con clave `(str(first_seen or "9999-99-99"), uid)` = **first_seen mas antiguo, desempate ulid asc**; el centinela "9999-99-99" empuja los first_seen NULL al final.
- `_build_cluster_table` :509-562 [VERIFIED]: init de TODOS los ulids :525-526, union por aristas con guard de pertenencia :527-529, rango de senal por raiz `_SIGNAL_RANK={none:0,firma:1,photo_url:2,both:3}` :532-539, fila por vehiculo con `match_signal = sig if sz>1 else 'none'` :556.
- `_write_to_pg` :570-652 [VERIFIED]: **idempotente** - `DELETE FROM vehicle_cluster / vehicle_cluster_run WHERE cluster_run_id=RUN_ID` :601-606, INSERT run con `vam_verified=FALSE` HARDCODE :613, `execute_values` page_size=5000 :639-650; todo en **una** `with conn:` txn :598.
- `assert len(cluster_rows) == n_in` :934-936 [VERIFIED]: cobertura exacta (cada vehiculo cargado produce exactamente una fila de cluster).

#### (b) Mecanismo al atomo
El resolver es una funcion pura grafo->particion. Nodos = `vehicle_ulid` (ULID opaco, **country-blind**). Aristas = union de Signal A (foto) + Signal B (firma), cada una etiquetada. `UnionFind` colapsa componentes conexas con dos optimizaciones que garantizan casi-O(alfa(n)): path-halving (cada `find` acorta el camino a la mitad) + union-by-rank (el arbol mas bajo cuelga del mas alto). `components()` devuelve `{raiz:[miembros]}`. Por componente se elige un canonico determinista (first_seen+ulid) y se emite una fila por miembro con el `match_signal` = senal mas fuerte presente en el cluster (both>photo>firma>none). La escritura borra-y-reescribe el `run_id` en una transaccion: **misma entrada -> mismos clusters byte-identicos**, y re-correr es un no-op idempotente. El `assert n_in==rows` es la prueba mecanica de que la particion cubre el universo exactamente-una-vez.

#### (c) Costura ES->generico
El motor **ya es pais-agnostico**: opera sobre ULIDs opacos y aristas; no lee `country_code` ni `province`. La unica costura es **indirecta**: el resolver hereda las aristas que construyen Signal A/B (facetas 6/7/8). Si esas aristas cruzan frontera (faceta 8), el union-find las colapsa fielmente - el motor amplifica el fallo upstream sin saberlo. Fix exacto del motor en si: **ninguno en la matematica**; el determinismo y la idempotencia son universales. El acoplamiento real es con faceta 5 (aislamiento por pais): `_write_to_pg` borra-y-reescribe el `run_id` **GLOBAL** :601-606, asi que un re-run recomputa TODO el espacio canonico (re-toca ES al onboardear el pais #2). Fix: scopear el DELETE/rewrite por `country_code` (run-per-country) inyectando un predicado de scope en `_load_vehicles` :258 - pero eso es faceta 5; el motor solo necesita aceptar el scope, no reescribir su algebra.

#### (d) Riesgo adversarial
- **Escala (DE/FR/IT a 2.3M+):** el union-find vive **en memoria** (dicts `_parent`/`_rank`) y el emparejamiento Signal B es **O(n^2) intra-bloque** - `for i in range(len(bucket)): for j in range(i+1,len(bucket))` :406-407 [VERIFIED]. Un bloque firma grueso (faceta 24: grano geo grueso -> bucket enorme) dispara el cuadratico. Anadir un pais duplica n y el espacio global se recomputa entero.
- **Canonico por timestamp:** `_select_canonical` depende de `first_seen` fiable :498; un conector nuevo (pais #2) con `first_seen` mal poblado o en otra zona horaria elige un canonico distinto -> el cdp/serving apunta a otra fila. El centinela "9999-99-99" es comparacion **string**, fragil si el formato de fecha del conector difiere.
- **Re-run global:** una sola pasada recomputa ES + pais nuevo juntos (acopla faceta 5) -> el canonico ES certificado se perturba en cada alta.

#### (e) Sellado + verificacion multi-via
- **Via 1 (idempotencia por recomputacion):** re-ejecutar el mismo `run_id` (DELETE+rewrite) debe producir clusters **byte-identicos** - diff de `vehicle_cluster` pre/post = 0. Es la via ortogonal nativa del sello.
- **Via 2 (cobertura exacta):** `assert len(cluster_rows)==n_in` :934 + Check 3 anti-FP (`clustered==available==distinct`) :880-892 - cada vehiculo exactamente una vez.
- **Via 3 (determinismo cross-maquina):** correr en dos hosts limpios con el mismo dump -> mismo hash de la tabla de clusters.
- **Via 4 (independiente):** un segundo motor ER (pyJedAI) sobre la misma entrada debe **concordar** en el conjunto canonico dentro del intervalo certificado; divergencia bloquea el sello.

#### (f) Herramienta nivel-inalcanzable
**pyJedAI** (Apache-2.0, EUR0) - https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:543-549]: segunda via ER **arquitectonicamente independiente** corrida sobre la misma entrada; el sello exige que el motor determinista (piso), Splink (probabilistico) y pyJedAI concuerden en el conteo canonico dentro del intervalo ER-Evaluation. Convierte "creemos que esta bien" en "tres motores ER independientes concuerdan" - la doctrina de 2-vias del bible hecha mecanica. **datasketch MinHash-LSH** (MIT, EUR0) - https://github.com/ekzhu/datasketch [VERIFIED NEXT-LEVEL.md:535-541]: retira el O(n^2) intra-bloque por blocking sub-cuadratico language-neutral, el fix exacto del riesgo de escala a 2.3M. Complementos: **Splink** (MIT) capa probabilistica que aisla la zona gris; **ER-Evaluation** (AGPL-3.0, solo offline) para el +/-IC certificado.

#### Resolución condensada — Faceta 3

- **Costura (ES→genérico):** El motor es pais-agnostico por construccion (ULIDs opacos, sin country_code); su unica costura es el DELETE+rewrite GLOBAL del run_id en _write_to_pg:601-606 que recomputa TODO el espacio canonico (re-toca ES al alta del pais #2). Acopla faceta 5.
- **Fix:** El algebra union-find no cambia. Inyectar un predicado de scope (country_code) en _load_vehicles:258 y en el DELETE/rewrite de _write_to_pg:601-606 para run-per-country; el motor solo acepta el scope, no reescribe su matematica. Mantener assert n_in==rows por scope.
- **Adversarial:** Union-find en memoria + Signal B O(n^2) intra-bloque (cluster_vehicles.py:406-407) escala mal a 2.3M+ DE/FR/IT; un bloque firma grueso (grano geo, faceta 24) dispara el cuadratico. _select_canonical depende de first_seen fiable (:498) y compara el centinela '9999-99-99' como string -> conector pais#2 con fecha mal poblada u otra TZ elige canonico distinto. Re-run global recomputa ES+pais nuevo juntos.
- **Sellado multi-vía:** Via1 idempotencia: re-run del mismo run_id (DELETE+rewrite) da clusters byte-identicos (diff=0). Via2 cobertura: assert len(cluster_rows)==n_in (:934) + Check3 clustered==available==distinct (:880-892). Via3 determinismo cross-host: mismo dump -> mismo hash de tabla. Via4 independiente: pyJedAI concuerda en el canonico dentro del IC certificado.
- **Herramienta NEXT-LEVEL:** pyJedAI (Apache-2.0, https://github.com/AI-team-UoA/pyJedAI) [VERIFIED NEXT-LEVEL.md:543-549] = 2a via ER independiente para certificar el sello a 3 motores; datasketch MinHash-LSH (MIT, https://github.com/ekzhu/datasketch) [VERIFIED :535-541] retira el O(n^2) intra-bloque. Complementos: Splink (MIT) zona gris probabilistica; ER-Evaluation (AGPL-3.0, offline) para +/-IC certificado.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-4"></a>

### Faceta 4 — Overlay no-destructivo + gate VAM cero-confianza

> **Gate cero-confianza.** `vam_verified` es per-run, no per-país → acopla Hole #2.

#### (a) Code hints [VERIFIED]
- [VERIFIED migrations/0023_vehicle_cluster.sql:21-34] `vehicle_cluster_run`: PK `cluster_run_id` TEXT caller-supplied (:22), `scope` TEXT = condicion SQL que filtro los vehiculos (:26), `blocking_rules` JSONB para reproducibilidad (:27), `n_in/n_clusters/n_merged` (:28-30), **`vam_verified BOOLEAN NOT NULL DEFAULT FALSE` (:31)**, `vam_verdict_id BIGINT REFERENCES verification_verdict(id)` (:32).
- [VERIFIED migrations/0023:39-48] `vehicle_cluster` per-listing: FK a `vehicle(vehicle_ulid) ON DELETE CASCADE` (:42-43, NO muta vehicle), `match_signal` 'photo_url'|'firma'|'both' (:44), PK `(cluster_run_id, vehicle_ulid)` (:47). Indices :50-52.
- [VERIFIED migrations/0023:57-76] `v_canonical_vehicle` VIEW sirve SOLO el run mas reciente con `vam_verified=TRUE` via subquery `ORDER BY run_at DESC LIMIT 1` (:70-76). Sin run TRUE -> la vista es VACIA.
- [VERIFIED migrations/0023:78-81] Rollback = DROP VIEW + DROP TABLE; `vehicle` intacto.
- [VERIFIED cluster_vehicles.py:598-606] `_write_to_pg` idempotente: `DELETE FROM vehicle_cluster` + `DELETE FROM vehicle_cluster_run WHERE cluster_run_id=%s` antes de reescribir.
- [VERIFIED cluster_vehicles.py:608-626] INSERT de `vehicle_cluster_run` con **`vam_verified` hardcoded a `FALSE`** en el VALUES (:613). El writer NUNCA puede nacer verificado.
- [VERIFIED migrations/0023:16] comentario de cabecera: 'vam_verified=FALSE until the Director manually gates it TRUE'.

#### (b) Mecanismo al atomo
Dos tablas overlay + una vista. El resolver escribe SIEMPRE `vam_verified=FALSE` (cluster_vehicles.py:613). El unico camino a TRUE es un `UPDATE` manual del Director tras revisar la muestra (faceta 23). La vista `v_canonical_vehicle` no expone NADA salvo el ultimo run TRUE (0023:70-76). Tres estados de servicio emergen como atomos: (1) hay run TRUE reciente -> se sirve resolucion sellada; (2) hay runs pero ninguno TRUE -> vista VACIA -> el serving DEBE degradar a filas `vehicle` crudas + cota `dup_ci` (faceta 20), jamas a '0 coches'; (3) rollback -> DROP no-destructivo, cada `vehicle_ulid` sobrevive (0023:78-81). El gate es cero-confianza por construccion: el sistema se niega a servir una resolucion que un humano no haya firmado, y el writer no tiene poder para auto-aprobarse.

#### (c) Costura ES->generico
Hoy hay **UN solo `vam_verified` por `cluster_run_id`** (0023:31), y el run es una pasada GLOBAL (carga sin filtro de pais - faceta 5). El boolean es por-run, no por-pais: no se puede gatear DE sin gatear lo que comparta el run, ni revertir un pais sin tocar el espacio canonico del otro. La vista filtra por run-id, no por `country_code`.

#### (d) Riesgo adversarial concreto
Al onboardear pais #2: un run global mezcla filas ES+DE bajo un unico boolean. Flipear `vam_verified=TRUE` para servir DE sirve TAMBIEN cualquier re-cluster ES no re-revisado (o al reves), violando la cero-confianza por pais. Peor: si por degradacion la subquery (:70-76) no halla run TRUE, la vista cae a vacia y un serving ingenuo devolveria '0 coches' para TODOS los paises (FR/IT/PT incluidos) en vez de degradar a crudo+cota. Ruido: un `cluster_run_id` colisionado entre dos campanas de pais borraria (DELETE :601-606) el run del otro.

#### (e) Sellado + verificacion multi-via
1. Test de gate por-pais: sellar DE (UPDATE su vam por-pais a TRUE), aseverar que `v_canonical_vehicle` SIGUE sirviendo el ES previamente sellado sin cambio (snapshot diff cero).
2. Test de degradacion honesta: sin run verificado -> vista vacia -> la API devuelve filas `vehicle` crudas + `dup_ci`, NUNCA count=0 (romper el gate y observar el fallback).
3. Test de no-destructividad: `SELECT count(*) FROM vehicle` identico antes/despues de DROP de overlay (invariante 0023:78-81).
4. Via cripto-independiente (tool): re-derivar el set canonico desde los content-hashes atestiguados debe dar la MISMA vista; mutar un byte -> verify FALLA.

#### (f) Herramienta NEXT-LEVEL
[VERIFIED NEXT-LEVEL.md:640-646] **in-toto (Apache-2.0)** https://github.com/in-toto/in-toto. Convierte `vam_verified` de fila mutable a ATESTACION firmada tamper-evident que liga {country_code, cluster_run_id, intervalo [cota_inf,cota_sup], set de migraciones, hashes de inputs, verdicts de quorum VAM} -> set canonico servido, firmada con Sigstore cosign keyless (OIDC gratis). Un tercero (auditor/comprador/regulador del pais) PRUEBA que el 'esto-esta-sellado' salio exactamente de esos inputs sin confiar en nosotros. Complementos verificados: transitions/pytransitions (MIT, NEXT-LEVEL:595) para la FSM del ciclo FALSE->VERIFIED->REOPENED guard-gated; pg_ivm (PostgreSQL License, NEXT-LEVEL:764) para que la vista materializada de servicio nunca quede vieja sin cron.

#### Resolución condensada — Faceta 4

- **Costura (ES→genérico):** Un unico vam_verified por cluster_run_id (migrations/0023:31) sobre una pasada global sin filtro de pais (cluster_vehicles.py:_load_vehicles): el boolean es per-run, no per-country; la vista v_canonical_vehicle filtra por run-id (0023:70-76), no por entity.country_code. No se puede gatear/revertir un pais sin tocar el espacio canonico del resto.
- **Fix:** Llevar el gate al grano (cluster_run_id, country_code): tabla hija vehicle_cluster_run_country(cluster_run_id, country_code, vam_verified DEFAULT FALSE, vam_verdict_id) -o columna country en el grano del gate-, y reescribir v_canonical_vehicle para JOIN entity.country_code y filtrar el ultimo run vam_verified=TRUE POR pais. El fallback de vista-vacia degrada a filas vehicle crudas + dup_ci (faceta 20), nunca a count=0. _write_to_pg sigue escribiendo FALSE por (run,pais).
- **Adversarial:** Pais #2 (DE/FR/IT/PT): un run global mezcla ES+DE bajo un boolean unico -> sellar DE expone re-cluster ES no revisado (rompe cero-confianza por pais). Si la subquery no halla run TRUE la vista cae a vacia y un serving ingenuo devuelve '0 coches' para todos los paises en vez de degradar a crudo+cota. cluster_run_id colisionado entre campanas borra (DELETE) el run ajeno.
- **Sellado multi-vía:** (1) Sellar DE deja intacto el ES ya servido (snapshot diff = 0). (2) Sin run verificado -> API sirve vehicle crudo + dup_ci, jamas count=0 (romper el gate y observar fallback). (3) count(*) vehicle identico tras DROP del overlay (no-destructividad, 0023:78-81). (4) Via cripto: re-derivar el set desde content-hashes atestiguados reproduce la vista; mutar un byte -> in-toto verify FALLA.
- **Herramienta NEXT-LEVEL:** in-toto (Apache-2.0) https://github.com/in-toto/in-toto [VERIFIED NEXT-LEVEL.md:643] - atestacion firmada tamper-evident del sello, verificable por terceros sin confiar en el emisor. Complementos: transitions/pytransitions (MIT, NEXT-LEVEL:595) FSM del ciclo vam; pg_ivm (PostgreSQL License, NEXT-LEVEL:764) frescura de la vista servida.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-5"></a>

### Faceta 5 — Aislamiento del sello por país (scoping + revertibilidad independiente)

> **Hole #2 — CIERRA por diseño** (partición del clustering por `country_code`).

#### (a) Verificacion de code_hints [VERIFIED]
- `RUN_ID = "vehicle-identity-det-v1"` [VERIFIED pipeline/identity/cluster_vehicles.py:77] — **una sola** constante a nivel de modulo. Existe exactamente UN run id para todo el motor; no es funcion del pais.
- `RESOLVER = "union-find-deterministic"` [:78], `RESOLVER_VERSION = "1.0.0"` [:79].
- `SCOPE_CONDITION = "status = 'available'"` [VERIFIED :80] — **sin predicado de pais**.
- `_load_vehicles`: `SELECT ... FROM vehicle v LEFT JOIN entity e ON e.entity_ulid=v.entity_ulid WHERE v.status = 'available'` [VERIFIED :242-259, WHERE :258] — carga TODO vehiculo disponible de la BD, ciego al pais. El JOIN a entity ya esta presente (trae `e.province_code` :255) pero NO filtra ni selecciona `country_code`.
- `_write_to_pg`: dentro de un unico `with conn:` (:598) hace `DELETE FROM vehicle_cluster WHERE cluster_run_id = %s` (RUN_ID) [:601-603] y `DELETE FROM vehicle_cluster_run WHERE cluster_run_id = %s` (RUN_ID) [:604-606], luego re-INSERT completo; `vam_verified` se inserta literal **FALSE** en el VALUES [:613].
- `vam_verified BOOLEAN NOT NULL DEFAULT FALSE` [VERIFIED migrations/0023_vehicle_cluster.sql:31] — **un** booleano por fila de `vehicle_cluster_run`.
- `v_canonical_vehicle` sirve `... WHERE vam_verified = TRUE ORDER BY run_at DESC LIMIT 1` [VERIFIED :70-76] — sirve el UNICO ultimo run verificado **global**.
- Rollback global: `DROP VIEW/TABLE` en la cola de la migracion [:78-81].

#### (b) Mecanismo al atomo
El resolver es **una pasada global de una sola corrida**. Cada ejecucion: (1) carga todas las filas `status='available'` de TODAS las entidades/paises; (2) computa union-find sobre ese espacio entero; (3) DELETE de las filas previas de `vehicle-identity-det-v1` y reescritura; (4) escribe UNA fila `vehicle_cluster_run` con UN `vam_verified=FALSE`. El Director voltea ese unico booleano a TRUE para sellar. La vista sirve el ultimo run TRUE global. Resultado: el sello es un objeto **todo-o-nada global** — no hay run por pais, ni flag verificado por pais, ni particion canonica por pais. El rollback (`DROP`) tambien es global.

#### (c) Costura ES -> generico
El invariante ACCIDENTAL "solo hay un pais (ES), luego una corrida global == una corrida ES" se vuelve falso en el instante en que aterriza un pais #2. La costura es la **ausencia de la dimension pais en el ciclo de vida del run**:
- identidad del run: `RUN_ID` es constante, no `f(country)`.
- scope de carga: `SCOPE_CONDITION` no tiene predicado de pais.
- flag verificado: un `vam_verified` por run, no por `(run, country)`.
- vista canonica: sirve el ultimo run verificado global, mezclando paises.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT onboarding:** la primera corrida tras anadir el pais #2 hace `DELETE ... WHERE cluster_run_id=RUN_ID` **global** y recomputa el canonico ES ya sellado -> un sello ES certificado queda **silenciosamente invalidado/perturbado** por la importacion de un pais ajeno, con pipeline en verde (regresion invisible).
- El unico `vam_verified` **acopla los gates**: no puedes certificar DE sin re-exponer un ES re-clusterizado bajo el mismo flag; voltear el booleano sirve TODOS los paises a la vez.
- El rollback de un sello DE malo exige discriminar filas DE dentro de un canonico compartido — hoy imposible porque las filas del run no estan scoped por pais.
- **no-UE / ruido:** la seleccion canonica es `first_seen`-min (facet 3, `_select_canonical`); un pais con reloj `first_seen` menos fiable re-desempata el espacio GLOBAL en cada re-run.

#### (e) Criterio de sellado + verificacion multi-via
- **Invariante de aislamiento:** re-correr el resolver para el pais B produce filas `vehicle_cluster` BYTE-identicas para el pais A (diff de las filas A-scoped pre/post corrida B; delta cero = aislamiento probado).
- `vam_verified` por pais independientemente volteable y revertible; golden: sella ES, onboarda DE, aserta que `vam_verified(ES)` sigue TRUE y el row-set canonico ES intacto (monotonia, cero regresion ES = estrella polar del proyecto).
- **Multi-via:** (1) diff SQL del canonico A-scoped pre/post; (2) recomputo del resolver solo-A en aislamiento y asercion de clusters identicos (via ortogonal = garantia de determinismo de facet 3); (3) atestacion de que la vista servida para A referencia solo el run id de A.

#### (f) Herramienta NEXT-LEVEL
**in-toto** (Apache-2.0, https://github.com/in-toto/in-toto) [VERIFIED NEXT-LEVEL.md:143] — cada corrida scoped-por-pais emite una atestacion in-toto firmada que liga {git-SHA del codigo, content-hashes de las filas de entrada de ESE pais} -> {set canonico del pais, veredicto vam_verified}. El sello por pais deja de ser un booleano compartido y pasa a ser un **certificado no-repudiable e independientemente verificable** scoped a las entradas de un pais; el onboarding/rollback de otro pais **no puede** alterar la atestacion de un pais sellado (alterar una fila de entrada -> la verificacion de la atestacion FALLA). Companero: **DVC** (Apache-2.0, https://github.com/iterative/dvc) [VERIFIED NEXT-LEVEL.md:151] content-addressa las entradas de cada pais para que una corrida scoped sea bit-reconstruible. Ambos EUR0, solo-CPU.

#### Resolución condensada — Faceta 5

- **Costura (ES→genérico):** El ciclo de vida del run no tiene dimension pais: RUN_ID es una constante de modulo (no f(country)) [cluster_vehicles.py:77], SCOPE_CONDITION='status=\'available\'' sin predicado de pais [:80], _load_vehicles carga toda la BD via WHERE status='available' [:258], _write_to_pg hace DELETE+rewrite del UNICO run id global [:601-606], y hay un solo vam_verified por run [migrations/0023:31] servido global por v_canonical_vehicle (LIMIT 1) [:70-76]. El invariante accidental 'solo hay ES, luego global==ES' se rompe con el pais #2.
- **Fix:** 1) Parametrizar el run id por pais: RUN_ID(cc) = f'vehicle-identity-det-v1::{cc}' (o anadir columna country_code a vehicle_cluster_run y scoping (cluster_run_id,country_code)). 2) Scoped load: SCOPE_CONDITION = "status='available' AND e.country_code = %s" (el JOIN a entity ya existe :257), una pasada por pais. 3) Scoped write: _write_to_pg DELETE/rewrite filtrado por el run id scoped-por-pais, para que re-correr el pais B nunca toque las filas del pais A. 4) Sello por pais: mover vam_verified a clave (run,country) (tabla vehicle_cluster_seal(country_code,cluster_run_id,vam_verified) o columna country en el run); v_canonical_vehicle con DISTINCT ON (country_code) ... WHERE vam_verified ORDER BY country_code, run_at DESC. 5) Rollback por pais: borrar las filas del run scoped de un pais deja intacto el canonico de los demas (el overlay ya es no-destructivo sobre vehicle).
- **Adversarial:** DE/FR/IT/PT: la primera corrida tras anadir el pais #2 hace DELETE global del run id [:601-606] y recomputa el canonico ES ya sellado -> sello ES silenciosamente invalidado con pipeline en verde (regresion invisible). El unico vam_verified acopla gates (no se puede certificar DE sin re-exponer ES bajo el mismo flag; voltear el booleano sirve todos los paises). Rollback de un sello DE malo exige discriminar filas DE en un canonico compartido = hoy imposible. no-UE: first_seen-min re-desempata el espacio global en cada re-run si el reloj del pais es menos fiable.
- **Sellado multi-vía:** Invariante: re-correr el resolver para el pais B deja las filas vehicle_cluster del pais A BYTE-identicas (diff A-scoped pre/post = delta cero). Golden de monotonia: sella ES -> onboarda DE -> aserta vam_verified(ES)=TRUE y row-set canonico ES sin cambio (cero regresion ES). Multi-via: (1) diff SQL canonico A pre/post; (2) recomputo solo-A en aislamiento, clusters identicos (via ortogonal = determinismo facet 3); (3) atestacion de que la vista de A referencia solo el run id de A.
- **Herramienta NEXT-LEVEL:** in-toto (Apache-2.0, https://github.com/in-toto/in-toto) [VERIFIED NEXT-LEVEL.md:143]: atestacion firmada por corrida scoped-por-pais ligando {git-SHA, content-hashes de las filas del pais} -> {canonico del pais, veredicto vam_verified}; el sello por pais se vuelve certificado no-repudiable e independientemente verificable, y onboardear otro pais no puede alterar la atestacion de un pais sellado. Companero: DVC (Apache-2.0, https://github.com/iterative/dvc) [VERIFIED NEXT-LEVEL.md:151] para content-addressing de las entradas por pais (corrida bit-reconstruible). Ambos EUR0, CPU.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-6"></a>

### Faceta 6 — Signal A: identidad por foto-URL

> **Calibración ES (K=12, regex resize).** Mejora P2 (quality-aware). Mecanismo país-agnóstico.

#### (a) Verificacion de code_hints [VERIFIED]
- `PHOTO_HIGH_COLLISION_K = 12` [VERIFIED cluster_vehicles.py:97]. La calibracion esta DOCUMENTADA en el bloque :89-96: muestra de produccion 2026-06-15, 1.689M vehiculos; histograma con 126.754 fotos en cnt=2 y decaimiento suave hasta cnt=11 (5 fotos); el codo real en cnt=12 donde aparecen catalogos confirmados (placeholder BCA 1.752x, render SEAT 220-274x, `coming_soon.jpg` de Flexicar 331x, placeholder Dealerk 83x). 63 URLs cualifican como stock, 126.874 se preservan como senal valida [VERIFIED :89-96].
- `_normalize_photo_url` [VERIFIED :145-163]: strip+lower (:159) -> quita query `_RE_QUERY` (:160) -> quita slash final (:161) -> quita sufijo resize `_RE_RESIZE_SUFFIX` (:162). El regex de sufijos es `[/_-](?:thumb|thumbnail|small|medium|large|\d+x\d+|\d+w)$` [VERIFIED :139-142].
- Indice foto->listings `idx_photo` [VERIFIED :327-331]; `high_collision_photos = frozenset(... if len(bucket) >= K)` [VERIFIED :338-342]; exclusion en el bucle `if norm in high_collision_photos: continue` [VERIFIED :356-358].
- Bucle pareado intra-bucket O(n^2) [VERIFIED :359-375]; guard km=0 `_is_new_car(va) or _is_new_car(vb)` -> `_can_merge_new_cars` [VERIFIED :365-367]; guard cross-generacion `PHOTO_YEAR_SPAN_MAX=2`, `PHOTO_KM_SPAN_MAX=50_000` [VERIFIED :290-291], `_photo_pair_spans_generations` [VERIFIED :294-306] aplicado en :372-373.
- Doctrina: `BLOCKING_RULES[0]` declara "same CDN photo = same physical car [signal A, sufficient alone]" [VERIFIED :100-101], y el guard high-collision como regla 4 [VERIFIED :109-114].

#### (b) Mecanismo al atomo
1. Para cada vehiculo se normaliza `photo_url` a una clave canonica (sin scheme implicito por path, sin query, sin slash final, sin sufijo de resize). Las fotos vacias -> None y no entran al indice.
2. Se construye `idx_photo: norm_url -> [vehicle_ulid...]`. Una clave compartida por >=2 listings es candidata a arista.
3. **Guard de colision-alta**: si una clave la comparten >=12 listings, se marca como catalogo/placeholder y se EXCLUYE entera (un placeholder BCA compartido 1.752 veces jamas genera 1.7K aristas).
4. Para cada bucket valido (<K, >=2) se generan pares O(n^2). Cada par pasa dos guards extra: (i) km=0/NULL -> solo une si comparten VIN no-null (faceta 25/19); (ii) cross-generacion -> si difieren >2 anios-modelo o >50k km, la foto es de catalogo reusada entre generaciones y la arista se descarta (monotono: un duplicado real tiene year+km iguales, span=0, nunca se bloquea).
5. Las aristas supervivientes alimentan el union-find (faceta 3) con senal `'photo_url'`. Signal A es **suficiente sola**: una foto CDN identica basta para declarar el mismo coche fisico, sin precio ni titulo.
6. **Es GLOBAL a proposito**: no lleva dimension pais. Una foto en un CDN compartido es la misma cruzando cualquier frontera; la identidad de la foto es universal.

#### (c) Costura ES->generico
La deteccion descansa en DOS constantes ES-moldeadas: (1) `K=12` es el codo del histograma de CDNs **espanoles** (el comentario :89-96 nombra BCA/SEAT/Flexicar/Dealerk, todas plataformas ES); (2) `_RE_RESIZE_SUFFIX` enumera sufijos de resize **observados en ES**. Ambas son invariantes accidentales del unico inquilino. El mecanismo en si (normalizar->indexar->guard de conteo) es pais-agnostico; lo ES-puro es la CALIBRACION.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT**: una plataforma nacional cuyo placeholder se comparte solo 8-11 veces (sub-K=12) PASA el guard high-collision -> esos 8-11 coches distintos se FUSIONAN en un cluster (over-merge: exactamente el fallo que el guard 1.752x de BCA fue construido para matar, re-armado por debajo del umbral ES).
- **No-UE (JP)**: un CDN que anexa un sufijo de resize que el regex ES no conoce (`=s1200`, `@2x`, `-l.webp`) -> la MISMA foto normaliza a dos cadenas distintas -> el duplicado genuino se PIERDE (under-count), y con `photo_hash` al 0% (faceta 13) no hay respaldo de pixeles.
- **Ruido**: CDNs donde el path es estable pero la imagen cambia por query (`?id=`); el normalizador tira la query (:160) -> dos coches distintos con path-stable URL distinta query -> false-merge.
- **Raiz**: el guard depende del CONTEO de colision, no de la CALIDAD de imagen; un placeholder sub-K se cuela estructuralmente.

#### (e) Criterio de sellado + verificacion multi-via
- **Golden**: set etiquetado (mismo-coche / distinto-coche) de pares foto-URL cosechado gratis POR PLATAFORMA; K + regex deben dar 0 false-merge en el set distinto-coche y recuperar todos los pares mismo-coche.
- **Via 2 (ortogonal, pixeles)**: recomputar cada cluster de Signal A con el hash perceptual + quality gate (PDQ); una arista URL que el hash de pixeles dice que son dos imagenes distintas es una arista falsa -> aflorarla, nunca sellarla en silencio.
- **Via 3 (re-validacion por pais)**: derivar K del codo del histograma de CADA plataforma (no la constante global); asertar que el histograma ES reproduce K=12 byte-identico (cero regresion) mientras cada plataforma nueva recibe su propio K; el anti-FP Check 1 (faceta 22) debe ademas asertar que ningun cluster cruza (country, geo_unit).

#### (f) Herramienta NEXT-LEVEL
**PDQ (facebook/ThreatExchange)** — hash perceptual 256-bit con quality gate incorporado, BSD-3-Clause [VERIFIED NEXT-LEVEL.md:434, URL https://github.com/facebook/ThreatExchange/tree/main/pdq]. Eleva Signal A de identidad-por-cadena-URL (fragil, conteo-dependiente, calibrada-ES) a identidad-por-pixel con exclusion ESTRUCTURAL de imagenes sin estructura: un placeholder featureless se descarta por su quality baja sin importar cuantas veces aparezca, eliminando la dependencia de K y del regex de resize ES. Ruta EUR0: CPU puro sobre fotos YA descargadas en el scrape (cero egress extra), hash inline, persistido en `vehicle.photo_hash` [VERIFIED :436]. Secundaria: **DINOv2** (facebookresearch/dinov2), Apache-2.0 [VERIFIED :442] para "mismo coche fisico, foto distinta" que el match exacto de URL nunca alcanza.

#### Resolución condensada — Faceta 6

- **Costura (ES→genérico):** K=12 (cluster_vehicles.py:97) y _RE_RESIZE_SUFFIX (:139-142) estan calibrados EXCLUSIVAMENTE sobre CDNs ES (muestra 2026-06-15, comentario :89-96 nombra BCA/SEAT/Flexicar/Dealerk). El mecanismo normalizar->indexar->guard-de-conteo es pais-agnostico; lo ES-puro es la calibracion del umbral y la lista de sufijos de resize. La deteccion es COUNT-based, no QUALITY-based.
- **Fix:** (1) K per-host/per-plataforma computado del codo del histograma de colision de cada plataforma, no constante global. (2) Sustituir la identidad URL-string por hash perceptual + quality gate (PDQ) que excluye placeholders por baja quality estructuralmente, eliminando la dependencia de K y del regex resize. (3) _RE_RESIZE_SUFFIX pasa a lista aditiva por country-pack, nunca constante global.
- **Adversarial:** DE/FR/IT/PT: placeholder nacional compartido 8-11x (sub-K) pasa el guard -> 8-11 coches distintos false-merge (re-arma el fallo BCA 1.752x bajo el umbral ES). No-UE/JP: CDN con sufijo resize desconocido (=s1200, @2x, -l.webp) -> misma foto normaliza a dos URLs -> duplicado perdido (under-count) sin respaldo pHash (0%). Ruido: query-string CDNs donde el path es estable pero la imagen cambia -> false-merge tras strip de query (:160).
- **Sellado multi-vía:** Golden por plataforma (pares mismo/distinto-coche, 0 false-merge + recall total). Via 2 ortogonal: recomputar cada cluster Signal A con PDQ pixel-hash y aflorar toda arista URL que el pixel-hash refute. Via 3 por pais: derivar K del histograma de cada plataforma, asertar ES reproduce K=12 byte-identico (cero regresion); anti-FP Check 1 (faceta 22) debe asertar 0 clusters cruzando (country, geo_unit).
- **Herramienta NEXT-LEVEL:** PDQ (facebook/ThreatExchange) — hash perceptual 256-bit + quality gate incorporado. BSD-3-Clause [VERIFIED NEXT-LEVEL.md:434]. URL: https://github.com/facebook/ThreatExchange/tree/main/pdq. Ruta EUR0: CPU sobre fotos ya descargadas, hash inline en el mismo fetch, persistido en vehicle.photo_hash. Secundaria: DINOv2 (facebookresearch/dinov2) Apache-2.0 [VERIFIED :442] para 'mismo coche, foto distinta'.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-7"></a>

### Faceta 7 — Signal B: firma cross-entity (algoritmo de emparejamiento)

> **Mecanismo país-agnóstico.** Sus inputs (clave/moneda/título) son las costuras B#1/B#3/B#4.

#### (a) Code hints — VERIFIED
- `PRICE_TOL_PCT = 0.02` [VERIFIED cluster_vehicles.py:83].
- `_prices_within_tolerance(p_a,p_b)` [VERIFIED cluster_vehicles.py:178-189]: False if either None (:180-181), False if either <=0 (:186-187), else `abs(fa-fb)/min(fa,fb) <= 0.02` (:188-189). Currency-blind by construction.
- firma block index [VERIFIED cluster_vehicles.py:386-398]: `block_key=(make,model,year,km,province)` at :397; make/model lowercased+stripped (:388-389); skips any row missing make/model/year/km/province (:394-395).
- pairwise O(n^2) intra-block loop [VERIFIED :402-450]; only blocks with >=2 members (:403-404).
- km=0 guard [VERIFIED :415-417] delegating to `_is_new_car` (:267-274) / `_can_merge_new_cars` (:277-286) — owned by facets 25/19.
- non-null-price guard [VERIFIED :426-427]: `if va.price is None or vb.price is None: continue`.
- price tolerance applied [VERIFIED :430].
- cross-entity-only guard [VERIFIED :441-442]: `if va.entity_ulid == vb.entity_ulid: continue`.
- title corroboration [VERIFIED :444-447]: `_normalize_title` (:166-175; NFKD -> `encode('ascii','ignore')` :173-174 -> strip non-[a-z0-9]); merge requires `ta and tb and ta == tb`.
- doctrine [VERIFIED BLOCKING_RULES :100-121, firma rule :102-107: "over-merge < under-merge"].

#### (b) Mechanism al atomo
For each block keyed by EXACT (make,model,year,km,province), every unordered pair (i,j) must clear FIVE sequential gates before an edge enters `firma_edges` (later fed to union-find): (1) neither is new-car stock unless shared non-null VIN; (2) both prices non-null; (3) prices within +/-2% of the lower; (4) different entity_ulid; (5) identical ASCII-folded title. Only the conjunction emits `(a,b)`. Each gate is a fail-closed `continue` — any single failure drops the pair (deliberate under-merge bias per doctrine :102-107). The +/-2% divides by `min(fa,fb)` so it is asymmetric-safe; the title gate is the SOLE positive corroborator (cross-platform photos differ, so a matching title is the only cross-entity identity proof once Signal A misses). The cross-entity guard encodes the doctrine that two units from the SAME dealer are distinct physical cars (if re-listed same car, Signal A's shared photo catches it).

#### (c) Costura ES->generico
The block key (:397) is `(make,model,year,km,province)` — COUNTRY-BLIND (bare province, no country_code): in a single-tenant DB "all rows are ES" is an accidental invariant. The +/-2% comparator (:188-189) is CURRENCY-BLIND (raw float compare). The title gate folds to ASCII (:173-174) — Latin-only. Three single-tenant assumptions ride here, but the seam OWNED by facet 7 is the matching-algorithm SHAPE: the five-gate conjunction is correct and country-agnostic AS A MECHANISM; what it consumes (the key, the currency, the title-norm) is injected by facets 8/9/10. Facet 7's own residual seam = the O(n^2) intra-block loop (:406-407) and the assumption "same block ⇒ comparable units", true only until facets 8/9/24 widen the key.

#### (d) Riesgo adversarial
- **DE/FR/IT (EUR)**: two genuinely-distinct dealers list the same common model (VW Golf 2020, 40k km, same province-equivalent) at +/-2% prices with a templated title that ASCII-folds identical -> FALSE firma-merge of two physical cars. Cross-entity+title is the only defense and templated dealer titles ("VW Golf 2.0 TDI") collide trivially.
- **JP/CJK**: `_normalize_title` folds kanji/kana to `''` -> None (:175) -> `ta and tb` falsy -> EVERY JP pair fails the title gate -> total UNDER-merge (Signal B dead in Japan). Fix owned by facet 10 but it bites at facet 7's gate :446.
- **non-EUR (GBP/CHF)**: +/-2% equates 8000 GBP vs 8000 EUR (currency-blind :188). Owned by facet 9.
- **Noise**: short/generic ASCII titles ("Furgoneta","Ocasion") false-corroborate; the non-null-price guard (:426) already killed the NULL-price vacuous-+/-2% collapse (VW Caddy 1,752 -> 1 cluster), but short folded titles remain a collision surface.

#### (e) Sellado + verificacion multi-via
- (1) Determinism golden: `firma_edges` byte-identical across re-runs on the ES corpus (block iteration + set dedup are stable).
- (2) Adversarial fixture: inject a DE-28/ES-28 pair (matching year/km/+/-2%/ASCII-title) and assert NO edge once facet 8 lands — RED today proves the latent cross-border merge.
- (3) Orthogonal: Signal B edges ⊆ an independent ER engine's (pyJedAI/Splink) proposals within the ER-Evaluation interval; divergence beyond the interval blocks the seal.
- (4) Property (Hypothesis): no pair with differing currency/country ever yields an edge.
- (5) Upgrade anti-FP Check 1 (facet 22, cluster_vehicles.py:852) from `DISTINCT province_code` to cross-(country,province) so the seal cannot pass green on a cross-border cluster.

#### (f) Herramienta NEXT-LEVEL
**Splink** (learned Fellegi-Sunter linkage) — MIT — https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:447-453]. Replaces the hand-coded boolean five-gate net with EM-trained m/u weights per comparison (price/title/geo/vin), a CALIBRATED match probability per pair, and an exportable `model.json` artifact that explains every merge via a per-comparison waterfall — re-fit per country, runs EUR0 in-process on DuckDB; unstable-cluster diagnostics auto-flag suspicious components for the gate. The deterministic five-gate net stays the lower-bound FLOOR (Splink only proposes, the VAM gate decides). Recall/candidate layer (not the merge decision): **LaBSE** multilingual semantic blocking (Apache-2.0, https://huggingface.co/sentence-transformers/LaBSE, NEXT-LEVEL.md:455-461) and **datasketch** MinHash-LSH + RapidFuzz (MIT, https://github.com/ekzhu/datasketch, NEXT-LEVEL.md:535-541) widen recall language-neutrally; **pyJedAI** (Apache-2.0, https://github.com/AI-team-UoA/pyJedAI, NEXT-LEVEL.md:543-549) is the independent 2nd ER path for tri-agreement seal certification.

#### Resolución condensada — Faceta 7

- **Costura (ES→genérico):** The Signal B block key `(make,model,year,km,province)` [cluster_vehicles.py:397] and the +/-2% comparator `_prices_within_tolerance` [:178-189] are country- and currency-blind; the ASCII title corroborator `_normalize_title` [:173-174] is Latin-only. The five-gate matching MECHANISM is itself country-agnostic and correct — its INPUTS (key/currency/title-norm) are the seams, owned by facets 8/9/10. Facet 7's own residual seam is the O(n^2) intra-block loop [:406-407] and the 'same block ⇒ comparable units' assumption that holds only until facets 8/9/24 widen the key.
- **Fix:** Keep the five-gate conjunction intact. (1) Consume a CountryFirmaKey that prepends country_code (facet 8); (2) add an explicit mechanical tripwire `assert va['currency']==vb['currency']` before the +/-2% gate at :430 ahead of facet 9's full FX; (3) swap the ASCII title-fold for a script-aware norm (facet 10). For facet 7 proper: bound the intra-block O(n^2) by capping block size and routing oversized blocks through MinHash-LSH candidate generation before the pairwise compare.
- **Adversarial:** EUR neighbors (DE/FR/IT): two distinct dealers, same common model, +/-2% price, templated title that ASCII-folds equal -> false-merge of two physical cars (cross-entity+title insufficient against templated titles). JP/CJK: title folds to '' -> None -> title gate falsy -> Signal B totally dead (under-merge). GBP/CHF: currency-blind +/-2% equates 8000 GBP ~ 8000 EUR. Noise: short generic ASCII titles ('Furgoneta') false-corroborate; the non-null-price guard already neutralized the NULL-price vacuous-+/-2% collapse (VW Caddy 1,752 -> 1).
- **Sellado multi-vía:** (1) Determinism golden — firma_edges byte-identical across re-runs on ES corpus. (2) Adversarial DE-28/ES-28 fixture asserts NO edge (red today = proves latent cross-border merge). (3) Orthogonal — Signal B edges ⊆ pyJedAI/Splink proposals within the ER-Evaluation interval. (4) Hypothesis property — no differing-currency/country pair ever yields an edge. (5) Upgrade anti-FP Check 1 from DISTINCT province_code [cluster_vehicles.py:852] to cross-(country,province) so the seal cannot pass green on a cross-border cluster.
- **Herramienta NEXT-LEVEL:** Splink (MIT) https://github.com/moj-analytical-services/splink [VERIFIED NEXT-LEVEL.md:450] — learned Fellegi-Sunter weights + exportable certifiable model.json; deterministic net stays the floor. Recall layer: LaBSE (Apache-2.0, https://huggingface.co/sentence-transformers/LaBSE [VERIFIED NEXT-LEVEL.md:458]) + datasketch MinHash-LSH/RapidFuzz (MIT, https://github.com/ekzhu/datasketch [VERIFIED NEXT-LEVEL.md:538]). Independent 2nd path: pyJedAI (Apache-2.0, https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:546]).

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-8"></a>

### Faceta 8 — Cualificación país+geo del matching (fusión transfronteriza)

> **B#1 CRITICAL — CIERRA (FIX-A). RIESGO #1 de la etapa.** Latente hoy; dispara en el país #2.

#### (a) code_hints verificados al atomo
- [VERIFIED pipeline/identity/cluster_vehicles.py:242-259] `_load_vehicles`: el `SELECT` trae `v.vehicle_ulid, v.entity_ulid, v.make, v.model, v.year, v.km, v.price, v.title, v.photo_url, v.vin_ref, v.first_seen, e.province_code` via `LEFT JOIN entity e ON e.entity_ulid = v.entity_ulid` -- **NO selecciona `e.country_code`**.
- [VERIFIED :258] `WHERE v.status = 'available'` -- **sin filtro de pais** (pasada global).
- [VERIFIED :387-398] construccion del bloque firma: extrae `make/model/year/km` y `province = v.get("province_code")` [:392], guard de no-nulos [:394], y `block_key = (make, model, year, km, province)` [:397] -- **country-BLIND**.
- [VERIFIED :415-417] guard km=0 (`_is_new_car` -> salvo VIN compartido, faceta 25); [:426-427] guard non-null-price; [:430-431] `_prices_within_tolerance` (±2%, `PRICE_TOL_PCT`); [:441-442] cross-entity-only; [:444-447] corroboracion por titulo normalizado (`ta and tb and ta==tb`).
- [VERIFIED migrations/0053_country_onboarding.sql:1-13] documenta la **colision de PK probada en vivo**: `INSERT geo_province(code='28', ..., country_code='DE')` falla sobre `geo_province_pkey(code)` -- es decir el codigo de provincia `'28'` es compartible ES-Madrid vs un Kreis DE; pre-0053 una PK de columna unica no puede sostener ES-28 y DE-28. 0053 promueve la PK geo a compuesta `(country_code, code)` PERO el `block_key` de firma sigue usando `province` desnudo.

#### (b) Mecanismo al atomo
Signal B agrupa por `(make, model, year, km, province)` y dentro del bloque aplica la cadena de guards. La clave **no tiene eje de pais**. Hoy es seguro SOLO porque `_load_vehicles` carga 100% filas ES (el invariante **accidental** "solo hay filas ES"). El geo backbone ya es compuesto tras 0053, pero el matcher **nunca lee `country_code`**: dos coches fisicos distintos en ES-provincia-28 y DE-provincia-28 (si DE usara un codigo de 2 chars '28') caen en el **mismo** bloque firma y, con `year/km` iguales + precio ±2% (ambos EUR) + titulo ASCII igual, se **fusionan como el mismo coche**.

#### (c) Costura ES -> generico (fix exacto)
Convertir el invariante accidental "solo hay filas ES" en garantia estructural "un coche fisico nunca cruza frontera ni unidad geo":
1. **Cargar el pais**: anadir `e.country_code` al `SELECT` de `_load_vehicles` (tras `e.province_code`, :255).
2. **Anteponerlo a la clave**: `block_key = (country_code, make, model, year, km, province)` en :397 -- la `CountryFirmaKey = (country_code, geo_unit, make, model, year, km)`.
3. **Parametrizar el grano geo**: expresar `geo_unit` como "misma unidad geo de nivel N" (ES = provincia/INE) impulsado por el country-pack, no hard-coded (acopla faceta 24, ancho de columna).
4. **Orden de despliegue**: enviar esto **ANTES** del pais #2 o del primer cluster global, o las fusiones cross-frontera ocurren en silencio.

#### (d) Riesgo adversarial concreto
- **LATENTE hoy** (ningun test lo captura -- solo existe ES). Dispara en silencio al aterrizar el pais #2: un **VW Golf ES-28 y DE-28** con mismo `year/km`, precio ±2% (ambos EUR -> faceta 9 no los separa) y titulo ASCII igual se **FUSIONAN** como un solo coche fisico. **CRITICAL**.
- El guard cross-entity (:441-442) **no protege**: dealers de paises distintos son cross-entity por definicion.
- El guard km=0 (:415-417) **no protege**: coches usados tienen km>0.
- DE/FR/IT/PT (zona EUR) son el vector mas peligroso justo porque comparten moneda; un no-UE con moneda propia se salva por el assert de moneda (faceta 9) pero no debe depender de ello.

#### (e) Sellado + verificacion multi-via
- **Via 1 (golden adversarial)**: par sintetico ES-28 + DE-28 con atributos identicos **NO** debe mergear (hoy SI lo hace) -- el test rojo que prueba la costura.
- **Via 2 (invariante de sello)**: la Check 1 anti-FP (faceta 22) elevada a cross-(country, geo_unit) reporta **0** clusters cross-country.
- **Via 3 (no-regresion ES)**: re-correr sobre datos ES-only reproduce clusters identicos (todas las filas ES llevan 'ES', asi que anteponer el eje pais es un no-op para ES).
- **Via 4 (autoridad geo)**: el `geo_unit` y su ancho derivan de ISO 3166-2 por pais (manifest), no de constantes INE.

#### (f) Herramienta NEXT-LEVEL
**pycountry** (ISO **3166-2** subdivision authority para el grano `geo_unit`) — LGPL-2.1, €0 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530, entry :527-533]. Es la entrada NEXT-LEVEL que mapea LITERALMENTE a esta faceta: el conteo y ancho de las subdivisiones de primer nivel de cada pais se vuelven **dato** (no centinelas con forma de Espana), alimentando un seal manifest per-pais (`geo_unit_level`, `geo_unit_width`) que hace la clave firma y sus guards **country-proof**. Comparte dependencia con faceta 1 (ISO 4217) y faceta 24 (ancho): **una autoridad ISO, tres registros**. Complemento de recall multi-script para la corroboracion de titulo: **LaBSE / BGE-M3** (multilingual semantic blocking) — Apache-2.0 — https://huggingface.co/sentence-transformers/LaBSE [VERIFIED :458].

#### Resolución condensada — Faceta 8

- **Costura (ES→genérico):** El block_key de Signal B (cluster_vehicles.py:397) es (make, model, year, km, province) -- country-BLIND. _load_vehicles (:242-259) ni selecciona country_code ni filtra por pais (WHERE status='available' :258). Es seguro solo por el invariante ACCIDENTAL 'solo hay filas ES'. El geo backbone ya es compuesto (country_code, code) tras 0053, pero el matcher nunca lee country_code -> la colision probada ES-28 vs DE-28 (0053:1-13) entra directa en la clave firma.
- **Fix:** 1) Anadir e.country_code al SELECT de _load_vehicles (tras :255). 2) block_key = (country_code, make, model, year, km, province) en :397 = CountryFirmaKey=(country_code, geo_unit, make, model, year, km). 3) Expresar geo_unit como 'misma unidad geo de nivel N' parametrico por country-pack (ES=provincia/INE), no hard-coded (acopla faceta 24). 4) Desplegar ANTES del pais #2 / primer cluster global, o las fusiones cross-frontera ocurren en silencio.
- **Adversarial:** LATENTE hoy (ningun test lo capta porque solo hay ES). Dispara en silencio con el pais #2: VW Golf ES-28 y DE-28 con mismo year/km, precio ±2% (ambos EUR -> faceta 9 no separa) y titulo ASCII igual se FUSIONAN como el mismo coche fisico. CRITICAL. El guard cross-entity no protege (dealers de paises distintos son cross-entity); el guard km=0 no protege (usados km>0). DE/FR/IT/PT (EUR comun) es el vector mas peligroso.
- **Sellado multi-vía:** Via 1: golden adversarial -- par ES-28 + DE-28 con atributos identicos NO debe mergear (hoy si). Via 2: Check 1 anti-FP (faceta 22) elevada a cross-(country, geo_unit) reporta 0 clusters cross-country. Via 3: no-regresion -- re-run ES-only reproduce clusters identicos (anteponer 'ES' es no-op para ES). Via 4: geo_unit y ancho derivados de ISO 3166-2 por pais (manifest), no de constantes INE.
- **Herramienta NEXT-LEVEL:** pycountry (ISO 3166-2 subdivision authority para el grano geo_unit) — LGPL-2.1 — https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:530, entry 527-533, mapeo LITERAL a esta faceta]. Conteo+ancho de subdivisiones de primer nivel por pais como dato -> seal manifest per-pais (geo_unit_level/width), guards country-proof. Una autoridad ISO compartida con facetas 1 (4217) y 24 (ancho). Complemento recall multi-script: LaBSE/BGE-M3 — Apache-2.0 — https://huggingface.co/sentence-transformers/LaBSE [VERIFIED :458].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-9"></a>

### Faceta 9 — Dimensión moneda end-to-end (FX)

> **B#3 CRITICAL — CIERRA (FIX-B).** Sin servicio FX: comparación intra-moneda por construcción.

#### (a) Verificacion de code_hints [VERIFIED]
- `migrations/0003_vehicles_events.sql:14` — `currency CHAR(3) NOT NULL DEFAULT 'EUR'`. La columna EXISTE y por defecto es EUR. [VERIFIED]
- `pipeline/platform/_core/sql.py:12-23` — `BULK_INSERT_VEHICLES` inserta 14 columnas (`vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, fuel, transmission, photo_url, vin_ref, status`) y **NO incluye `currency`** -> todo conector que use este bulk se apoya en el `DEFAULT 'EUR'`. [VERIFIED]
- **Grep `\bcurrency\b` en `delta.py`, `cluster_vehicles.py`, `delta_photo.py` = 0 coincidencias.** La moneda NO existe en la capa de matching ni de delta. [VERIFIED]
- `cluster_vehicles.py:178-189` — `_prices_within_tolerance(p_a,p_b)`: convierte ambos a `float`, exige `>0`, y compara `abs(fa-fb)/min(fa,fb) <= PRICE_TOL_PCT`. **Currency-blind**: no recibe ni mira moneda. [VERIFIED]
- `cluster_vehicles.py:83` — `PRICE_TOL_PCT = 0.02` (+/-2%). [VERIFIED]
- `pipeline/delta.py:319-324` — `diff_vehicle` emite `PRICE_CHANGE` con `old_value={"price":...}` / `new_value={"price":...}` **sin `currency`**. [VERIFIED]
- `pipeline/delta.py:378-385` — `_BULK_REFRESH_VEHICLES` actualiza `price/km/photo_url` y **no toca `currency`**. [VERIFIED]

#### (b) El mecanismo al atomo
El precio recorre tres puntos donde la moneda DEBERIA particionar y hoy no existe:
1. **Ingesta**: el conector inserta `price` por `BULK_INSERT_VEHICLES` y deja `currency` caer al `DEFAULT 'EUR'` (`sql.py:12-23` + `0003:14`). El dato de moneda que el sitio publica se PIERDE en frontera.
2. **Matching Signal B**: `_prices_within_tolerance` (cluster_vehicles.py:178-189) decide identidad fisica por `±2%` comparando floats crudos. Dos coches en monedas distintas con el mismo numero (8000 GBP / 8000 EUR) satisfacen el `±2%` de forma espuria.
3. **Delta/serving**: `diff_vehicle` (delta.py:319-324) registra el cambio de precio sin moneda; el historico servido es ambiguo. `_BULK_REFRESH_VEHICLES` refresca `price` sin `currency`.

La comparacion `±2%` es matematicamente valida SOLO si ambos operandos estan en la misma unidad. Hoy esa unidad esta garantizada por un **invariante accidental**: "solo hay filas ES, todas EUR". No hay un solo `assert same-currency`.

#### (c) La costura ES->generico
La costura es convertir el supuesto implicito "todo es EUR" en una **dimension estructural**:
- **Escritura**: el conector DEBE fijar `vehicle.currency` desde lo que publica el sitio (anadir `currency` a la lista de columnas de `BULK_INSERT_VEHICLES` y al unnest). Hoy 0 conectores la escriben.
- **Particion en la clave firma**: anteponer `currency` al bloque de Signal B y/o un `assert` de misma-moneda ANTES del `±2%`, de modo que un par cross-moneda nunca entre al mismo bloque (over-merge cross-moneda estructuralmente imposible).
- **Payload**: registrar `currency` en `old_value`/`new_value` de `PRICE_CHANGE`.
- **Techo por moneda**: alimentar `sanitize_price` (faceta 11) con un `PRICE_MAX` por-moneda (el techo EUR no es portable a JPY).
**Sin FX rates**: por construccion las comparaciones son intra-moneda (la moneda esta en la clave de bloque), asi que NO hace falta servicio de cambio ni tasas — coste cero.

#### (d) Riesgo adversarial concreto
- **No-UE (UK/GBP, JP/JPY, etc.)**: un pais no-EUR cuyo conector no fije `currency` hereda `'EUR'` -> el `±2%` compara magnitudes sin sentido; un coche JP a Y3.000.000 y otro a Y3.050.000 ("EUR" fantasma) se fusionan o no por puro azar numerico. CRITICAL al aterrizar el primer mercado no-EUR.
- **DE/FR/IT/PT (EUR)**: INOCUO hoy — comparten EUR, por eso el bug esta LATENTE y ningun test lo dispara. Pero co-resident con un mercado no-EUR, la BD ya es multi-moneda y el riesgo se materializa.
- **Ruido**: un sitio que publique precio en una moneda secundaria (p.ej. anuncios en EUR dentro de un portal UK) sin senal de moneda corrompe el bloque.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado** = (1) cada vehiculo no-EUR lleva su `currency` fijada por el conector (cero herencia silenciosa de EUR); (2) NINGUN bloque de Signal B mezcla dos monedas; (3) `PRICE_CHANGE` porta `currency`; (4) `PRICE_MAX` parametrizado por moneda.
- **Via 1 (golden parser)**: price-parser trae strings de precio etiquetados por locale; pinear una muestra por pais y asertar que la moneda detectada coincide con la esperada.
- **Via 2 (invariante de clave de bloque)**: test que asierta que ningun bloque de Signal B contiene dos `currency` distintas -> una colision GBP/EUR a `±2%` es estructuralmente imposible. [espeja NEXT-LEVEL.md:509]
- **Via 3 (techo por moneda)**: un precio JPY normal SOBREVIVE `sanitize_price` bajo el techo JPY (fixture B3 verde) mientras el junk EUR sigue rechazado. [espeja NEXT-LEVEL.md:509]
- **Via 4 (adversarial)**: inyectar un par cross-moneda con numeros casi iguales y confirmar que NO se fusionan (antes-de-fix se fusionaban).

#### (f) Herramienta NEXT-LEVEL que lo eleva
**price-parser** (parser de precio+moneda CLDR en frontera) — BSD-3-Clause, EUR0=True — https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216 y :506]. Es el match EXACTO de esta faceta ("Currency-correct pricing: price-parser at the boundary + Babel/py-moneyed for per-currency ceilings", NEXT-LEVEL.md:503-509). Detecta la divisa in-band en el string de precio; **Babel** (CLDR, BSD) valida el formato por-locale y **py-moneyed** aporta el tipo Money currency-safe [VERIFIED NEXT-LEVEL.md:507]. Todo es CPU puro, offline (CLDR empaquetado con Babel), sin servicio de FX porque las comparaciones son intra-moneda por construccion (la moneda va en la clave de bloque) -> EUR0 total [VERIFIED NEXT-LEVEL.md:508]. Eleva el `±2%` de "valido por accidente porque todo es EUR" a "correcto en toda moneda, probado por golden multi-locale + invariante de no-mezcla".

#### Resolución condensada — Faceta 9

- **Costura (ES→genérico):** La columna currency EXISTE (migrations/0003:14, CHAR(3) DEFAULT 'EUR') pero NADIE la escribe: BULK_INSERT_VEHICLES (sql.py:12-23) inserta 14 cols sin currency -> herencia silenciosa de EUR. La moneda esta AUSENTE de todo el matching/delta (grep \bcurrency\b en delta/cluster_vehicles/delta_photo = 0). El ±2% (_prices_within_tolerance cluster_vehicles.py:178-189, PRICE_TOL_PCT=0.02 :83) compara floats crudos currency-blind; PRICE_CHANGE (delta.py:319-324) no porta moneda. El invariante 'todo es EUR' es accidental, no estructural.
- **Fix:** 1) Anadir currency a las columnas/unnest de BULK_INSERT_VEHICLES y que cada conector la fije desde el sitio. 2) Anteponer currency a la clave de bloque de Signal B + assert same-currency ANTES del ±2% (over-merge cross-moneda imposible por construccion). 3) Registrar currency en old_value/new_value de PRICE_CHANGE. 4) Parametrizar PRICE_MAX por moneda. Sin FX rates: comparaciones intra-moneda por construccion, coste cero.
- **Adversarial:** No-UE CRITICAL: un pais no-EUR sin fijar currency hereda 'EUR' -> ±2% compara magnitudes sin sentido (dos coches JPY se fusionan o no por azar numerico; 8000 GBP ~ 8000 EUR comparan iguales). DE/FR/IT/PT (EUR): inocuo HOY -> bug LATENTE que ningun test dispara, pero co-residente con un mercado no-EUR la BD ya es multi-moneda y se materializa. El payload de evento sin moneda es ambiguo al servir historico mixto.
- **Sellado multi-vía:** Sellado = cada no-EUR con currency fijada (cero herencia de EUR) + ningun bloque Signal B mezcla 2 monedas + PRICE_CHANGE con currency + PRICE_MAX por moneda. Multi-via: (1) golden de price-parser por locale (moneda detectada == esperada); (2) invariante de clave de bloque: 0 bloques con 2 currency -> colision GBP/EUR imposible; (3) techo por moneda: JPY normal sobrevive sanitize_price, junk EUR sigue rechazado; (4) adversarial: par cross-moneda casi-igual NO se fusiona.
- **Herramienta NEXT-LEVEL:** price-parser (precio+moneda CLDR en frontera) — BSD-3-Clause, EUR0=True — https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:216,:506]. Match EXACTO ('Currency-correct pricing', NEXT-LEVEL.md:503-509): detecta divisa in-band; Babel (CLDR) valida formato por-locale; py-moneyed da el tipo Money currency-safe. CPU puro, offline, sin servicio FX (comparaciones intra-moneda por construccion) -> EUR0 total.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-10"></a>

### Faceta 10 — Normalización de título consciente de script/locale

> **B#4 HIGH — CIERRA eurozona / OPEN JP** (`title_norm_policy=CJK`).

#### (a) code_hints VERIFICADOS
- `_normalize_title` `cluster_vehicles.py:166-175` [VERIFIED]: guard vacio :171-172; `unicodedata.normalize("NFKD", title)` :173; `_RE_NON_ALNUM.sub("", nfkd.encode("ascii","ignore").decode("ascii").lower())` :174; **devuelve None si queda vacio** :175. Pipeline exacto: NFKD -> `encode('ascii','ignore')` (DESCARTA todo no-ASCII) -> lower -> strip `[^a-z0-9]`.
- Aplicado en la corroboracion de Signal B :444-447 [VERIFIED]: `ta=_normalize_title(va.get("title")); tb=_normalize_title(vb.get("title")); if not (ta and tb and ta==tb): continue`. El titulo es **el unico** corroborador cross-entity de Signal B (mismo dealer ya lo caza Signal A :441-442).

#### (b) Mecanismo al atomo
La firma (faceta 7) empareja por `(make,model,year,km,province)` + precio +/-2%; el titulo normalizado es la **prueba final** que evita fundir dos unidades distintas con la misma firma. `_normalize_title` reduce el titulo a un esqueleto `[a-z0-9]` para que "VW Golf 2.0 TDI" y "vw  golf 2,0 tdi!" colapsen. El predicado `ta and tb and ta==tb` exige **ambos no-None e iguales**: si cualquiera es None (titulo que se vacia tras el fold), la corroboracion **falla cerrada** -> no hay merge. Ahi esta el atomo del fallo: `encode('ascii','ignore')` sobre un titulo 100% no-ASCII produce `b''` -> `''` -> None.

#### (c) Costura ES->generico
ES es Latin-1: el fold ASCII es casi-identidad (pierde acentos que el titulo automotriz raramente usa). La costura es la linea :174 `encode('ascii','ignore')`, **irreversible y destructiva** fuera de Latin:
- **CJK (JP/CN/KR):** "Toyota Prius" en kana/kanji -> NFKD no descompone Han/Kana a ASCII -> `b''` -> None -> Signal B **muerto** (under-merge: todo par JP cross-entity se queda sin corroborar).
- **eszett aleman:** "Strasse" escrito con ss-ligadura -> NFKD no la convierte -> ignore la borra -> "strae" (pierde "ss"); "Strasse" -> "strasse". Dos grafias del mismo modelo **no corroboran** (under-merge leve).
- **Diacriticos FR/PT:** NFKD separa el diacritico como marca combinante y `ignore` lo borra -> "Citroen" con dieresis -> "citroen" (converge por suerte). El riesgo fino: digitos fullwidth que NFKD **si** mapea a ASCII -> dos titulos distintos colapsan a un residuo corto e **igual** -> falso-corrobora (over-merge).
**Fix exacto:** sustituir la rama `nfkd.encode('ascii','ignore')` por `anyascii(title)` (transliteracion no-destructiva, script-aware) ANTES del strip `[^a-z0-9]`, seleccionada por `pack.normalize_policy`; ES queda byte-identico (ASCII inalterado). Anadir guard de pre-imagen vacia: si la transliteracion devuelve vacio, escalar/registrar en vez de None silencioso.

#### (d) Riesgo adversarial
- **Japon (CRITICAL/HIGH):** titulos CJK -> '' -> None -> `ta and tb` False -> Signal B no corrobora **nunca** -> under-merge sistematico; el over-count JP se sirve como +/-dup_ci ancho (y con VIN-17 excluido en JP -faceta 19- y photo_hash 0% -faceta 13-, **ninguna** via lawful colapsa JP).
- **Over-merge por residuo:** dos modelos JP distintos cuyo unico ASCII (digitos fullwidth NFKD->ASCII, p.ej. cilindrada) coincide -> residuo corto igual -> falso-corrobora dentro de un bloque firma ya estrecho.
- **DE/FR/PT (leve):** ss perdido y algun diacritico -> under-merge marginal; menos grave porque make/model/year/km/precio ya restringen el bloque.
- **Ruido:** un titulo-plantilla ("Coche ocasion garantia") normaliza igual entre coches distintos -> el guard cross-entity+firma lo contiene, pero el titulo deja de discriminar.

#### (e) Sellado + verificacion multi-via
- **Via 1 (golden byte-identico ES):** re-normalizar el corpus ES con la nueva ruta `anyascii` -> claves identicas a hoy (cero re-key); suite Ferrari verde.
- **Via 2 (regresion no-Latina):** fixture de 2 dealers JP **distintos** name-only -> claves DISTINTAS (no colapsan), y 2 listings del MISMO coche JP -> misma clave (corrobora). key(eszett)==key("Strasse").
- **Via 3 (no-vacio):** assert que ningun titulo no-Latino produce None tras transliteracion (guard de pre-imagen vacia probado).
- **Via 4 (adversarial/property):** Hypothesis genera titulos CJK/fullwidth/mixtos y afirma "anyascii nunca vacia un titulo con contenido y nunca colisiona dos titulos semanticamente distintos a un residuo corto".

#### (f) Herramienta nivel-inalcanzable
**anyascii** (ISC, EUR0) - https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:479-485 y :326-332]: transliteracion data-driven, dependency-free, **ISC** (comercial-limpia, a diferencia de unidecode GPL que contaminaria el servicio API). Mapea cada bloque Unicode a ASCII sensato (CJK->romaji/pinyin-ish, Cirilico/Griego->Latin, eszett->ss, a-dieresis->ae). Cierra la "CRITICAL ASCII-fold double-failure" exacta de :174. Drop-in en el call-site del fold. **Complemento:** **LaBSE** (Apache-2.0, sentence-transformers) - https://huggingface.co/sentence-transformers/LaBSE [VERIFIED NEXT-LEVEL.md:455-461]: blocking semantico multilingue (109 idiomas) que recupera recall cross-script ANTES de que exista un normalizador por locale, ensanchando el candidate-net sin que los guards estructurales cedan. Caveat [VERIFIED NEXT-LEVEL.md:327]: anyascii romaniza Han via pinyin chino, **incorrecto** para toponimos JP; para TITULOS de coche el riesgo es menor, pero preferir romanizacion de fuente si el conector la trae.

#### Resolución condensada — Faceta 10

- **Costura (ES→genérico):** cluster_vehicles.py:174 `nfkd.encode('ascii','ignore')` es Latin-only y destructivo: un titulo 100% no-ASCII -> b'' -> '' -> None; aplicado en la corroboracion de Signal B :444-447 donde `ta and tb and ta==tb` falla cerrada si cualquiera es None.
- **Fix:** Sustituir la rama encode('ascii','ignore') por anyascii(title) ANTES del strip [^a-z0-9], elegido por pack.normalize_policy; ES byte-identico (ASCII inalterado). Anadir guard de pre-imagen: transliteracion vacia -> registrar/escalar, no None silencioso.
- **Adversarial:** JP CRITICAL: CJK -> '' -> None -> Signal B no corrobora nunca (under-merge sistematico); con VIN-17 excluido y photo_hash 0%, JP sin via lawful de colapso. Over-merge: digitos fullwidth que NFKD mapea a ASCII -> residuo corto igual -> falso-corrobora. DE/FR/PT leve: ss perdido y diacriticos -> under-merge marginal.
- **Sellado multi-vía:** Via1 golden byte-identico ES (anyascii sobre corpus ES = claves de hoy, Ferrari verde). Via2 regresion no-Latina: 2 dealers JP distintos -> claves distintas; mismo coche JP -> misma clave; key(eszett)==key('Strasse'). Via3 assert no-None tras transliteracion. Via4 Hypothesis fuzz CJK/fullwidth: nunca vacia titulo con contenido, nunca colisiona distintos a residuo corto.
- **Herramienta NEXT-LEVEL:** anyascii (ISC, https://github.com/anyascii/anyascii) [VERIFIED NEXT-LEVEL.md:479-485,326-332] cierra el fold ASCII destructivo (CJK->romaji, eszett->ss), ISC limpio vs unidecode GPL. Complemento LaBSE (Apache-2.0, https://huggingface.co/sentence-transformers/LaBSE) [VERIFIED :455-461] para blocking semantico multilingue. Caveat: anyascii romaniza Han via pinyin (mal para toponimos JP); preferir romaji de fuente cuando exista.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-11"></a>

### Faceta 11 — Saneo numérico en frontera (price/km/year + cross-field)

> **B#3 + B#8 — CIERRA (FIX-B / FIX-F).** `PRICE_MAX` magnitud EUR; KM/year físicos heredables.

#### (a) Code hints [VERIFIED]
- [VERIFIED pipeline/price_sanity.py:49] `PRICE_MAX = 5_000_000`. Comentario (:47-48): techo real de mercado usado ~3.6M EUR (Bugatti Chiron); >5M es centinela/parse-error (Qashqai @ 10M EUR, camiones @ 9.999.999 'all-9s').
- [VERIFIED price_sanity.py:51] `KM_MAX = 1_500_000`. Comentario (:50, :70-74): 1.5M es el DEFAULT de la API de Wallapop para odometro SIN fijar -> el boundary `>=` (:81) mata exactamente ese centinela.
- [VERIFIED price_sanity.py:53] `YEAR_MIN = 1900`.
- [VERIFIED price_sanity.py:56-66] `sanitize_price`: None si no-parseable, o `p <= 0 or p > PRICE_MAX` (:64). Devuelve el price ORIGINAL (no el float) si pasa.
- [VERIFIED price_sanity.py:69-83] `sanitize_km`: None si `k < 0 or k >= KM_MAX` (:81).
- [VERIFIED price_sanity.py:86-96] `sanitize_year`: None si `y < YEAR_MIN or y > datetime.now().year + 1` (:94) -> cota dinamica, nunca caduca.
- [VERIFIED price_sanity.py:99-124] `sanitize_year_km` cross-field: `age = datetime.now().year - y` (:121); `(age<=0 and k>300_000) or (age<=1 and k>500_000)` -> `(None, None)` (:122). NULL AMBOS porque cual campo es el error es price-dependiente y ambiguo (:101-104).
- [VERIFIED price_sanity.py:29, :107] doctrina Law I: under-correct over mis-correct.

#### (b) Mecanismo al atomo
Cuatro gates puros, sin I/O, idempotentes. Cada `sanitize_X` devuelve el valor ORIGINAL intacto o `None` (junk inequivoco). El cross-field `sanitize_year_km` es el unico que toca dos campos: cuando edad~0 y km enorme, nula AMBOS (no adivina cual esta mal) y el coche SIGUE servible - solo el campo imposible lee 'desconocido' en vez de distorsionar toda la distribucion km/edad/precio. La banda 150k-500k a 1 anio se deja DELIBERADAMENTE (fuzz model-year-vs-matricula + uso comercial intensivo legitimo, :110-112). Todo el modulo esta calibrado sobre el corpus EUR/ES 2026-06-15/16.

#### (c) Costura ES->generico
`PRICE_MAX=5_000_000` es una MAGNITUD EUR (techo Bugatti ~3.6M EUR). No es portable: es el unico de los cuatro limites que es moneda-dependiente. `KM_MAX` y `YEAR_MIN`/`year+1` son limites FISICOS heredables. El modulo es currency-blind: no recibe `currency` ni la mira.

#### (d) Riesgo adversarial concreto
**Japon: CRITICAL.** Un coche JPY normal vale 6M-40M JPY y supera `PRICE_MAX=5_000_000` -> `sanitize_price` -> None. Efecto domino: (1) `PRICE_CHANGE` (faceta 14, diff_vehicle) NUNCA dispara porque el precio nulado queda congelado por COALESCE; (2) el guard non-null-price de Signal B (cluster_vehicles.py:426) tira CADA coche JPY del matching. Es decir, un techo EUR mal-portado borra el precio de TODO un pais. Mercados de millas (no-UE, p.ej. UK servido en millas): `KM_MAX` en km es semanticamente distinto; un centinela km-desconocido extranjero (p.ej. 999.999) pasa el gate `<1.5M`. GBP/EUR: 8000 GBP comparado como 8000 EUR es inocuo en el saneo pero envenena el +/-2% (faceta 9).

#### (e) Sellado + verificacion multi-via
1. Test techo por-moneda: un precio JPY normal (p.ej. 8M JPY) SOBREVIVE `sanitize_price` bajo el techo JPY mientras el junk EUR de 10M sigue rechazado (la fixture B3 pasa a verde).
2. ES baseline byte-identico: sobre el corpus EUR, la salida de los cuatro sanitizers no cambia (cero regresion).
3. Heritabilidad fisica: `KM_MAX`/`YEAR` se aseveran INALTERADOS cross-pais (son fisica, no moneda).
4. Golden del parser (tool): price-parser trae strings etiquetados por locale; fijar una muestra por pais ancla el parseo amount+currency.

#### (f) Herramienta NEXT-LEVEL
[VERIFIED NEXT-LEVEL.md:503-509] **price-parser (BSD-3-Clause)** https://github.com/scrapinghub/price-parser + Babel (CLDR) + py-moneyed. price-parser extrae amount+currency del string crudo en ingesta (puebla vehicle.currency fiable), Babel resuelve formato numero/moneda por locale, py-moneyed da aritmetica monetaria segura, y `PRICE_MAX` pasa a ser PER-MONEDA en el CountryProfile. Pone currency en la block-key de Signal B (mismo bloque -> misma moneda) y asevera misma-moneda ANTES del +/-2%. Ruta EUR0: todo permisivo, pure-Python, offline (CLDR bundled con Babel), sin servicio FX (comparaciones intra-moneda por construccion). Cierra el B3 CRITICAL.

#### Resolución condensada — Faceta 11

- **Costura (ES→genérico):** PRICE_MAX=5_000_000 (price_sanity.py:49) es una magnitud EUR (techo Bugatti ~3.6M EUR), el unico limite moneda-dependiente; KM_MAX (:51) y YEAR (:53/:94) son fisicos y heredables. El modulo es currency-blind: no recibe ni mira currency. KM en km asume mercados metricos.
- **Fix:** PRICE_MAX per-moneda en CountryProfile (p.ej. techo JPY ~60-80M); el conector puebla vehicle.currency (hoy se confia en DEFAULT 'EUR'); sanitize_price recibe currency y busca el techo correspondiente. Parametrizar la unidad de distancia (km vs millas) por pais. KM_MAX/YEAR_MIN/year+1 se heredan sin cambio (limites fisicos).
- **Adversarial:** JPY CRITICAL: coche normal 6M-40M JPY > PRICE_MAX=5M -> sanitize_price=None -> PRICE_CHANGE (faceta 14) nunca dispara (precio congelado por COALESCE) y el guard non-null-price de Signal B (cluster_vehicles.py:426) tira cada coche JPY. Mercados de millas: km semanticamente distinto; centinela km-desconocido extranjero (999.999) pasa el gate <1.5M. GBP/EUR: igual magnitud envenena el +/-2% (faceta 9).
- **Sellado multi-vía:** (1) Precio JPY normal sobrevive sanitize_price bajo techo JPY mientras junk EUR 10M sigue rechazado (fixture B3 verde). (2) ES baseline EUR byte-identico (cero regresion). (3) KM_MAX/YEAR aseverados inalterados cross-pais (fisica). (4) Golden de price-parser por locale fija el parseo amount+currency.
- **Herramienta NEXT-LEVEL:** price-parser (BSD-3-Clause) https://github.com/scrapinghub/price-parser + Babel (CLDR) + py-moneyed [VERIFIED NEXT-LEVEL.md:506] - parseo amount+currency en ingesta, techos PRICE_MAX per-moneda, currency en la block-key de Signal B; EUR0, offline, sin servicio FX (intra-moneda por construccion). Cierra B3 CRITICAL.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-12"></a>

### Faceta 12 — Núcleo pHash DCT 64-bit + calibración de umbrales

> **Umbrales ASSUMED — OPEN (calibración).** Núcleo matemático ya país-blind.

#### (a) Verificacion de code_hints [VERIFIED] (pipeline/delta_photo.py)
- Geometria imagehash.phash: `_HASH_SIZE=8`, `_HIGHFREQ_FACTOR=4`, `_IMG_SIDE=32` [VERIFIED :27-29] (resize a 32x32, conserva el bloque DCT low-freq 8x8 superior-izquierdo).
- `hash_image_bytes(data) -> PhotoHash` [VERIFIED :64-80]: `Image.open(BytesIO)` -> `convert("L").resize((32,32), LANCZOS)` [:69] -> `dct(dct(arr,axis=0,norm='ortho'),axis=1,norm='ortho')` [:71] -> `low = coeff[:8,:8]` [:72] -> `bits = low > np.median(low)` [:73] -> 64 bits hex [:77]. `quality` = `np.std(ac)` tras anular DC `ac[0,0]=0.0` [:74-78]; `content_hash` = `blake2b(data, digest_size=16)` [:79].
- `hamming(a,b)` = `bin(int(a,16) ^ int(b,16)).count("1")` [VERIFIED :83-85].
- `same_photo(a,b,max_distance=PHASH_HAMMING_MAX)` = `hamming<=max` [VERIFIED :88-90].
- `is_phash(value)` guard: `isinstance str` + `len==16` + `int(value,16)` parseable [VERIFIED :93-101].
- `download_and_hash(url, *, fetch, cache)` [VERIFIED :104-126]: `fetch` **INYECTADO** [:117], clave `blake2b` [:120], cache short-circuit [:121-122]; "never opens a socket itself; the egress stays gated in `fetch`" [:114-115].
- `PhotoHash` dataclass frozen: `phash` / `quality` / `content_hash` [VERIFIED :37-41, campo `quality` :40].
- `PHASH_HAMMING_MAX = 10` [VERIFIED :34] con comentario explicito **ASSUMED** "to be CALIBRATED against real car photos before relied upon" [:31-33].
- Segunda constante (watermark, identidad mismo-coche): "(pHash Hamming <= 6 AND make,model,year,km-band all equal)" [VERIFIED scripts/cross_platform_dedup_watermark.py:14].

#### (b) Mecanismo al atomo
DCT-II separable 2D sobre un plano luma 32x32; el bloque low-freq 8x8 se umbraliza contra su **propia mediana** -> 64 bits de signo. Robustez a escala/recompresion/brillo porque umbralizar-por-mediana el low-freq DCT es invariante a transformaciones monotonas de luma. `quality` = std de los coeficientes AC (DC anulado) = cuanta ESTRUCTURA lleva la imagen; un placeholder casi plano tiene quality~0. Dos fotos son "la misma imagen" sii Hamming(64-bit) <= umbral. Viven **DOS umbrales semanticamente distintos** en dos ficheros: `PHASH_HAMMING_MAX=10` (delta path: "misma imagen modulo recompresion/CDN re-encode") y `<=6` (watermark strong-key: "mismo coche fisico"). Ambos ASSUMED, sin calibrar. `download_and_hash` mantiene el egress fuera (fetch inyectado) -> el core de hashing es offline-testable.

#### (c) Costura ES -> generico + fix
La matematica es **country-blind** (los pixeles no tienen locale) — rara faceta cuyo NUCLEO ya es generico. La costura es: (1) las dos constantes ASSUMED calibradas contra nada, y (2) `quality` se computa pero **NO se usa para gate** — el heuristico de colision K=12 de Signal A (facet 6) hace el mata-placeholder en vez de un piso estructural de calidad.
**Fix:** (i) cosechar gratis un set etiquetado misma-foto/distinta-foto (pares VIN-exact => mismo coche; make/model distinto => distinto) y calibrar `PHASH_HAMMING_MAX` y el `<=6` del watermark **por separado** via ROC, jamas reutilizando uno por el otro; (ii) anadir un **piso estructural de calidad** (`quality < q_min` => excluir del strong-key) para que las imagenes catalogo/placeholder caigan por ESTRUCTURA, no por conteo; (iii) preservar el gating de egress por-host de `download_and_hash` (token-bucket, facet 13) para cualquier pais.

#### (d) Riesgo adversarial concreto
- Un hash de **64 bits** tiene poder separador limitado: a escala censo (2.3M, ~131.8K over-count de clave debil) la tasa de falso-merge al recall necesario para colapsar duplicados es demasiado alta -> el residual se sirve como `+/-dup_ci` ancho en vez de colapsarse.
- Ambas constantes sin calibrar -> over-fusion (coches distintos fundidos) o under-fusion (dup real servido doble). **DE/FR/IT/PT** CDNs re-codifican distinto (cuantizacion JPEG distinta) -> un umbral afinado en CDNs ES mis-fire fuera.
- Placeholders/fotos sin estructura (quality~0) hoy se cuelan porque el gate es conteo de colision (K), no calidad; un pais con otra convencion de placeholder derrota K.
- El set de calibracion depende de `photo_hash` poblado (facet 13) — **0% hoy**, asi que ninguna constante puede calibrarse ahora mismo.

#### (e) Criterio de sellado + verificacion multi-via
- **Golden de calibracion:** ROC sobre el set etiquetado held-out debe mostrar que el umbral elegido mantiene falso-merge ~0 al recall objetivo, reportado CON IC; los dos umbrales documentados con sus puntos de operacion separados (recompresion vs identidad).
- **Unit de piso de calidad:** una imagen plana sintetica (quality~0) se excluye sin importar el Hamming.
- **Cross-check ortogonal:** todo merge propuesto por pHash debe ADEMAS satisfacer firma Signal-B OR VIN antes de auto-aplicar; post-swap el conteo de dedup servido debe seguir igualando el recomputo SQL independiente (doctrina dedup-invariant).
- **Determinismo:** mismos bytes -> mismo hash de 64 bits entre runs (golden vectors).

#### (f) Herramienta NEXT-LEVEL
**PDQ** (BSD-3-Clause, https://github.com/facebook/ThreatExchange/tree/main/pdq) [VERIFIED NEXT-LEVEL.md:434] — el hash perceptual de **256 bits** de Meta que trae una metrica de calidad 0-100 Y un umbral Hamming documentado y calibrado (`<=31/256` match + piso de calidad). 256 bits separa misma/distinta imagen con falso-merge mucho menor a recall fijo que 64 bits -> es el strong-key que puede colapsar lawfully una porcion grande del over-count de 131.8K; su score de calidad mata placeholders ESTRUCTURALMENTE, **retirando AMBAS constantes ASSUMED** (PHASH_HAMMING_MAX=10 y <=6) de una vez. Verificacion: golden vectors de referencia de PDQ (port dentro de distancia<=10 del C++ de referencia para quality>=80) + ROC vs el hash de 64 bits sobre el set etiquetado gratis. Complemento: **DINOv2** (Apache-2.0, https://github.com/facebookresearch/dinov2) [VERIFIED NEXT-LEVEL.md:442] para el residual "mismo coche, foto DISTINTA" que ningun pHash alcanza (embedding visual self-supervised + ANN pgvector, gateado bajo VAM). Ambos EUR0 sobre fotos ya descargadas.

#### Resolución condensada — Faceta 12

- **Costura (ES→genérico):** El nucleo matematico ya es country-blind (pixeles sin locale). La costura no es el pais sino: (1) PHASH_HAMMING_MAX=10 [delta_photo.py:34] y el <=6 del watermark [watermark:14] son DOS umbrales ASSUMED calibrados contra nada (delta_photo.py:31-33 lo declara), y (2) PhotoHash.quality [:40,:74-78] se computa pero NO gatea — el mata-placeholder lo hace el conteo K=12 de Signal A en vez de un piso estructural de calidad. CDNs por pais (DE/FR/IT/PT) re-codifican distinto, asi que un umbral afinado en ES mis-fire fuera.
- **Fix:** (i) Cosechar gratis un set etiquetado misma/distinta-foto (VIN-exact => mismo coche; make/model distinto => distinto) y calibrar PHASH_HAMMING_MAX y el watermark <=6 POR SEPARADO via ROC, sin reutilizar uno por el otro (semanticas distintas: recompresion vs identidad). (ii) Anadir piso estructural de calidad: quality < q_min => excluir del strong-key, para que placeholders caigan por estructura y no por conteo K. (iii) Mantener el egress por-host inyectado de download_and_hash (facet 13) para cualquier pais. Prerequisito: photo_hash poblado (facet 13), 0% hoy, sin el cual no hay set de calibracion.
- **Adversarial:** 64 bits tiene poder separador limitado: a 2.3M filas (~131.8K over-count de clave debil) el falso-merge al recall necesario es demasiado alto -> residual servido como +/-dup_ci ancho en vez de colapsado. Constantes sin calibrar -> over/under-fusion. DE/FR/IT/PT: cuantizacion JPEG de CDN distinta rompe el umbral ES-afinado. Placeholders quality~0 se cuelan porque el gate es conteo K no calidad; otra convencion de placeholder por pais derrota K. La calibracion entera esta bloqueada por photo_hash 0% (facet 13).
- **Sellado multi-vía:** Golden de calibracion: ROC en set held-out etiquetado mantiene falso-merge ~0 al recall objetivo, reportado con IC; los dos umbrales con puntos de operacion separados. Unit de piso de calidad: imagen plana (quality~0) excluida sin importar Hamming. Cross-check ortogonal: todo merge pHash debe ademas pasar firma Signal-B OR VIN antes de auto-aplicar; post-swap el dedup servido sigue igualando el recomputo SQL (dedup-invariant). Determinismo: mismos bytes -> mismo hash (golden vectors).
- **Herramienta NEXT-LEVEL:** PDQ (BSD-3-Clause, https://github.com/facebook/ThreatExchange/tree/main/pdq) [VERIFIED NEXT-LEVEL.md:434]: hash perceptual 256-bit de Meta con metrica de calidad 0-100 y umbral calibrado (<=31/256 + piso de calidad); separa misma/distinta imagen con falso-merge mucho menor a recall fijo que 64 bits, colapsa lawfully gran parte del over-count 131.8K y retira AMBAS constantes ASSUMED (10 y 6). Verificacion via golden vectors propios de PDQ + ROC vs el hash 64-bit. Complemento: DINOv2 (Apache-2.0, https://github.com/facebookresearch/dinov2) [VERIFIED NEXT-LEVEL.md:442] para 'mismo coche, foto distinta' (embedding visual + ANN pgvector, gateado por VAM). Ambos EUR0 sobre fotos ya descargadas.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-13"></a>

### Faceta 13 — `photo_hash`: ruta de escritura + backfill gateado por governor

> **Hueco GLOBAL (no ES-puro) — OPEN (plan pHash €0).** Desbloquea la única vía de Japón.

#### (a) Verificacion de code_hints [VERIFIED]
- Columna existe e INERTE: `photo_hash TEXT, -- perceptual hash for Δphoto detection` [VERIFIED migrations/0003_vehicles_events.sql:18]. La doctrina del watermark confirma "photo_hash populated on 0 vehicles" [VERIFIED scripts/cross_platform_dedup_watermark.py:21].
- INSERT sin photo_hash: `BULK_INSERT_VEHICLES` lista 14 columnas `(vehicle_ulid, entity_ulid, deep_link, title, make, model, year, km, price, fuel, transmission, photo_url, vin_ref, status)` -> NO incluye photo_hash [VERIFIED pipeline/platform/_core/sql.py:12-23, lista :13-14].
- REFRESH sin photo_hash: `_BULK_REFRESH_VEHICLES` actualiza solo `price/km/photo_url` via COALESCE [VERIFIED pipeline/delta.py:378-385]. El emisor `emit_change_deltas` (:388-446) appendea `up_photo.append(new_obj.photo_url)` -> la URL CRUDA, nunca un hash [VERIFIED :441].
- Frontera de egress YA aislada e INYECTADA: `download_and_hash(url, *, fetch, cache)` [VERIFIED pipeline/delta_photo.py:104-126]; `fetch` es inyectado (:107) y "This function never opens a socket itself; the egress stays gated in `fetch`" [VERIFIED :110, :114-115]. El docstring nombra `fetch` como "governor-wrapped" (:110).
- Matematica del hash (faceta 12, no esta): `hash_image_bytes` puro offline (:64-80), `content_hash` blake2b como cache-key (:79), cache por content-hash que SALTA re-hashear bytes identicos (:120-125), `PhotoHash.quality` AC-energy con DC dropeado (:40, :74-75).

#### (b) Mecanismo al atomo
1. **Hoy**: la columna `photo_hash` existe en el esquema pero NINGUN escritor la puebla -> 0% poblada. El strong-key pHash (faceta 12, 20) esta INERTE; el `PHOTO_CHANGE` content-aware cae a comparacion de string `photo_url` (faceta 14).
2. **El plan de plumbing (EUR0)** tiene tres piezas: (i) anadir `photo_hash` a la lista de columnas de `BULK_INSERT_VEHICLES` (alta de listing); (ii) anadir `photo_hash` a `_BULK_REFRESH_VEHICLES` (re-visto); (iii) un writer de backfill que hashea INLINE las fotos ya descargadas en el scrape via `download_and_hash`.
3. **El governor**: el egress NO vive en el codigo de hash — vive en el `fetch` inyectado. El backfill masivo sobre la flota viva ES egress a escala y debe pasar por un token-bucket **per-HOST** (per-TLD/CDN), porque un host CDN sirve muchos paises y un pais usa muchos hosts. El hashing del path scrape-en-vivo es egress marginal CERO (los bytes ya estan en mano); solo el backfill historico es egress real.
4. **Cache de contenido**: `download_and_hash` salta re-hashear bytes byte-identicos via `content_hash` (:120-125) -> un placeholder reusado en 1.000 listings se descarga/hashea una vez.

#### (c) Costura ES->generico
Este es un hueco **GLOBAL, no ES-puro**: la columna y los escritores ausentes existen para TODOS los paises. La costura es de ACTIVACION: sin la ruta de escritura, el strong-key de CADA pais colapsa a VIN-exact (18 filas, faceta 19/20). El fix es pais-blind (anadir una columna a dos listas de SQL). La UNICA dimension de scope es el governor: debe ser per-HOST, no per-pais (un Cloudflare/Akamai frontea dealers de DE+FR+IT a la vez).

#### (d) Riesgo adversarial concreto
- **Global**: sin esta ruta, el dedup fuerte de TODO pais queda limitado a VIN-exact y el over-count ~131.8K (faceta 20) persiste sin via lawful de colapso.
- **No-UE (JP)**: el peor caso — el numero de chasis JDM no es VIN de 17 (faceta 19) -> 0 auto-merge lawful, y con photo_hash 0% no hay NINGUNA via de identidad fuerte. Activar photo_hash es la UNICA puerta para JP.
- **Egress/bans**: un backfill ingenuo sobre la flota viva martillea hosts CDN -> bans/throttle que ademas envenenan el scrape en vivo. Un governor per-PAIS seria INCORRECTO: un host compartido por DE+FR+IT queda infra-protegido por buckets per-pais; un dealer PT en 3 hosts queda sobre-throttled por un bucket PT. El HOST es la unidad de fragilidad, no el pais.

#### (e) Criterio de sellado + verificacion multi-via
- **Mecanico**: tras cablear, asertar `photo_hash` poblado > 0 en filas recien insertadas y refrescadas (hoy 0%); test CI inserta un vehiculo por `BULK_INSERT_VEHICLES` y aserta photo_hash no-null.
- **Idempotencia/egress**: el backfill re-corrido hace 0 fetches adicionales para contenido ya hasheado (cache content_hash :120-125) -> asertar fetch-count == solo-fotos-nuevas.
- **Governor**: load test aserta que el token-bucket per-host capa el egress al host H al rate configurado bajo N workers concurrentes (PyrateLimiter PostgresBucket compartido entre procesos).
- **Via 2 (efecto)**: el photo_hash poblado DEBE reducir el over-count medido del watermark (faceta 20); asertar que la cota +/-dup_ci ENCOGE monotonamente y nunca crece al activar el brazo pHash del strong-key.

#### (f) Herramienta NEXT-LEVEL
**PyrateLimiter (RedisBucket/PostgresBucket/MultiprocessBucket)** — MIT, EUR0 [VERIFIED NEXT-LEVEL.md:304, URL https://github.com/vutran1710/PyrateLimiter]. Es exactamente el governor de egress per-host battle-tested para el backfill: `PostgresBucket` reusa el Postgres que el proyecto YA corre (cero infra nueva, EUR0) [VERIFIED :306]; trae el backend DISTRIBUIDO que permite paralelizar el backfill multi-maquina sin escribir un limiter a mano y sin re-ganar el ban por-host. Alternativa GCRA exacta: redis-cell (MIT self-host). La matematica del hash escrita por esta ruta es PDQ (faceta 12); aqui solo se PERSISTE su salida 256-bit+quality en photo_hash.

#### Resolución condensada — Faceta 13

- **Costura (ES→genérico):** Hueco GLOBAL (no ES-puro): la columna photo_hash (migrations/0003:18) existe pero ningun escritor la puebla -> 0% (cross_platform_dedup_watermark.py:21). BULK_INSERT_VEHICLES (sql.py:12-23, 14 cols) y _BULK_REFRESH_VEHICLES (delta.py:378-385) la omiten. El fix es pais-blind; la unica dimension de scope es que el governor de egress debe ser per-HOST, no per-pais.
- **Fix:** (1) Anadir photo_hash a la lista de columnas de BULK_INSERT_VEHICLES (sql.py:13-14). (2) Anadir photo_hash a _BULK_REFRESH_VEHICLES (delta.py:378-385). (3) Writer de backfill que hashea inline via download_and_hash (delta_photo.py:104-126, egress queda en el fetch inyectado :110/:114-115), gateado por token-bucket per-host (PyrateLimiter PostgresBucket reusa el PG existente). El scrape-en-vivo es egress marginal cero (bytes ya en mano); solo el backfill historico es egress real.
- **Adversarial:** Global: sin la ruta, el strong-key de TODO pais cae a VIN-exact (18 filas) y el over-count ~131.8K persiste. No-UE/JP: peor caso, chasis JDM != VIN de 17 -> 0 auto-merge lawful con pHash tambien 0%; activar photo_hash es la unica puerta. Egress: backfill ingenuo martillea hosts CDN -> bans que envenenan el scrape vivo. Governor per-PAIS es erroneo: un Cloudflare/Akamai frontea DE+FR+IT (infra-protegido) y un dealer PT en 3 hosts queda sobre-throttled; el HOST es la unidad de fragilidad.
- **Sellado multi-vía:** Mecanico: asertar photo_hash poblado > 0 en filas insertadas/refrescadas (hoy 0%); test CI inserta via BULK_INSERT_VEHICLES y aserta no-null. Idempotencia: backfill re-corrido hace 0 fetches para contenido ya hasheado (cache content_hash :120-125). Governor: load test capa egress al host H al rate bajo N workers (PostgresBucket compartido). Via 2: el photo_hash poblado debe ENCOGER monotonamente la cota +/-dup_ci del watermark (faceta 20), nunca crecerla.
- **Herramienta NEXT-LEVEL:** PyrateLimiter (RedisBucket/PostgresBucket/MultiprocessBucket) — governor de egress per-host distribuido. MIT [VERIFIED NEXT-LEVEL.md:304]. URL: https://github.com/vutran1710/PyrateLimiter. Ruta EUR0: PostgresBucket reusa el Postgres existente, cero infra nueva. La matematica del hash persistido es PDQ (faceta 12); esta ruta solo escribe su salida 256-bit+quality en photo_hash.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-14"></a>

### Faceta 14 — `diff_vehicle`: motor de delta puro

> **País-agnóstico.** Costura propia = `currency` ausente en el payload de PRICE_CHANGE.

#### (a) Code hints — VERIFIED
- `diff_vehicle(old,new) -> list[dict]`, pure, no I/O [VERIFIED delta.py:290-360]; docstring "Returns [] when nothing changed (no false positives)" (:308).
- imports [VERIFIED delta.py:67-69]: `from pipeline.delta_photo import PHASH_HAMMING_MAX, hamming, is_phash`; `from pipeline.price_sanity import sanitize_km, sanitize_price`.
- PRICE_CHANGE [VERIFIED :317-324]: `new_price = sanitize_price(getattr(new,'price',None))` (:318); NULL->valid promotion `old_price is None or float(old_price)!=float(new_price)` (:319); junk -> None -> no event.
- KM_CHANGE [VERIFIED :327-334]: same NULL->valid promotion (:329).
- PHOTO_CHANGE content-aware [VERIFIED :336-358]: if `is_phash(old_phash) and is_phash(new_phash)` (:346) compare `hamming(...) > PHASH_HAMMING_MAX` (:347); else fallback string `new_photo and old_photo != new_photo` (:353).
- `PHASH_HAMMING_MAX = 10` [VERIFIED delta_photo.py:34] explicitly labeled ASSUMED/uncalibrated [VERIFIED delta_photo.py:33: "to be CALIBRATED ... before relied upon (ASSUMED)"].

#### (b) Mechanism al atomo
A pure comparator: reads (price,km,photo_url,photo_hash) off both `old` (dict-or-attr, via isinstance branch) and `new` (attr), runs each field through its boundary sanitizer, and appends an event dict ONLY on a real change. THREE independent arms, each fail-closed to "no event": the price arm sanitizes new (junk -> None -> skip) then fires on NULL->valid OR float-inequality; the km arm is identical; the photo arm prefers pHash Hamming (> threshold = changed) and DEGRADES to exact-string compare when either side lacks a well-formed phash (backward-compatible with the 26 connectors that do not yet populate photo_hash). Returns the accumulated list (possibly empty). No mutation of inputs, no DB — the caller `emit_change_deltas` (:388-446) persists. The NULL->valid promotion (:319,:329) is the load-bearing asymmetry fix: the old `old_price is not None` guard silently dropped every first-price/first-km FILL across all 26 wholesale connectors.

#### (c) Costura ES->generico
The price arm is CURRENCY-BLIND in TWO places: (1) `sanitize_price` (facet 11) applies a single EUR-shaped `PRICE_MAX` ceiling; (2) the emitted PRICE_CHANGE payload `{"price": float(new_price)}` (:322-323) carries NO currency tag. Seam consequences: a non-EUR price above the EUR ceiling is nulled by sanitize_price -> None -> PRICE_CHANGE never fires -> the served price FREEZES (the `_BULK_REFRESH_VEHICLES` COALESCE :379-381 keeps the old); and the event payload is currency-ambiguous when serving multi-currency. The km arm carries a unit seam (km vs miles) but is physically heritable. The photo arm is country-neutral (pixels) but depends on the uncalibrated `PHASH_HAMMING_MAX=10` (facet 12) and on photo_hash being populated (0% today — facet 13). diff_vehicle's OWN seam = the missing currency dimension in the gate (inherited from facet 11) and in the payload (its own to fix).

#### (d) Riesgo adversarial
- **JP (JPY)**: a normal car is Y6M-Y40M, exceeds `PRICE_MAX=5_000_000` -> `sanitize_price` -> None -> PRICE_CHANGE never fires -> price frozen forever via COALESCE. CRITICAL (B3); the same nulling kills Signal B's non-null-price gate (facet 7).
- **GBP/CHF**: a legit 8000 -> 8200 GBP change fires numerically, but the payload `{"price":8200}` is currency-blind and a multi-market consumer reads it as EUR.
- **non-EU miles markets (US / partial UK)**: the km arm treats an odometer in miles as km — a 60k-mile car vs a 60k-km car produce no KM_CHANGE despite different mileage.
- **Noise**: a CDN that ROTATES photo_url on an unchanged image — the pHash arm (:346-347) correctly suppresses the false PHOTO_CHANGE the string fallback (:353) would fire; but with photo_hash 0%-populated (facet 13) the pHash arm is INERT and every URL rotation false-fires.

#### (e) Sellado + verificacion multi-via
- (1) ES golden: fixtures (price up/down, NULL->valid fill, km fill, photo rotate) -> exact expected event list; and `diff_vehicle(snap, no-change) == []` (zero false positives).
- (2) Per-currency fixture: a JPY price UNDER a JPY ceiling MUST produce PRICE_CHANGE (B3 fixture goes green) while EUR junk is still nulled — proves the ceiling is currency-parametric (facet 11) and the payload carries currency.
- (3) Orthogonal: count of PRICE_CHANGE rows in vehicle_event == count of price-deltas recomputed by a direct SQL snapshot diff (independent mechanism).
- (4) Property (Hypothesis): for all (old,new), diff_vehicle is IDEMPOTENT (re-running on the post-state yields []) and never emits an event whose old == new.
- (5) The pHash arm is sealed ONLY after `PHASH_HAMMING_MAX` is calibrated (facet 12) against a labeled same/different-car set.

#### (f) Herramienta NEXT-LEVEL
**price-parser** — BSD-3-Clause — https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:503-509]. Extracts amount+currency from the raw listing string at INGEST so `vehicle.currency` is reliably populated (today connectors trust DEFAULT 'EUR'); **Babel** (CLDR) resolves per-locale number/currency formats and decimal handling; **py-moneyed** gives currency-safe money arithmetic for a per-currency `PRICE_MAX` in the CountryProfile. The fix chain: currency into the comparison context -> assert same-currency -> per-currency ceiling, so a normal JPY price SURVIVES sanitize_price and PRICE_CHANGE fires. All three are permissive, pure-Python, offline (CLDR bundled with Babel), with NO FX service (comparisons are intra-currency by construction). Directly dissolves the B3 CRITICAL. The PHOTO_CHANGE arm's elevation is owned by facet 12 (PDQ/pHash calibration) and facet 13 (photo_hash backfill).

#### Resolución condensada — Faceta 14

- **Costura (ES→genérico):** diff_vehicle's PRICE_CHANGE is currency-blind in two places: the `sanitize_price` gate applies a single EUR-shaped PRICE_MAX (inherited from facet 11) and the emitted payload `{"price": float(new_price)}` [delta.py:322-323] carries no currency tag. The km arm assumes km units (not miles); the photo arm depends on the uncalibrated PHASH_HAMMING_MAX=10 [delta_photo.py:34, labeled ASSUMED :33] and on photo_hash being populated (0% today — facet 13).
- **Fix:** Parameterize PRICE_MAX per currency (facet 11) and add a `"currency"` key to the PRICE_CHANGE old/new payloads at delta.py:322-323; populate vehicle.currency at the boundary via price-parser (facet 9). Keep the NULL->valid promotion (:319,:329) and the pHash-first/string-fallback photo logic unchanged — both already generic. The diff_vehicle-owned delta is the currency tag in the event payload.
- **Adversarial:** JP (JPY): a Y6M-Y40M car exceeds PRICE_MAX=5,000,000 -> sanitize_price -> None -> PRICE_CHANGE never fires -> served price frozen by COALESCE (CRITICAL B3). GBP/CHF: numeric change fires but the currency-blind payload is misread as EUR downstream. Miles markets: km arm treats miles as km, no KM_CHANGE between a 60k-mile and a 60k-km car. Noise: with photo_hash 0%-populated the pHash suppressor is inert, so every CDN URL-rotation false-fires PHOTO_CHANGE via the string fallback (:353).
- **Sellado multi-vía:** (1) ES golden event-list fixtures + `diff_vehicle(no-change)==[]`. (2) Per-currency fixture: a JPY price under the JPY ceiling fires PRICE_CHANGE while EUR junk is still nulled. (3) Orthogonal SQL snapshot-diff count == vehicle_event PRICE_CHANGE count. (4) Hypothesis idempotence property (re-run on post-state ⇒ []). (5) pHash arm sealed only post-calibration of PHASH_HAMMING_MAX (facet 12).
- **Herramienta NEXT-LEVEL:** price-parser (BSD-3-Clause) https://github.com/scrapinghub/price-parser [VERIFIED NEXT-LEVEL.md:506] + Babel (CLDR locale/currency) + py-moneyed (currency-safe money). Populates vehicle.currency at ingest and drives a per-currency PRICE_MAX; intra-currency by construction (no FX service). Dissolves the B3 JPY-nulled-price CRITICAL. (PHOTO_CHANGE elevation owned by facet 12 / facet 13.)

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-15"></a>

### Faceta 15 — `emit_change_deltas`: emisión DRY landing-time (re-vistos)

> **DRY país-agnóstico.** Costura = durabilidad/idempotencia landing-time.

#### (a) code_hints verificados al atomo
- [VERIFIED pipeline/delta.py:369-376] `_BULK_INSERT_DELTA_EVENTS`: `INSERT INTO vehicle_event (event_ulid, vehicle_ulid, entity_ulid, event_type, old_value, new_value) SELECT ... FROM unnest($1::text[]..$6::text[])` -- append bulk de eventos (6 arrays).
- [VERIFIED :378-385] `_BULK_REFRESH_VEHICLES`: `UPDATE vehicle v SET price = COALESCE(u.price, v.price), km = COALESCE(u.km, v.km), photo_url = COALESCE(u.photo_url, v.photo_url) FROM unnest($1..$4) WHERE v.vehicle_ulid = u.vehicle_ulid` -- refresca SOLO `price/km/photo_url`, **NO `photo_hash`** (acopla faceta 13); `COALESCE` mantiene el viejo si el nuevo es junk/NULL.
- [VERIFIED :388-446] `emit_change_deltas(conn, existing_snap, new_vehicles, keys)`: itera `keys`; **salta los genuinamente nuevos** (`snap is None -> continue`, :419-420; "handled by the NEW-event path"); salta si falta `new_obj` (:422-423); `events = diff_vehicle(snap, new_obj)` (:424); salta si `not events` (:425-426); `ent = key[0] if isinstance(key, tuple)` (:429); construye arrays de evento + de refresh; en el refresh aplica `sanitize_price`/`sanitize_km` (:439-440 -> "junk -> None -> COALESCE keeps old (no junk write)"); ejecuta `_BULK_INSERT_DELTA_EVENTS` (:443) y luego `_BULK_REFRESH_VEHICLES` (:445); devuelve counts por tipo (:446).
- [VERIFIED pipeline/platform/wallapop_wholesale.py:971-972] call-site: `_dc = await emit_change_deltas(conn, existing_snap, {k: cars[k].vehicle for k in car_keys}, car_keys)`; stats agregadas :973-975. (El path NEW va aparte: `_BULK_INSERT_VEHICLES` :980-988.)

#### (b) Mecanismo al atomo
Por cada `key` **re-visto**: `diff_vehicle` (faceta 14) compara snapshot DB vs scrape y devuelve eventos PRICE/KM/PHOTO_CHANGE; los **nuevos** (sin snapshot) saltan al path NEW del conector (`BULK_INSERT_VEHICLES` + `BULK_INSERT_EVENTS` en `_core/sql.py`). El bulk `UPDATE` toca **solo filas que cambiaron** (MVCC-limpio). `COALESCE(sanitize_price(...), v.price)` -> precio junk se nula y se mantiene el servido (correcto, pero **enmascara** dato perdido). Es **seguro en cosecha parcial**: toca solo re-vistos, **jamas retira** (GONE es aparte, coverage-gated, faceta 16). Es **DRY**: una implementacion, ~28 call-sites; la semantica delta se prueba una vez.

#### (c) Costura ES -> generico
La funcion es ya **country-blind** (opera sobre ulids opacos + atributos fisicos); no tiene molde ES. Las costuras son **multi-moneda** y **durabilidad**, no pais:
1. **Moneda en el payload**: el evento PRICE_CHANGE (via `diff_vehicle`, faceta 14) no registra `currency`; el refresh escribe `price` sin contexto de moneda -> ambiguo al servir multi-moneda (acopla faceta 9).
2. **photo_hash no se refresca**: `_BULK_REFRESH_VEHICLES` (:378-385) omite `photo_hash` -> el PHOTO_CHANGE content-aware y el strong-key quedan a medias (acopla faceta 13).
3. **Idempotencia solo-en-codigo**: `vehicle_event` no tiene UNIQUE (faceta 2) -> la no-duplicacion de eventos depende de la disciplina de emitir-una-vez; un re-call o un crash entre `:443` (insert eventos) y `:445` (refresh) puede dejar eventos sin refresh o duplicar eventos.

#### (d) Riesgo adversarial concreto
- **No-UE/no-EUR (JP)**: un precio JPY refrescado donde `sanitize_price` (PRICE_MAX=5M, faceta 11) lo nula -> `COALESCE` mantiene el precio **stale** -> PRICE_CHANGE **nunca dispara** -> precio servido congelado. CRITICAL (via acople 11/14).
- **Crash/duplicado**: matar el worker entre la insercion de eventos (:443) y el refresh (:445) -> eventos escritos sin el refresh asociado; o un conector que doble-llame -> GONE/CHANGE duplicado en un timeline que se asume inmutable (sin UNIQUE que lo frene).
- **DE/FR/IT/PT (EUR)**: benignos hoy para moneda; el unico riesgo es el de duplicacion/crash, agnostico de pais.

#### (e) Sellado + verificacion multi-via
- **Via 1 (golden DRY)**: `diff_vehicle` devuelve `[]` cuando nada cambio (cero eventos falsos), probado una vez, cubre los ~28 conectores.
- **Via 2 (MVCC)**: filas actualizadas por `_BULK_REFRESH_VEHICLES` == numero de keys con eventos (no toca filas sin cambio).
- **Via 3 (crash-safety)**: matar el worker entre insert (:443) y refresh (:445) **no** debe dejar eventos sin refresh **ni** duplicar eventos -- exige la elevacion a tarea durable.
- **Via 4 (invariante de cosecha parcial)**: `emit_change_deltas` nunca escribe `status` -> jamas retira inventario.

#### (f) Herramienta NEXT-LEVEL
**Procrastinate** (tareas durables Postgres-nativas) — MIT, €0 — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555]. Convierte la emision landing-time en una **tarea durable, idempotente y reintentada**: claim exactamente-una-vez (`FOR UPDATE SKIP LOCKED`), retry con backoff, y reanudacion a mitad de vuelo tras crash -- cerrando el hueco "la idempotencia vive SOLO en codigo / vehicle_event sin UNIQUE" con semantica exactly-once y resume. **Cero infra nueva** (corre sobre el PG existente, :557). Alternativas €0 listadas [VERIFIED :556]: DBOS Transact, pgqueuer (mas ligera, LISTEN/NOTIFY + SKIP LOCKED).

#### Resolución condensada — Faceta 15

- **Costura (ES→genérico):** emit_change_deltas es ya country-blind (ulids opacos + atributos fisicos); sin molde ES. Las costuras son multi-moneda y durabilidad: (1) el payload PRICE_CHANGE (via diff_vehicle, faceta 14) no registra currency y el refresh escribe price sin moneda (acopla faceta 9); (2) _BULK_REFRESH_VEHICLES (delta.py:378-385) NO refresca photo_hash (acopla faceta 13); (3) vehicle_event sin UNIQUE (faceta 2) -> idempotencia solo-en-codigo, fragil ante re-call o crash entre :443 (insert eventos) y :445 (refresh).
- **Fix:** 1) La emision en si es ya generica/DRY (1 impl, ~28 call-sites) -- mantener. 2) Anadir currency al payload PRICE_CHANGE (facetas 9/14). 3) Anadir photo_hash a la lista de columnas de _BULK_REFRESH_VEHICLES (:378-385, faceta 13). 4) Elevar la emision a tarea durable para que el hueco de idempotencia (sin UNIQUE en vehicle_event) gane semantica exactly-once (claim + resume).
- **Adversarial:** JP/no-EUR: precio JPY refrescado que sanitize_price (PRICE_MAX=5M, faceta 11) nula -> COALESCE mantiene el stale -> PRICE_CHANGE nunca dispara -> precio servido congelado. CRITICAL (acople 11/14). Crash entre insert eventos (:443) y refresh (:445) deja eventos sin refresh; un doble-call duplica eventos en un timeline asumido inmutable (sin UNIQUE que lo frene). DE/FR/IT/PT (EUR) benignos salvo el riesgo de duplicacion/crash, agnostico de pais.
- **Sellado multi-vía:** Via 1: golden DRY -- diff_vehicle devuelve [] sin cambios (cero eventos falsos), probado una vez, cubre ~28 conectores. Via 2: MVCC -- filas refrescadas == keys con eventos. Via 3: crash-safety -- matar worker entre :443 y :445 no deja eventos sin refresh ni duplica (exige tarea durable). Via 4: emit_change_deltas nunca escribe status -> jamas retira inventario (cosecha parcial segura).
- **Herramienta NEXT-LEVEL:** Procrastinate (tareas durables sobre el Postgres existente) — MIT — https://github.com/procrastinate-org/procrastinate [VERIFIED NEXT-LEVEL.md:555]. Eleva la emision landing-time a tarea durable: claim exactamente-una-vez (FOR UPDATE SKIP LOCKED), retry con backoff, resume tras crash -> cierra el hueco 'idempotencia solo-en-codigo / vehicle_event sin UNIQUE' con exactly-once. Cero infra nueva (:557). Alts €0: DBOS Transact, pgqueuer [VERIFIED :556].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-16"></a>

### Faceta 16 — `reconcile_gone`: baja de stale source-scoped + coverage-gate

> **País-agnóstico.** Depende de `source_coverage.verdict` por fuente; under-retirement honesto.

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/delta.py:146-283` — `reconcile_gone(conn, source_key, run_started_at, *, max_gone_fraction=0.5, min_coverage=None)`. [VERIFIED]
- `delta.py:107` — `MIN_INVENTORY_FOR_GUARD = 20` (umbral bajo el cual el guard de fraccion NO se aplica). [VERIFIED]
- **Coverage gate** `delta.py:188-201`: si `min_coverage is not None`, lee `SELECT coverage_pct, verdict FROM source_coverage WHERE source_key=$1`; aborta (`return 0, ...`) si no hay verdict (:191-193), si `coverage_pct < min_coverage` (:195-198), o si `verdict == 'REFUTED'` (:199-201). Lema "Better a hole than a lie" (:187). [VERIFIED]
- **Denominador** `delta.py:204-216`: `COUNT(*)` de vehiculos `available` del source via `entity_source`; si 0 -> no-op. [VERIFIED]
- **Candidatos stale** `delta.py:219` via `_FIND_STALE` (`delta.py:77-84`): `status='available' AND last_seen < run_started_at`, JOIN `entity_source` por `source_key` (source-scoped). [VERIFIED]
- **Fraction cap** `delta.py:229-238`: `fraction = stale/available`; si `available >= MIN_INVENTORY_FOR_GUARD AND fraction > max_gone_fraction(0.5)` -> ABORTA sin tocar nada. [VERIFIED]
- **Transaccion unica** `delta.py:245`: `async with conn.transaction():` envuelve todo el barrido (atomico: o todas o ninguna). [VERIFIED]
- **Status guard de carrera** `delta.py:264-266`: `_MARK_GONE` (`delta.py:86-92`) hace `UPDATE ... WHERE status='available'`; si devuelve `"UPDATE 0"` -> `continue` (no emite GONE duplicado, no hay UNIQUE en vehicle_event). [VERIFIED]
- **Evento** `delta.py:271-273` via `_INSERT_GONE_EVENT` (`delta.py:94-98`): `old_value={"price": float|null}` snapshot, `new_value=NULL`. [VERIFIED]

#### (b) El mecanismo al atomo
`reconcile_gone` es la **baja con presuncion de inocencia**. La doctrina es "mejor un hueco que una mentira": jamas retira inventario salvo prueba de que el harvest fue completo. Tres anillos de defensa, en orden:
1. **Coverage gate (DB-backed, opcional)**: consulta `source_coverage` (la senal B9 de completitud captured/declared). Sin verdict -> no retira. `coverage_pct < floor` -> no retira (los no-vistos son "probablemente no-capturados, NO idos"). `verdict='REFUTED'` (conteos inconsistentes) -> no retira.
2. **Fraction cap (auto-contenido, no confia en el caller)**: aunque pase coverage, si el barrido retiraria >50% de un inventario no-trivial (>=20), aborta — una contraccion real de >50% entre dos runs es casi seguro un harvest roto, no churn. Reemplazo explicito del viejo `min_captured` que nunca comparaba captured-vs-expected (delta.py:167-170).
3. **Atomicidad + race guard**: todo en UNA transaccion (delta.py:245); cada `_MARK_GONE` guarda en `status='available'` para que una retirada concurrente (otro conector, re-run) no genere un GONE duplicado en el timeline inmutable (delta.py:259-266).

`source_key` lo hace **source-scoped**: nunca contamina otra fuente. Es idempotente: un segundo run con el mismo `run_started_at` es no-op (los ya-gone los salta el filtro `status='available'`).

#### (c) La costura ES->generico
El mecanismo es **estructuralmente pais-agnostico**: opera sobre `source_key` + `last_seen` + ratios de completitud (0.95/0.50/0.50), todos agnosticos de pais. La unica costura es la DEPENDENCIA del `source_coverage` por fuente:
- El coverage gate solo protege si EXISTE un verdict de coverage para ese `source_key`. Un pais nuevo cuyas fuentes aun no producen verdict de coverage -> `min_coverage` se pasa `None` o el gate aborta -> **no retira nada** (correcto y seguro, pero deja stale vivo: hueco honesto, no mentira).
- El `max_gone_fraction=0.5` y `MIN_INVENTORY_FOR_GUARD=20` son heuristicas mercado-agnosticas razonables; no requieren re-calibracion por pais, pero una contraccion legitima >50% (p.ej. un dealer que liquida) queda bloqueada hasta confirmar (falso-negativo aceptado por doctrina).
**Fix de costura**: ninguno en el algoritmo; lo que falta es que el pipeline de coverage (faceta externa) emita `source_coverage.verdict` por `source_key` para CADA pais, y cablear `min_coverage` en los call-sites de los conectores del pais nuevo.

#### (d) Riesgo adversarial concreto
- **Pais nuevo sin coverage (DE/FR/IT/PT/no-UE)**: sin verdict de coverage, el gate se niega a retirar -> stale acumulado (hueco), nunca una baja falsa. El riesgo NO es over-retirement sino UNDER-retirement silencioso hasta que el pipeline de coverage cubra esas fuentes.
- **Contraccion real >50%**: un mercado que de verdad pierde >50% de inventario entre runs queda bloqueado por el fraction cap hasta verificacion manual — falso-negativo por diseno ("better a hole than a lie").
- **Ruido/harvest parcial**: el escenario que el guard EXISTE para matar — wallapop capturando 5k de 588k (delta.py:169) habria retirado el ~99%; coverage gate + fraction cap lo abortan.
- **Carrera multi-conector**: dos conectores del mismo pais retirando concurrentemente -> el race guard `WHERE status='available'` evita el GONE duplicado (critico porque vehicle_event no tiene UNIQUE).

#### (e) Criterio de sellado + verificacion multi-via
**Sellado** = `reconcile_gone` NUNCA retira sobre un harvest no-probadamente-completo, en ningun pais, y jamas duplica un GONE.
- **Via 1 (test)**: harvest parcial simulado (captured << declared) -> 0 retiros; harvest completo (coverage>=floor, verdict!=REFUTED, fraction<=0.5) -> retira exactamente los stale.
- **Via 2 (ortogonal, DB)**: tras un run, `COUNT` de `status='gone'` nuevos == filas stale elegibles; y `GROUP BY vehicle_ulid HAVING COUNT(*)>1` sobre GONE == 0 (no duplicados).
- **Via 3 (adversarial)**: forzar `verdict='REFUTED'` y `coverage_pct` justo por debajo del floor y confirmar abort; forzar `fraction=0.51` sobre inventario >=20 y confirmar abort.
- **Via 4 (fail-closed contract)**: codificar las precondiciones (verdict presente, coverage>=floor, fraction plausible) como contrato ejecutable que BLOQUEA el barrido ante violacion, en vez de `if` inline.

#### (f) Herramienta NEXT-LEVEL que lo eleva
**Great Expectations** (contrato de datos pre-barrido, fail-closed) — Apache-2.0, EUR0=True — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Convierte las precondiciones OCULTAS de la baja (coverage presente, `>=floor`, `verdict != REFUTED`, fraccion plausible) en **expectativas ejecutables, versionadas y BLOQUEANTES**: el estrato/source falla CERRADO, no abierto — la forma institucional del lema "better a hole than a lie" (delta.py:187). La revision manual jamas atrapa un fallo-abierto; la maquina si [VERIFIED NEXT-LEVEL.md:166]. Es Python puro, corre en CI y pre-barrido, sin coste [VERIFIED NEXT-LEVEL.md:169]. Complementos verificados: **transitions (pytransitions)** (MIT, https://github.com/pytransitions/transitions [VERIFIED NEXT-LEVEL.md:595]) para modelar la baja como una TRANSICION legal solo desde un estado COMPLETE de coverage (sin default-allow); **Healthchecks** (BSD-3-Clause, https://github.com/healthchecks/healthchecks [VERIFIED NEXT-LEVEL.md:563]) como dead-man switch EXTERNO que confirma con su propio reloj que el harvest corrio a termino antes de autorizar cualquier retiro.

#### Resolución condensada — Faceta 16

- **Costura (ES→genérico):** El algoritmo es estructuralmente pais-agnostico: opera sobre source_key + last_seen + ratios de completitud (max_gone_fraction=0.5 delta.py:230, MIN_INVENTORY_FOR_GUARD=20 :107), todos agnosticos de pais. Unica costura: el coverage gate (delta.py:188-201) depende de que exista source_coverage.verdict por source_key; un pais nuevo cuyas fuentes aun no producen verdict -> el gate se niega a retirar (hueco honesto, no mentira). No hay re-calibracion de algoritmo por pais.
- **Fix:** Ningun cambio en el algoritmo. Costura externa: (1) que el pipeline de coverage emita source_coverage.verdict por source_key para CADA pais; (2) cablear min_coverage en los call-sites de los conectores del pais nuevo. El fraction cap 0.5 y MIN_INVENTORY_FOR_GUARD=20 se heredan tal cual (mercado-agnosticos).
- **Adversarial:** Pais nuevo sin coverage (DE/FR/IT/PT/no-UE): el gate se niega a retirar -> riesgo es UNDER-retirement silencioso (stale vivo), nunca baja falsa. Contraccion real >50%: bloqueada por el fraction cap hasta verificacion manual (falso-negativo por diseno). Harvest parcial (wallapop 5k/588k, delta.py:169): coverage gate + fraction cap lo abortan (el escenario que el guard existe para matar). Carrera multi-conector: el race guard WHERE status='available' (delta.py:264-266) evita el GONE duplicado (critico: vehicle_event sin UNIQUE).
- **Sellado multi-vía:** Sellado = jamas retira sobre harvest no-probadamente-completo en ningun pais, jamas duplica GONE. Multi-via: (1) harvest parcial simulado -> 0 retiros, harvest completo -> retira exactamente los stale; (2) DB ortogonal: gone-nuevos == stale elegibles, y GROUP BY vehicle_ulid HAVING COUNT(*)>1 sobre GONE == 0; (3) adversarial: verdict=REFUTED y coverage<floor -> abort, fraction=0.51 sobre >=20 -> abort; (4) precondiciones como contrato ejecutable fail-closed.
- **Herramienta NEXT-LEVEL:** Great Expectations (contrato de datos pre-barrido, fail-closed) — Apache-2.0, EUR0=True — https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:167]. Codifica las precondiciones de la baja (coverage presente, >=floor, verdict!=REFUTED, fraccion plausible) como expectativas bloqueantes: el source falla CERRADO = forma institucional de 'better a hole than a lie'. Complementos: transitions/pytransitions (MIT, NEXT-LEVEL.md:595) -> baja como transicion legal solo desde estado COMPLETE; Healthchecks (BSD-3-Clause, NEXT-LEVEL.md:563) -> dead-man switch externo que confirma harvest completo antes de retirar.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-17"></a>

### Faceta 17 — `emit_gone_events`: baja en timeline para conectores edge-set

> **Hueco GLOBAL.** Idempotencia del GONE solo-en-código (sin `UNIQUE`).

#### (a) code_hints VERIFICADOS
- `pipeline/delta.py:110-143` [VERIFIED] `emit_gone_events(conn, vehicle_ulids)`:
  - bucle por ulid :129; `fetchrow` de `(entity_ulid, price)` de `vehicle` :130-131.
  - **skip huerfano** :132-133 (`row is None or entity_ulid is None`).
  - **idempotencia en codigo** :134-138: `SELECT 1 FROM vehicle_event WHERE vehicle_ulid=$1 AND event_type='GONE' LIMIT 1` -> si existe, `continue` (nunca duplica GONE).
  - **old_value snapshot** :139: `{"price": float(price) if price is not None else None}`.
  - INSERT via `_INSERT_GONE_EVENT` con `ulid(), vulid, entity_ulid, json.dumps(old_value)` :140-141; `emitted+=1` :142.
- Docstring :114-127 explicita el contrato: **espeja reconcile_gone**, un GONE por vehiculo, `new_value=null`, `observed_at` default now(); **"the timeline has no UNIQUE on (vehicle_ulid, event_type), so dedup is enforced here"** :124-125; el caller **debe** haber fijado `status='gone'` (contrato implicito) :125-126; audit P4 = **1.823 bajas silenciosas** de group_subastas/localizavo :118-120.

#### (b) Mecanismo al atomo
Dos conectores (group_subastas_wholesale, localizavo_wholesale) retiran lotes por su **propio edge-set de plataforma** (no por `last_seen`), asi que no pueden pasar por `reconcile_gone`. Antes, flipeaban `vehicle.status='gone'` **sin** emitir el evento -> el timeline inmutable (faceta 2) perdia 1.823 bajas. `emit_gone_events` es el helper compartido que garantiza que TODA baja queda en el log append-only. El atomo critico es la **idempotencia en codigo** :134-138: como `vehicle_event` **no tiene** `UNIQUE(vehicle_ulid,event_type)`, la unica defensa contra un GONE duplicado es el `SELECT 1 ... LIMIT 1` previo. Es un **check-then-insert no atomico**: entre el SELECT y el INSERT no hay candado -> dos invocaciones concurrentes sobre el mismo ulid pueden ambas ver "no existe" y ambas insertar (TOCTOU).

#### (c) Costura ES->generico
**Hueco GLOBAL, no ES-puro:** la idempotencia vive 100% en este codigo, no en el esquema. Es country-blind (opera sobre ulids/price), asi que el comportamiento es identico en cualquier pais - pero tambien el **fallo** es identico en cualquier pais. Fix exacto en dos capas:
1. **Piso mecanico en-DB (la verdad):** `CREATE UNIQUE INDEX CONCURRENTLY ... ON vehicle_event (vehicle_ulid) WHERE event_type='GONE'` - indice UNIQUE **parcial** que hace la duplicacion **estructuralmente imposible** (la maquina impone la regla, no el codigo). Cierra el TOCTOU y a cualquier emisor que sortee este helper. Doctrina NEXT-LEVEL: "hacer que la maquina la imponga".
2. **Contrato + INSERT defensivo:** cambiar el INSERT a `... ON CONFLICT DO NOTHING` (apoyado en el indice) y un data-contract pre-serve que asevera "0 `vehicle_ulid` con >1 GONE".

#### (d) Riesgo adversarial
- **Emisor que sortea el helper:** cualquier conector futuro (pais #2) que flipee `status='gone'` y escriba el evento por su cuenta **sin** el SELECT-guard duplica la baja en un timeline que se asume inmutable -> el conteo de bajas miente. La idempotencia "vive SOLO en este codigo".
- **Concurrencia (TOCTOU):** dos drains del mismo conector (o un retry solapado) sobre el mismo lote -> doble INSERT (sin UNIQUE que lo pare).
- **Contrato implicito roto:** el caller **debe** fijar `status='gone'` antes (:125-126); un conector nuevo que llame en orden inverso emite GONE sobre una fila aun 'available' -> estado incoherente (evento de baja + fila viva).
- **DE/FR/IT/non-EU:** sin particularidad de locale, pero **mas conectores edge-set** = mas superficie para el sorteo; el riesgo escala con el numero de plataformas, no con el pais.

#### (e) Sellado + verificacion multi-via
- **Via 1 (invariante en-DB):** tras crear el indice parcial UNIQUE, `SELECT vehicle_ulid, COUNT(*) FROM vehicle_event WHERE event_type='GONE' GROUP BY 1 HAVING COUNT(*)>1` -> **0 filas** (mecanico, no esperanza).
- **Via 2 (property-based/adversarial):** Hypothesis genera secuencias de emision adversariales (ulids duplicados en una llamada, re-invocacion, lotes solapados) y afirma la propiedad "exactamente un GONE por vehicle_ulid, jamas duplicado"; el fuzzer **minimiza** al contraejemplo y lo congela como regression-fixture.
- **Via 3 (idempotencia funcional):** invocar `emit_gone_events` dos veces con el mismo lote -> el segundo retorna `emitted=0` y el conteo de eventos no cambia.
- **Via 4 (cierre del audit P4):** re-correr el chequeo "filas con status='gone' sin evento GONE" -> 0 (las 1.823 silenciosas quedan cubiertas y no reaparecen).

#### (f) Herramienta nivel-inalcanzable
**Hypothesis** (MPL-2.0, EUR0) - https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:317-323]: property-based testing que **caza el caso de la esquina** que el golden no ve - genera adversarialmente las secuencias de emision (duplicado, concurrente, orden invertido) y prueba el invariante de idempotencia; minimiza al contraejemplo minimo y lo deja como fixture deterministica. Es la 2a via adversarial del ritual hecha mecanica. **Great Expectations / Pandera** (Apache-2.0 / MIT, EUR0) - https://github.com/great-expectations/great_expectations [VERIFIED NEXT-LEVEL.md:164-170]: contrato de datos pre-serve que **falla CERRADO** - asevera "0 vehicle_ulid con >1 GONE" como expectativa versionada y bloqueante, convirtiendo la precondicion oculta en invariante probado. El piso real de la correccion es el indice UNIQUE parcial en-DB; Hypothesis lo PRUEBA y Great Expectations lo VIGILA en runtime - el trio cierra el hueco que el codigo-solo deja abierto.

#### Resolución condensada — Faceta 17

- **Costura (ES→genérico):** Hueco GLOBAL (no ES-puro): la idempotencia del GONE vive 100% en codigo (delta.py:134-138 SELECT-then-insert), NO en el esquema - vehicle_event carece de UNIQUE(vehicle_ulid,event_type) (docstring :124-125). Check-then-insert no atomico (TOCTOU).
- **Fix:** Dos capas. (1) Piso en-DB: CREATE UNIQUE INDEX CONCURRENTLY ON vehicle_event(vehicle_ulid) WHERE event_type='GONE' -> duplicado estructuralmente imposible, cierra TOCTOU y emisores que sorteen el helper. (2) INSERT ... ON CONFLICT DO NOTHING + data-contract pre-serve '0 vehicle_ulid con >1 GONE'.
- **Adversarial:** Emisor pais#2 que flipea status='gone' y escribe el evento sin el SELECT-guard duplica la baja (idempotencia solo-en-codigo). Concurrencia TOCTOU: dos drains/retry solapados sobre el mismo lote -> doble INSERT. Contrato implicito: caller debe fijar status='gone' antes (:125-126); orden inverso emite GONE sobre fila 'available'. Riesgo escala con el nº de conectores edge-set, no con el pais.
- **Sellado multi-vía:** Via1 invariante en-DB: GROUP BY vehicle_ulid HAVING COUNT(*)>1 sobre GONE = 0 filas (mecanico). Via2 Hypothesis: secuencias adversariales (duplicado/concurrente/orden) afirman 'un solo GONE por ulid', contraejemplo congelado. Via3 idempotencia funcional: 2a invocacion del mismo lote -> emitted=0, conteo inalterado. Via4 cierre audit P4: 0 filas status='gone' sin evento GONE.
- **Herramienta NEXT-LEVEL:** Hypothesis (MPL-2.0, https://github.com/HypothesisWorks/hypothesis) [VERIFIED NEXT-LEVEL.md:317-323] = property-based fuzz que prueba el invariante de idempotencia y minimiza el contraejemplo. Great Expectations/Pandera (Apache-2.0/MIT, https://github.com/great-expectations/great_expectations) [VERIFIED :164-170] = contrato fail-closed '0 ulid con >1 GONE'. Piso real = indice UNIQUE parcial en-DB; Hypothesis lo prueba, GE lo vigila.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-18"></a>

### Faceta 18 — `delta_guard`: probe de completitud declared/previous

> **Ratios país-agnósticos.** Costura = cobertura/adopción en los conectores.

#### (a) Code hints [VERIFIED]
- [VERIFIED pipeline/delta_guard.py:54] `DECLARED_THRESHOLD: float = 0.95`.
- [VERIFIED delta_guard.py:59] `PREVIOUS_THRESHOLD: float = 0.50`.
- [VERIFIED delta_guard.py:66-141] `should_emit_gone(harvested, declared, previous_available)`:
  - Branch 1 (declared no-None, :91): **supresion anomalia** `declared==0 and previous_available is not None and previous_available>0` -> `(False, 'gateway anomaly...')` (:97-102); si no, `threshold = declared*0.95` (:103), `harvested >= threshold` -> True (:104-109), si no -> partial False (:110-115).
  - Branch 2 (declared None, :117): `previous_available is None or ==0` -> True (primer run, nada que retirar, :118-125); si no, `threshold = previous*0.50` (:127), `harvested >= threshold` -> True (:128-134), si no -> False (:135-141).
- [VERIFIED delta_guard.py:88] docstring: 'All branches are explicit - no silent default-allow on ambiguous inputs.'
- [VERIFIED delta_guard.py:144-165] TODO de adopcion: `group_subastas_wholesale.py ~1005`, `localizavo_wholesale.py ~801`, `subastacar_wholesale.py ~813` solo gatean por `fetch_error is None` (cubre fallos duros, NO un drain parcial silencioso sin excepcion).

#### (b) Mecanismo al atomo
Funcion pura de decision con dos probes y cero default-allow. Probe primario (declared): el sitio reporta su propio total (numberOfResults/totalHits); el sweep GONE solo dispara si `harvested >= declared*0.95` (el 5% absorbe colisiones de dedup cross-pagina). Probe fallback (previous_available): sin total declarado, cae al ultimo count conocido de la DB y exige `harvested >= previous*0.50` (piso conservador: pilla un timeout a mitad de drain pero permite contracciones legitimas de hasta 49%). El atomo de seguridad es la supresion de `declared=0`: un 200 valido con count=0 + items vacios (fallo de tenant-scope) daria `threshold=0` y `harvested=0 >= 0 = True`, autorizando un wipe de stock vivo; se suprime self-consistente cuando hay inventario previo. Todas las ramas son explicitas: ningun input ambiguo cae en allow silencioso.

#### (c) Costura ES->generico
Los ratios 0.95/0.50 son FRACCIONES DE COMPLETITUD (agnosticas de pais/moneda/geo); el docstring (:14-21) es honesto en esto. La costura NO es el umbral: es la COBERTURA/ADOPCION. Los tres conectores wholesale (:148-156) y los que no tienen sweep gatean solo por `fetch_error`, asi que un drain parcial sin excepcion puede barrer GONE sin pasar por el guard. Un pais #2 con conectores nuevos hereda ese hueco.

#### (d) Riesgo adversarial concreto
`declared=0` por anomalia de gateway (200 valido + items vacios): suprimido SOLO si el caller pasa `previous_available>0` (:97); un conector que pase `previous_available=None` en esa rama SORTEA la supresion y autoriza el wipe. `previous_available` STALE (cache vieja en vez de SELECT COUNT fresco) derrota el fallback - el modulo lo advierte (:20-21) pero no lo impone. Conectores no-adoptados (DE/FR/IT/PT nuevos) sin ratio-guard barren GONE ante un timeout silencioso. Ruido: una contraccion real de inventario >50% queda bloqueada hasta confirmar (correcto pero requiere intervencion).

#### (e) Sellado + verificacion multi-via
1. Test anomalia: `should_emit_gone(harvested=0, declared=0, previous_available=20)` -> `(False, ...)` (no wipe).
2. Prueba por-propiedades (tool): NINGUNA combinacion (harvested, declared, previous) devuelve True cuando `harvested < min(declared*0.95, previous*0.50)` y hay inventario - generada adversarialmente, no enumerada.
3. Auditoria de adopcion mecanica: un test de CI enumera los conectores con sweep GONE/reconcile y asevera que CADA UNO llama `should_emit_gone` (cierra el TODO :144-165 con un build ROJO si falta).
4. Via independiente: el contraejemplo minimo de Hypothesis se congela como regression-fixture determinista.

#### (f) Herramienta NEXT-LEVEL
[VERIFIED NEXT-LEVEL.md:317-323] **Hypothesis (MPL-2.0)** https://github.com/HypothesisWorks/hypothesis. `should_emit_gone` es una funcion de decision con umbrales: property-based testing GENERA el lattice (harvested, declared, previous_available) adversarialmente y PRUEBA el invariante de no-falso-wipe sobre TODO el espacio (incluida la anomalia declared=0 y los boundary ratios), minimiza al contraejemplo mas simple y lo congela como golden. Es por construccion la 2a via adversarial del ritual. EUR0, CPU puro, CI local, se integra en el job db-tests/unit existente. Complemento: Pydantic (MIT, NEXT-LEVEL:587) como CONTRATO TIPADO del input de harvest-stats para que un conector no pueda pasar senales de completitud malformadas (previous_available stale/None donde debia ir int).

#### Resolución condensada — Faceta 18

- **Costura (ES→genérico):** Los ratios 0.95 (delta_guard.py:54) y 0.50 (:59) son fracciones de completitud, genuinamente agnosticas de pais (el docstring :14-21 lo confirma). La costura es la COBERTURA: los tres conectores wholesale (:148-156) y los sin-sweep gatean solo por fetch_error is None, no por harvest-ratio; un pais #2 con conectores nuevos hereda el hueco.
- **Fix:** Cablear should_emit_gone en los tres conectores listados (group_subastas ~1005, localizavo ~801, subastacar ~813) en su call de reconcile usando declared_full / SELECT COUNT fresco; exigir que TODO sweep GONE nuevo lo llame (test de CI que lo asevera mecanicamente). previous_available debe ser SELECT COUNT fresco per-entidad, nunca cache stale (ya documentado :20-21, falta imponerlo).
- **Adversarial:** declared=0 por anomalia de gateway (200 valido + items vacios) se suprime SOLO si el caller pasa previous_available>0 (:97); un conector que pase None en esa rama sortea la supresion y autoriza el wipe. previous_available stale derrota el fallback. Conectores no-adoptados (DE/FR/IT/PT nuevos) barren GONE ante un timeout silencioso sin ratio-guard.
- **Sellado multi-vía:** (1) should_emit_gone(0,0,20) -> (False,...) (no wipe). (2) Prueba por-propiedades: ninguna combinacion devuelve True cuando harvested < min(declared*0.95, previous*0.50) con inventario. (3) Auditoria de adopcion: test de CI enumera conectores con sweep y asevera que cada uno llama should_emit_gone (cierra TODO :144-165, build ROJO si falta). (4) Contraejemplo de Hypothesis congelado como regression-fixture.
- **Herramienta NEXT-LEVEL:** Hypothesis (MPL-2.0) https://github.com/HypothesisWorks/hypothesis [VERIFIED NEXT-LEVEL.md:320] - genera el lattice (harvested, declared, previous_available) adversarialmente y PRUEBA el invariante de no-falso-wipe sobre todo el espacio, minimiza al contraejemplo y lo congela como golden. Complemento: Pydantic (MIT, NEXT-LEVEL:587) como contrato tipado del input de harvest-stats.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-19"></a>

### Faceta 19 — VIN como strong-key (identidad fuerte + decode)

> **B#5 HIGH — CIERRA MX/UE / OPEN JP** (chasis JDM ≠ VIN-17).

#### (a) Verificacion de code_hints [VERIFIED]
- `_can_merge_new_cars(va,vb)` [VERIFIED pipeline/identity/cluster_vehicles.py:277-286]: True solo si ambos `vin_ref` no-null y `str(vin_a).strip().upper() == str(vin_b).strip().upper()` [:282-286]; **la unica via de merge permitida para stock nuevo** (docstring :280). Aplicado en Signal A [:365-366] y Signal B [:415-416], gateado por `_is_new_car` = `km is None or km == 0` [:267-274].
- `_VIN_SQL = "length(v.vin_ref)=17 AND v.vin_ref ~ '^[a-hj-npr-zA-HJ-NPR-Z0-9]{17}$'"` [VERIFIED scripts/cross_platform_dedup_watermark.py:59] — 17 chars sobre el charset WMI (sin I/O/Q); tokens nativos de plataforma (8/9/12 char) excluidos por comentario [:57-58].
- `_vin_exact_resolver(conn, *, apply)` [VERIFIED :83-151]: agrupa por `upper(v.vin_ref)` HAVING `count(DISTINCT v.vehicle_ulid) >= 2` [:95-102]; survivor = oldest `first_seen` re-resuelto deterministicamente [:108-113]; captura before-state para backup [:117-127]; repunta `platform_listing` (PK (vehicle_ulid, platform_entity_ulid): borra arista dup si el survivor ya tiene esa plataforma, si no UPDATE) [:134-145] + `vehicle_event` straight repoint [:146-148]; DELETE de las filas folded **al final** [:149]. Reversible (JSON `.backups/`) + idempotente (re-run = 0 folds; el trigger `>=2 DISTINCT vehicle_ulid` + `array_agg(DISTINCT)` garantiza que el survivor nunca aparece en su propia fold-list) [:90-93].
- Doctrina cabecera: "VIN exact, OR (pHash Hamming <= 6 AND make,model,year,km-band all equal)" [:14]. Cierres DB vivos: photo_hash en **0** vehiculos, VINs de 17 char en **17,730** vehiculos, solo **18** filas comparten VIN cross-platform [VERIFIED :20-31] -> la unica via lawful hoy es VIN-exact (inmaterial, 18 filas).
- next_level idea #4 -> herramienta **vininfo** (NEXT-LEVEL.md:498). NOTA: la tabla ensamblada lista vininfo con esfuerzo "S" [VERIFIED NEXT-LEVEL.md:60], no "M" como dice el hint — la identidad de la herramienta (vininfo) es inequivoca; deriva de drift de etiqueta de esfuerzo.

#### (b) Mecanismo al atomo
VIN-exact es el **unico auto-merge cero-falsos** disponible hoy; el fuzzy-floor se MIDE, no se funde (facet 20). El resolver colapsa cada grupo VIN de >=2 filas de vehiculo distintas al survivor (oldest `first_seen`), repunta las **unicas dos** FKs a `vehicle.vehicle_ulid` (platform_listing, vehicle_event) ANTES de borrar las filas folded (orden de seguridad), y escribe un JSON before-state completo para reversibilidad. La idempotencia es **estructural**: el trigger es distinct-vehicle-count>=2 y `array_agg(DISTINCT)` garantiza que el survivor jamas esta en su propia fold-list (la trampa de perdida de dato). Para km=0/stock nuevo, VIN es ADEMAS la unica fuga del guard de no-merge (facet 25): coches nuevos comparten fotos de catalogo + atributos identicos entre dealers, asi que solo un VIN compartido puede fundir dos coches nuevos.

#### (c) Costura ES -> generico + fix
El test `length=17` + charset [:59] codifica la forma VIN ISO-3779 / norteamericana+UE. La costura: `length=17` **excluye duro** los mercados que no usan VIN de 17 char. El numero de chasis domestico JDM de Japon NO es VIN-17 -> `_VIN_SQL` no matchea nada -> con photo_hash al 0%, **JP no tiene NINGUN brazo de auto-merge lawful** (brazo vacio silencioso). Ademas no hay validacion (un string-junk de 17 char string-iguala a otro junk y podria falso-fundir) ni cross-check de marca.
**Fix:** adoptar decode WMI/VDS + validacion del digito de control ISO-3779 para que (i) los VIN parse-junk se rechacen por digito de control, (ii) el fabricante decodificado se cross-checkee contra el make normalizado para cazar corrupcion OCR/scrape, (iii) la aplicabilidad VIN se **gatee por pais**: el decode triunfa en mercados VIN-17 (UE/MX NOM-001 de 17 encaja), el chasis JDM falla el test 17/charset y se **enruta a pHash** (facet 12) en vez de producir un brazo vacio en silencio.

#### (d) Riesgo adversarial concreto
- **Japon:** chasis JDM (no VIN-17) -> excluido -> JP sin auto-merge lawful con photo_hash 0% (HIGH).
- **Mexico:** NOM-001 de 17 char encaja, OK.
- Captura de VIN baja en todas partes (17,730 capturados, solo 18 cross-platform) -> VIN-exact inmaterial hasta que suba la captura; la fuga km=0 (facet 25) casi nunca dispara en mercados de VIN bajo -> el over-count de stock nuevo persiste.
- Sin validacion, un "VIN" junk corrupto/duplicado podria sembrar un falso-merge; el decode/digito-de-control es el guard.
- **Ruido:** tokens nativos de listado de 17 char que no son VIN podrian colarse en el regex de charset en algun locale.

#### (e) Criterio de sellado + verificacion multi-via
- **Golden de digito de control:** VINs known-good y known-bad (set de referencia ISO-3779) prueban que la validacion acepta/rechaza correctamente.
- **Cross-check WMI->make:** el fabricante decodificado debe concordar con el make normalizado; las discrepancias se marcan como parse-junk, nunca se funden.
- **Asercion de gating por pais:** fixtures de chasis JDM clasificados no-VIN y excluidos del brazo VIN (aserto) -> Japon degrada a pHash/+-dup_ci honestamente, no en silencio.
- **Reversibilidad/idempotencia:** el JSON backup round-trip (restaurar devuelve el estado pre-merge); un re-run encuentra 0 folds (idempotente) — ya garantizado estructuralmente [:90-93], se extiende con test.

#### (f) Herramienta NEXT-LEVEL
**vininfo** (BSD-3-Clause, https://github.com/idlesign/vininfo) [VERIFIED NEXT-LEVEL.md:498] — decodificador WMI/VDS embebido, sin red, + validacion del digito de control ISO-3779. Convierte el naive string-match de 17 char en un **strong-key auto-validante**: rechaza parse-junk gratis, cross-checkea fabricante decodificado vs make del listado, y gatea limpiamente la aplicabilidad VIN por pais (decode OK para UE/MX, JDM falla -> enrutado a pHash, cerrando el brazo-vacio-silencioso "B5"). Mas VINs capturados se vuelven auto-merges lawful mas alla de las 18 filas de hoy. Cross-check ortogonal opcional: flat-file NHTSA vPIC (gov US, gratis) [VERIFIED NEXT-LEVEL.md:499]. EUR0, pure-Python, datos embebidos, decode inline en tiempo de extract/identity.

#### Resolución condensada — Faceta 19

- **Costura (ES→genérico):** _VIN_SQL test length=17 + charset WMI [watermark:59] codifica la forma VIN ISO-3779/NA+UE y EXCLUYE DURO los mercados sin VIN-17. El chasis JDM de Japon no es VIN-17 -> no matchea -> con photo_hash 0%, JP sin ningun brazo de auto-merge lawful (brazo vacio silencioso). Ademas no hay validacion (string-junk de 17 podria falso-fundir) ni cross-check decode->make. _can_merge_new_cars [:277-286] hace string-compare crudo de vin_ref upper/strip, sin decode.
- **Fix:** Adoptar decode WMI/VDS + validacion del digito de control ISO-3779: (i) rechazar VIN parse-junk por digito de control; (ii) cross-checkear fabricante decodificado vs make normalizado (caza corrupcion OCR/scrape); (iii) gatear aplicabilidad VIN por pais: decode OK en VIN-17 (UE/MX NOM-001 encaja), chasis JDM falla el test 17/charset y se ENRUTA a pHash (facet 12) en vez de producir brazo vacio en silencio. Mantener el orden de seguridad existente (repuntar platform_listing+vehicle_event antes de DELETE) y el backup JSON reversible.
- **Adversarial:** Japon: chasis JDM (no VIN-17) excluido -> JP sin auto-merge lawful con photo_hash 0% (HIGH). Mexico: NOM-001 de 17 encaja OK. Captura VIN baja global (17,730 capturados, 18 cross-platform) -> VIN-exact inmaterial; la fuga km=0 (facet 25) casi nunca dispara en mercados VIN-bajo -> over-count de stock nuevo persiste. Sin validacion un VIN junk podria sembrar falso-merge. Ruido: tokens de listado de 17 char no-VIN podrian colarse en el charset en algun locale.
- **Sellado multi-vía:** Golden de digito de control: VINs known-good/known-bad (ref ISO-3779) prueban accept/reject. Cross-check WMI->make: fabricante decodificado debe concordar con make normalizado; discrepancia => parse-junk, nunca fundir. Asercion de gating por pais: fixtures de chasis JDM clasificados no-VIN y excluidos del brazo VIN -> JP degrada a pHash/+-dup_ci honestamente. Reversibilidad/idempotencia: backup JSON round-trip; re-run = 0 folds (ya estructural [:90-93], extender con test).
- **Herramienta NEXT-LEVEL:** vininfo (BSD-3-Clause, https://github.com/idlesign/vininfo) [VERIFIED NEXT-LEVEL.md:498]: decode WMI/VDS embebido sin red + validacion digito de control ISO-3779. Convierte el string-match naive de 17 char en strong-key auto-validante: rechaza parse-junk, cross-checkea fabricante vs make, gatea VIN por pais (UE/MX OK; JDM falla -> enrutado a pHash, cierra el brazo-vacio 'B5'); mas VINs capturados se vuelven auto-merges lawful mas alla de las 18 filas. Cross-check ortogonal: NHTSA vPIC flat-file (gov US, gratis) [VERIFIED NEXT-LEVEL.md:499]. NOTA: tabla ensamblada marca esfuerzo 'S' [NEXT-LEVEL.md:60] (hint decia M). EUR0, pure-Python, datos embebidos.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-20"></a>

### Faceta 20 — Watermark de over-count + ledger ±dup_ci

> **B#6 HIGH — CIERRA (FIX-A).** Sirve cada contador con su cota ±dup_ci.

#### (a) Verificacion de code_hints [VERIFIED]
- Doctrina strong-key: over-merge prohibido y "strictly below under-merge"; auto-collapse SOLO en strong key = "VIN exact, OR (pHash Hamming <= 6 AND make,model,year,km-band all equal)"; todo lo mas debil -> fila distinta servida CON su cota medida `+/-dup_ci` [VERIFIED scripts/cross_platform_dedup_watermark.py:11-18].
- Hechos vivos: "photo_hash populated on 0 vehicles" -> el brazo pHash del strong-key no puede correr; "real 17-char VINs on 17,730 vehicles -> only 18 rows share a VIN across platforms"; el material vive en el fuzzy floor ~131.8K (SQL GROUP BY 131,773 ~= Python grouping 131,895, agree within 0.09%) [VERIFIED :20-31].
- `_VIN_SQL = length(v.vin_ref)=17 AND ... '^[a-hj-npr-zA-HJ-NPR-Z0-9]{17}$'` (charset WMI ISO-3779, sin I/O/Q) [VERIFIED :59].
- `_FUZZY_FLOOR_BASE`: clave `(mk, md, yr, km, price, prov)` con `e.province_code AS prov` (:68), `v.km > 0` (:74), `v.price > 0` (:75); **SIN country_code** [VERIFIED :65-76].
- `_measure_bound`: PATH 1 SQL GROUP BY (:157-164), PATH 2 stream + grouping Python independiente (:165-173), `divergence_pct` (:184) [VERIFIED :154-185].
- Ledger: `record_count_verdict(... subject_key="ES_national" ... paths={"excess_sql_groupby":..., "excess_python_grouping":...}, tolerance=0.01)` [VERIFIED :209-218, subject :212]. La regla de quorum del verdict es ">=2 orthogonal paths agree" [VERIFIED pipeline/verify.py:53-68].
- VIN-exact resolver reversible (JSON backup :121-127) + idempotente (`count(DISTINCT v.vehicle_ulid) >= 2`, array_agg DISTINCT :90-93, :102) + safety-order (repunta platform_listing + vehicle_event antes de borrar :131-149); dry-run hace rollback de la fila ledger tambien (:236-240) [VERIFIED].

#### (b) Mecanismo al atomo
1. El esquema materializa 2 filas para un coche en 2 plataformas (UNIQUE(entity_ulid,deep_link), faceta 1) -> over-count estructural. El watermark NO lo fusiona a ciegas: lo MIDE y sirve cada contador con su cota.
2. **Unico merge lawful hoy**: VIN-exact. Colapsa cada grupo VIN de >=2 filas DISTINTAS a un superviviente (oldest first_seen), repuntando aristas+eventos, reversible+idempotente. Es inmaterial (18 filas) pero se aplica por ser el colapso cero-falso.
3. **La cota medida**: el `_FUZZY_FLOOR_BASE` (exact make+model+year+km+price+province) es la cota INFERIOR conservadora de duplicacion cross-plataforma. Se mide por DOS vias ortogonales: SQL GROUP BY y grouping Python sobre el mismo input. Coinciden al 0.09% -> la cota es de confianza.
4. **El ledger**: `record_count_verdict` exige quorum (>=2 vias coinciden dentro de tolerance=0.01) y persiste el veredicto como `+/-dup_ci`. La API sirve cada contador nacional/plataforma CON esa cota: "un contador inflado por una cantidad no-medida esta prohibido; o se dedupe o se sirve con su cota".
5. **Doctrina**: over-merge < under-merge. Con photo_hash 0%, la unica via lawful es VIN (18 filas), asi que el grueso del 131.8K se sirve como cota ancha, no se colapsa.

#### (c) Costura ES->generico
El agrupado `_FUZZY_FLOOR_BASE` (:65-76) es **country-BLIND**: agrupa por `province_code` DESNUDO (:68), sin country_code. En BD mono-pais es correcto. En multi-pais, el codigo de provincia '28' colisiona (ES Madrid '28' vs un Kreis/codigo DE '28' — migration 0053_country_onboarding.sql DOCUMENTA esta colision exacta). Dos coches fisicamente distintos (ES-28 y DE-28, mismo make/model/year/km/price, AMBOS EUR) caen en el MISMO grupo -> el watermark los CUENTA como par duplicado cross-plataforma -> infla `+/-dup_ci` con fantasmas transfronterizos. Ademas `subject_key='ES_national'` (:212) etiqueta MAL todo veredicto corrido sobre una BD multipais.

#### (d) Riesgo adversarial concreto
- **DE**: provincia '28' (Kreis o derivado de 2 digitos) colisiona con ES Madrid '28' (migration 0053 lo prueba) -> ES-28 y DE-28 con make/model/year/km/price identicos agrupan como "duplicado cross-plataforma" -> cota inflada por un fantasma que cruza frontera.
- **FR/IT/PT (todos EUR)**: la igualdad de moneda hace que el `price` de la clave se satisfaga cross-frontera -> el fantasma NI siquiera lo bloquea un mismatch de moneda (faceta 9). CRITICAL.
- **No-EUR (UK/JP)**: la igualdad de precio casi nunca se cumple entre monedas -> la tasa de fantasma BAJA, pero `subject_key='ES_national'` sigue mis-etiquetando cualquier medida sobre esa BD.
- **Ruido**: con photo_hash 0% (faceta 13), el watermark no puede escalar ningun fantasma a un merge lawful VIN/pHash -> todo el residual queda como cota (inflada). La medida es honesta sobre ser una cota, pero la cota esta wrong-by-country.

#### (e) Criterio de sellado + verificacion multi-via
- **2 vias existentes**: SQL GROUP BY (:157-164) vs Python grouping (:165-173) coinciden dentro de tolerance=0.01 (:218) — ya impuesto por el quorum de `record_count_verdict` (verify.py:65-68).
- **Sello country-proof**: tras el fix country_code, un fixture sintetico 2-pais (ES-28 + DE-28 atributos identicos) DEBE producir CERO cross-groups (el fantasma desaparece); la baseline ES-only debe reproducir `excess_sql` byte-identico (cero regresion).
- **Via 3 (motor ER independiente)**: ER-Evaluation (o pyJedAI) re-estima el CI de cardinalidad independientemente; el `+/-dup_ci` servido debe caer DENTRO del intervalo ER-Evaluation (tri-acuerdo: SQL, Python, ER-Evaluation).
- **Reversibilidad**: el merge VIN-exact es JSON-backed (:121-127) e idempotente (:90-93, :102); un `--dry-run` deja BD y fila-ledger rolled back (:236-240).

#### (f) Herramienta NEXT-LEVEL
**ER-Evaluation** — cardinalidad certificada con intervalos de confianza (el mandato `+/-dup_ci`, SOTA), AGPL-3.0, EUR0 [VERIFIED NEXT-LEVEL.md:522, URL https://github.com/OlivierBinette/er-evaluation]. Sustituye el GROUP-BY hand-rolled por estimadores ER con CIs basados en muestreo (bias-corrected cluster-size counts + bootstrap), grado-investigacion. **Caveat AGPL [VERIFIED :524]**: usar como CLI offline de analisis (sin servicio de red que lo exponga) para que el copyleft-de-red no alcance el producto, O portar la matematica del estimador a scipy/numpy (BSD) para una ruta servida totalmente permisiva. Segunda via ortogonal: **pyJedAI** (AI-team-UoA/pyJedAI), Apache-2.0 [VERIFIED :546, URL https://github.com/AI-team-UoA/pyJedAI] como motor ER arquitectonicamente INDEPENDIENTE para la certificacion 2-via del sello (tri-agreement deterministic/Splink/pyJedAI dentro del intervalo ER-Evaluation, :549).

#### Resolución condensada — Faceta 20

- **Costura (ES→genérico):** _FUZZY_FLOOR_BASE (cross_platform_dedup_watermark.py:65-76) es country-BLIND: agrupa por province_code desnudo (:68) sin country_code. En mono-pais correcto; en multi-pais el codigo '28' colisiona (ES Madrid vs DE Kreis '28', documentado en migration 0053_country_onboarding.sql). Ademas subject_key='ES_national' (:212) hardcodea la etiqueta del veredicto.
- **Fix:** (1) Anteponer country_code a la clave del fuzzy-floor (y al JOIN via entity.country_code) para que un grupo nunca cruce frontera. (2) Parametrizar subject_key por pais (f'{cc}_national') en vez del literal 'ES_national' (:212). (3) La doctrina (over-merge < under-merge, servir CON cota medida, :11-18) ya es pais-agnostica y se mantiene verbatim. Las 2 vias VAM (SQL vs Python) y el quorum del ledger no cambian.
- **Adversarial:** DE: provincia '28' colisiona con ES Madrid '28' (migration 0053 lo prueba) -> ES-28 y DE-28 con make/model/year/km/price identicos cuentan como duplicado cross-plataforma -> +/-dup_ci inflado por fantasma transfronterizo. FR/IT/PT (EUR): la igualdad de moneda satisface el price de la clave cross-frontera, ni la bloquea un mismatch FX (faceta 9) -> CRITICAL. No-EUR (UK/JP): tasa de fantasma baja, pero subject_key='ES_national' mis-etiqueta. Con photo_hash 0% no hay escape lawful VIN/pHash -> todo el residual queda como cota wrong-by-country.
- **Sellado multi-vía:** Las 2 vias existentes (SQL GROUP BY :157-164 vs Python grouping :165-173) coinciden dentro de tolerance=0.01 (:218), ya impuesto por el quorum '>=2 paths agree' de record_count_verdict (verify.py:65-68). Country-proof: fixture sintetico 2-pais (ES-28 + DE-28 identicos) debe dar CERO cross-groups y la baseline ES-only reproducir excess_sql byte-identico (cero regresion). Via 3: ER-Evaluation/pyJedAI re-estiman el CI independientemente; el +/-dup_ci servido cae dentro del intervalo (tri-acuerdo). Reversibilidad: merge VIN JSON-backed (:121-127) + idempotente (:90-93,:102), dry-run rolled back (:236-240).
- **Herramienta NEXT-LEVEL:** ER-Evaluation — cardinalidad certificada con intervalos de confianza (el mandato +/-dup_ci, SOTA). AGPL-3.0 [VERIFIED NEXT-LEVEL.md:522]. URL: https://github.com/OlivierBinette/er-evaluation. Caveat AGPL [VERIFIED :524]: usar como CLI offline o portar el estimador a scipy/numpy (BSD) para la ruta servida. Segunda via ortogonal: pyJedAI (AI-team-UoA/pyJedAI) Apache-2.0 [VERIFIED :546] como motor ER independiente para la certificacion 2-via del sello.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-21"></a>

### Faceta 21 — `make_normalizer`: taxonomía canónica de marca

> **Costura = datos + tokenizer.** `_CANON` ES + `split()[0]`; OPEN JP (gramática lark).

#### (a) Code hints — VERIFIED
- `_CANON: dict[str,str]` [VERIFIED make_normalizer.py:19-40] — ~70 lowercased brand tokens -> canonical display form; acronym brands keep all-caps (BMW/SEAT/MG/DS/CUPRA/MINI/BYD/KGM/SWM/DFSK/EBRO), aliases included (vw->Volkswagen, citroen/citroën->Citroen, skoda/škoda->Skoda, alfa/alfa-romeo->Alfa Romeo, lynk&co->Lynk & Co). Grounded in the 2026-06-15 LIVE ES distribution (docstring :9-11), not invented.
- `canonical_make(value)` [VERIFIED :43-47]: `_CANON.get(value.strip().lower())` or None.
- `make_from_title(title)` [VERIFIED :50-54]: `_CANON.get(title.strip().split()[0].lower())` — leading whitespace token only.
- `normalize_make(make,title)` [VERIFIED :57-76]: canon(make) first (:68-70) -> else make_from_title (:71-73, recovers model-as-make) -> else verbatim if non-empty (:74-75) -> else None. NEVER guesses (Law I :65 "under-fill over mis-fill").
- model deliberately NOT parsed (:12-13).
- call-site [VERIFIED wallapop_wholesale.py:984]: `[normalize_make(x[3].make, x[3].title) for x in ins]` inside the `_BULK_INSERT_VEHICLES` column list (code_hint said :986; actual :984 — minor line drift, mechanism identical).

#### (b) Mechanism al atomo
A three-tier precision cascade feeding the `make` field of the firma block key (facet 7). Tier 1: if the raw make is a known brand (any casing) return its canonical display form — fixes casing fragmentation (VOLKSWAGEN / Volkswagen / volkswagen -> Volkswagen). Tier 2: if make is NOT a known brand but the title's leading token IS, return the title's brand — recovers BOTH a NULL make (~400k classifieds rows e.g. milanuncios) AND a model-as-make (make='Golf', title 'Volkswagen Golf' -> 'Volkswagen'). Tier 3: make non-empty, unknown, no title-brand -> keep VERBATIM (Law I: never invent). Tier 4: nothing -> None. High-precision by design: a value is normalized/recovered ONLY on a hit against the CLOSED `_CANON` set; an unknown brand survives untouched (no fuzzy guess). This keeps the firma block's `make` axis consistent without ever fabricating a brand.

#### (c) Costura ES->generico
Two ES-anchored atoms: (1) `_CANON` (:19-40) is the top-70 ES distribution — it omits importers/local spellings prominent elsewhere (PT/IT classifieds variants, JDM marques in JP). (2) `make_from_title` (:54) tokenizes by WHITESPACE `split()[0]` — assumes a Latin, space-delimited title with the brand leading. The function CONTRACT (closed-set match, verbatim fallback, never guess) is country-agnostic and CORRECT; the seam is purely the DATA (`_CANON` contents) and the tokenizer. Extension MUST be additive (add aliases, never remove/rewrite existing keys) to preserve ES byte-identity.

#### (d) Riesgo adversarial
- **JP/CJK**: title `トヨタプリウス` (Toyota Prius, no spaces) -> `split()[0]` returns the WHOLE string `トヨタプリウス` -> `_CANON.get('トヨタプリウス')` -> None -> make_from_title dead -> a NULL-make JP row stays NULL (under-fill). The leading-token heuristic structurally fails in scriptless-whitespace languages. HIGH — NEXT-LEVEL.md:279 names this exact line make_normalizer.py:54.
- **DE**: importers/sub-brands and local spellings absent from the ES top-70 -> kept verbatim (safe, but casing/alias variants are not collapsed, fragmenting the search axis).
- **PT/IT**: same — missing local aliases mean legit brands fall to verbatim, splitting the firma `make` axis (mild under-merge into facet 7's block key).
- **Noise**: a non-brand leading token ("Vendo","Ocasion","Caravana") correctly yields NO make (Tier 2 miss -> Tier 3/4), so junk does not seed a false brand — the closed-set design is noise-robust by construction.

#### (e) Sellado + verificacion multi-via
- (1) ES byte-identity golden: re-run normalize_make over the ES corpus -> identical `make` column (cdp/firma goldens + Ferrari suite stay green; the additive `_CANON` extension proven non-regressive).
- (2) Per-country golden: a DE/PT/IT/JP fixture of (raw make, title) -> expected canonical, pinned; a CJK title asserts BOTH the current failure mode (-> None) and the grammar-parser fix recovery.
- (3) Orthogonal: the grammar-extracted make (lark) cross-checked vs the make from a structured JSON-LD / next_data field when present — must agree; divergence escalates (not silently merged).
- (4) Property (Hypothesis): `normalize_make` output ∈ `_CANON.values() ∪ {verbatim input} ∪ {None}` for ALL inputs (never an invented brand) and is idempotent (`normalize_make(normalize_make(x)) == normalize_make(x)`).

#### (f) Herramienta NEXT-LEVEL
**lark** (EBNF grammar parser) — MIT — https://github.com/lark-parser/lark [VERIFIED NEXT-LEVEL.md:277-283]. Replaces `make_from_title`'s `title.split()[0]` (NEXT-LEVEL.md:279 cites make_normalizer.py:54 BY NAME) with a deterministic EBNF grammar (Earley/LALR) that segments make/model/trim/displacement/fuel/power from the title — pure-Python, zero-dep, EUR0, auditable, faster than any LLM, and maintainable per-country as PACK DATA (`countries/<CC>/title.lark`). Only on grammar failure does it escalate to a Capa-2 LLM. Fixes the CJK no-space tokenization (a romanized grammar parses `トヨタプリウス` where split()[0] returns the whole string) and extracts trim/cc/power the naive split loses. Pairs with **anyascii** (ISC, https://github.com/anyascii/anyascii, NEXT-LEVEL.md:479-485) ONLY if a transliteration step precedes the grammar; the grammar itself is the headline elevation. Verification rides **Hypothesis** (MPL-2.0, NEXT-LEVEL.md:317-323): assert "the grammar never emits a make outside brand_table and never crashes (falls to LLM-scale)".

#### Resolución condensada — Faceta 21

- **Costura (ES→genérico):** Two ES-anchored atoms: `_CANON` [make_normalizer.py:19-40] is the top-70 ES brand distribution (omits non-ES importers/local spellings/JDM marques), and `make_from_title` [:54] tokenizes by whitespace `split()[0]` (assumes a Latin space-delimited title with the brand leading). The function contract — closed-set match, verbatim fallback, never guess — is itself country-agnostic; only the DATA and the tokenizer are the seam.
- **Fix:** Extend `_CANON` additively per country (add aliases/local spellings, never remove or rewrite existing keys -> preserves ES byte-identity) and replace `make_from_title`'s whitespace `split()[0]` [make_normalizer.py:54] with a lark EBNF title parser (pack data `countries/<CC>/title.lark`) that segments make from a scriptless title; keep the three-tier cascade and the never-guess Law-I verbatim fallback intact.
- **Adversarial:** JP/CJK: `トヨタプリウス` (no spaces) -> split()[0] returns the whole string -> _CANON miss -> make_from_title dead -> NULL-make JP row stays NULL (HIGH; NEXT-LEVEL.md:279 names line :54). DE/PT/IT: local importer/sub-brand spellings absent from the ES top-70 fall to verbatim, fragmenting the firma `make` axis (mild under-merge in facet 7). Noise: non-brand leading tokens ('Vendo'/'Caravana') correctly yield no make; the closed-set design is noise-robust by construction.
- **Sellado multi-vía:** (1) ES byte-identity golden (additive _CANON proven non-regressive; Ferrari suite green). (2) Per-country (make,title)->expected goldens incl. a CJK fixture asserting both the current None failure and the grammar-fix recovery. (3) Orthogonal cross-check vs structured JSON-LD/next_data make when present; divergence escalates. (4) Hypothesis property: output ∈ _CANON.values() ∪ {verbatim} ∪ {None} (never invented) and idempotent.
- **Herramienta NEXT-LEVEL:** lark (MIT) https://github.com/lark-parser/lark [VERIFIED NEXT-LEVEL.md:280] — deterministic EBNF title->(make,model,trim,cc,fuel,power), pack-data grammar per country, replaces the CJK-fatal split()[0] at make_normalizer.py:54, escalates to LLM only on parse failure. Supporting: anyascii (ISC, https://github.com/anyascii/anyascii [VERIFIED NEXT-LEVEL.md:482]) for pre-grammar transliteration; Hypothesis (MPL-2.0 [VERIFIED NEXT-LEVEL.md:320]) for the adversarial 'never emits a make outside brand_table' property.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-22"></a>

### Faceta 22 — Anti-FP sealing checks (4 checks + cross-país)

> **B#2 CRITICAL — CIERRA (FIX-A).** Check 1 cuenta provincia, no país.

#### (a) code_hints verificados al atomo
- [VERIFIED pipeline/identity/cluster_vehicles.py:834-909] `_run_anti_fp_checks(conn)` -- los auto-checks "Director-mandated".
- **Check 1 cross-province** [:840-859]: `GROUP BY vc.canonical_vehicle_ulid HAVING COUNT(DISTINCT e.province_code) > 1` [:852], con `WHERE e.province_code IS NOT NULL` [:850] y `cluster_run_id = RUN_ID`; reporta `OK (0)` o `FAIL`.
- **Check 2 giant clusters** [:861-877]: `HAVING MAX(cluster_size) > 20` [:870]; emite **WARN** (no FAIL) si hay alguno [:876].
- **Check 3 exactly-once** [:879-892]: compara `total_vehicles` (`vehicle WHERE status='available'`) == `clustered` (`vehicle_cluster WHERE run`) == `distinct_clustered` [:890]; FAIL si difieren.
- **Check 4 singletons** [:894-907]: `cluster_size = 1 AND match_signal <> 'none'` [:900-901] -> `bad_singletons` debe ser 0.
- [VERIFIED :944] se invoca desde `main()` tras `_measure_and_validate` (:943). Nota mecanica: los checks **imprimen** (`print`), no lanzan -- son advisory; la Check 2 solo **WARN**.

#### (b) Mecanismo al atomo
Los 4 checks leen el overlay `vehicle_cluster` recien escrito y reportan pass/fail. La **Check 1 es la garantia estrella** "0 fusiones cross-province", pero cuenta `DISTINCT province_code`, **NO `country_code`** -> un cluster que abarca ES-28 y DE-28 (paises distintos, ambos provincia '28') tiene `COUNT(DISTINCT province_code) = 1` -> **PASA** -> certifica "0 cross-province" mientras **oculta una fusion cross-PAIS**. Los umbrales (Check 2 `>20`, y aguas arriba `K=12`, `PRICE_MAX`, centinela KM, `PRICE_TOL=2%`, `PHASH`) son **ES-calibrados** y los checks pueden ir en VERDE aunque esas constantes esten equivocadas para el pais nuevo.

#### (c) Costura ES -> generico (fix exacto)
1. **Check 1 -> cross-(country, geo_unit)**: `HAVING COUNT(DISTINCT (e.country_code, e.province_code)) > 1` en :852.
2. **Nueva Check 1b (hard FAIL)**: "0 clusters con `COUNT(DISTINCT e.country_code) > 1`" -- el invariante "0 fusiones cross-PAIS" que **hoy no existe** (sealing_hole declarado). Debe ser FAIL, no WARN.
3. **Check 2 a FAIL o gate per-pais**: promover el WARN >20 a bloqueante o parametrizar el cap por pais.
4. **Re-validar constantes por pais**: `K/PRICE_MAX/centinela-KM/PRICE_TOL/PHASH` antes de confiar en el VERDE.
5. **Fail-closed**: que los checks **lancen** (raise) en vez de `print`, para que un rojo bloquee `vam_verified`.

#### (d) Riesgo adversarial concreto
- La garantia estrella **"0 fusiones cross-province" NO aguanta entre fronteras**: cuenta provincia, no pais -> fusiones cross-border DE/FR/IT/PT/MX/JP **pasan como limpias**. La faceta 8 produce la fusion; esta faceta la **certifica como buena**.
- Los 4 checks pueden ir **VERDE con umbrales ES equivocados** -> colapso silencioso de calidad con **sello limpio**. Es el peor desenlace adversarial: **el sello MIENTE** (un contador certificado-pero-falso).
- Ruido: un cluster gigante real (Check 2) solo da WARN -> pasa el sello aunque sea una cadena patologica.

#### (e) Sellado + verificacion multi-via
- **Via 1 (golden adversarial)**: un cluster sintetico cross-pais (ES-28 + DE-28) debe **FALLAR Check 1b** (hoy pasa Check 1).
- **Via 2 (ER independiente)**: un motor ER **arquitectonicamente independiente** (pyJedAI) re-resuelve la misma entrada y debe coincidir con el set canonico dentro de un **intervalo certificado** (ER-Evaluation); divergencia mas alla del intervalo **bloquea** el sello.
- **Via 3 (re-pin por pais)**: los caps/anchos se re-fijan desde el seal manifest ISO 3166-2 (pycountry) por pais.
- **Via 4 (fail-closed)**: los checks lanzan; un rojo bloquea `vam_verified` (no solo imprime).

#### (f) Herramienta NEXT-LEVEL
**pyJedAI** (independent 2nd ER path para certificacion de sello 2-via) — Apache-2.0, €0 — https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:546, entry :543-549]. Levanta un motor ER **independiente** para certificar adversarialmente el clustering casero: el sello exige que la red determinista + Splink + pyJedAI **concuerden** dentro del intervalo certificado, convirtiendo "creemos que los checks pasan" en "tres motores independientes concuerdan por pais". Complementos: **ER-Evaluation** (cardinalidad certificada con CIs = el intervalo ±dup_ci dentro del cual deben concordar) — AGPL-3.0 — https://github.com/OlivierBinette/er-evaluation [VERIFIED :522] (usar offline para evitar el copyleft de red); **pycountry** (seal manifest ISO 3166-2 para re-pinear caps/anchos por pais) — LGPL-2.1 — https://github.com/pycountry/pycountry [VERIFIED :530]; **Great Expectations** (convertir los 4 print-checks en contratos versionados fail-closed) — Apache-2.0 — https://github.com/great-expectations/great_expectations [VERIFIED :167].

#### Resolución condensada — Faceta 22

- **Costura (ES→genérico):** Check 1 (cluster_vehicles.py:852) cuenta HAVING COUNT(DISTINCT e.province_code) > 1 -- country-BLIND. NO existe invariante '0 fusiones cross-PAIS' (DISTINCT country_code) -- sealing_hole declarado. Los umbrales (Check 2 >20 :870, y aguas arriba K=12/PRICE_MAX/centinela-KM/PRICE_TOL/PHASH) son ES-calibrados y los checks pasan VERDE aunque esten equivocados para el pais nuevo. Los checks imprimen (print), no lanzan; Check 2 solo WARN.
- **Fix:** 1) Check 1 -> HAVING COUNT(DISTINCT (e.country_code, e.province_code)) > 1 en :852. 2) Nueva Check 1b hard-FAIL: '0 clusters con COUNT(DISTINCT e.country_code) > 1'. 3) Check 2 (>20) de WARN a FAIL o cap per-pais. 4) Re-validar K/PRICE_MAX/centinela-KM/PRICE_TOL/PHASH por pais antes de confiar en el VERDE. 5) Fail-closed: los checks lanzan (raise) en vez de print, para que un rojo bloquee vam_verified.
- **Adversarial:** La garantia estrella '0 fusiones cross-province' NO aguanta entre fronteras (cuenta provincia, no pais) -> fusiones DE/FR/IT/PT/MX/JP pasan como limpias; la faceta 8 fusiona y esta faceta lo certifica como bueno. Los 4 checks pueden ir VERDE con umbrales ES equivocados -> colapso silencioso de calidad con sello limpio: el sello MIENTE (contador certificado-pero-falso). Un cluster gigante real solo da WARN -> pasa el sello.
- **Sellado multi-vía:** Via 1: golden adversarial -- cluster sintetico ES-28 + DE-28 debe FALLAR Check 1b (hoy pasa Check 1). Via 2: ER independiente (pyJedAI) re-resuelve la misma entrada y debe concordar con el set canonico dentro del intervalo certificado (ER-Evaluation); divergencia bloquea el sello. Via 3: caps/anchos re-pineados desde el seal manifest ISO 3166-2 (pycountry) por pais. Via 4: fail-closed -- los checks lanzan; un rojo bloquea vam_verified.
- **Herramienta NEXT-LEVEL:** pyJedAI (independent 2nd ER path, certificacion 2-via) — Apache-2.0 — https://github.com/AI-team-UoA/pyJedAI [VERIFIED NEXT-LEVEL.md:546, entry 543-549]. Motor ER independiente que certifica adversarialmente el clustering casero: el sello exige determinista + Splink + pyJedAI concordando dentro del intervalo certificado. Complementos: ER-Evaluation (±dup_ci con CIs) — AGPL-3.0 — https://github.com/OlivierBinette/er-evaluation [VERIFIED :522] (offline por copyleft de red); pycountry (seal manifest ISO 3166-2, re-pin caps por pais) — LGPL-2.1 [VERIFIED :530]; Great Expectations (4 checks como contratos fail-closed versionados) — Apache-2.0 — https://github.com/great-expectations/great_expectations [VERIFIED :167].

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-23"></a>

### Faceta 23 — Medición & muestra VAM (20-pares + province sample)

> **Muestra 28/08 ES hardcode — CIERRA** (parametrizar por país; pack #8).

#### (a) Verificacion de code_hints [VERIFIED]
- `pipeline/identity/cluster_vehicles.py:660-826` — `_measure_and_validate(conn)`: "Measure unique physical cars + 20-pair sample for Director validation" (:661). [VERIFIED]
- **Run stats** `:666-683`: lee `vehicle_cluster_run` (n_in, n_clusters, n_merged) y calcula `% colapso`. [VERIFIED]
- **Breakdown por senal** `:685-706`: GROUP BY `match_signal` (clusters multi-listing). [VERIFIED]
- **Breakdown por plataforma** `:708-731`: `regexp_replace(v.deep_link,'^https?://([^/]+).*','\1') AS host` (:712), GROUP BY host LIMIT 15. [VERIFIED]
- **Province sample HARDCODE** `:733-755`: `for prov, pname in [("28","Madrid"), ("08","Barcelona")]` (:734) -> total/unique/merged por provincia ES. [VERIFIED]
- **20-pair VAM** `:757-824`: CTE `merged` sobre `cluster_size = 2` y `match_signal IN ('photo_url','firma','both')` (:782-783), `ROW_NUMBER() OVER (PARTITION BY canonical ORDER BY first_seen, vehicle_ulid)` (:775-778), self-join rn=1 vs rn=2, `LIMIT 20` (:797); imprime A/B con make/model/year/km/price/title/photo. [VERIFIED]
- **Host regexp Python** `:805-809`: `_host(dl)` con `re.search(r"https?://([^/]+)", dl)`. [VERIFIED]

#### (b) El mecanismo al atomo
`_measure_and_validate` es la **superficie de evidencia para el gate humano** (el VAM del Director que decide `vam_verified` en la faceta 4). NO sella; PREPARA la decision. Emite cinco artefactos: (1) stats del run (cuanto colapso), (2) desglose por senal (cuanto aporto photo_url vs firma vs both), (3) desglose por host (que plataformas se fusionaron), (4) muestra por provincia (foto de densidad local), (5) **la muestra de 20 pares**: 20 clusters de tamano 2 con sus dos listings lado a lado (A y B), de modo que el Director pueda juzgar a ojo si cada par es el MISMO coche fisico. El `ROW_NUMBER` garantiza un orden determinista (first_seen, ulid) para A/B; el filtro `cluster_size=2` toma los pares limpios; `match_signal IN (...)` cubre las tres rutas de merge. La extraccion de host por regexp (SQL :712 y Python :805-809) ya es generica.

#### (c) La costura ES->generico
Dos elementos estan **moldeados a ES** y romperian un sello DE/FR/no-UE:
1. **`province sample` hardcode `[("28","Madrid"),("08","Barcelona")]` (:734)**: son codigos INE de provincias espanolas. Un sello DE pondria al Director revisando densidad de provincias ESPANOLAS -> certifica el pais nuevo a ciegas.
   - **Fix**: computar la muestra de provincias como **top-2 por inventario del pais que se sella** (`SELECT province_code ... WHERE country_code=$cc GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 2`), no literal.
2. **El `subject`/etiqueta del verdict es nacional-ES** (acopla con faceta 20 `subject_key='ES_national'`): la muestra debe etiquetarse con el pais que se mide.
   - **Fix**: parametrizar el subject por `country_code`.
Lo que NO es costura: la extraccion de host por regexp (`:712`, `:805-809`) es URL-generica; el `cluster_size=2` y el `ROW_NUMBER` son agnosticos; las stats del run son agnosticas.

#### (d) Riesgo adversarial concreto
- **DE/FR/IT/PT**: el Director recibe una muestra de 20 pares del pais nuevo (eso SI escala — el SQL no fija pais en el 20-pair), PERO la "province sample" sigue mostrando Madrid/Barcelona (28/08 no existen como esos nombres en DE) -> la foto de densidad local es ESPANOLA aunque se este sellando DE. El gate humano cree ver el pais nuevo y ve ES.
- **No-UE / ruido**: una muestra de 20 pares NO es estadisticamente representativa de un pais de millones de coches; el Director gateaba `vam_verified` sobre 20 ejemplos elegidos por LIMIT (no aleatorios, no estratificados) -> sesgo de muestreo. El sello descansa en una inspeccion ocular de 20 pares ad-hoc.
- **Representatividad**: sin estratificar por (provincia x senal x plataforma), 20 pares pueden ser todos del mismo cluster facil y ocultar el modo de fallo real.

#### (e) Criterio de sellado + verificacion multi-via
**Sellado** = el Director gatea sobre una muestra REPRESENTATIVA del pais correcto, con una medida de la incertidumbre del conteo, no un eyeball de 20 pares ES.
- **Via 1 (parametrizacion)**: las provincias de muestra se computan top-2 por inventario del pais sellado; cero literal 28/08; el subject lleva `country_code`.
- **Via 2 (representatividad)**: la muestra de pares se estratifica por (senal x plataforma x provincia) y se aleatoriza (no `LIMIT` ciego); test de que cubre las 3 senales y >=N plataformas.
- **Via 3 (medida con IC)**: ademas del eyeball, emitir un conteo de cardinalidad con intervalo de confianza derivado de la muestra etiquetada -> el `+/-dup_ci` (faceta 20) deja de ser eyeball y pasa a estimacion certificada.
- **Via 4 (adversarial)**: ejecutar `_measure_and_validate` sobre un fixture DE y confirmar que la province sample muestra provincias DE (no 28/08) y el subject dice el pais correcto.

#### (f) Herramienta NEXT-LEVEL que lo eleva
**ER-Evaluation** (cardinalidad certificada con intervalos de confianza) — AGPL-3.0, EUR0=True — https://github.com/OlivierBinette/er-evaluation [VERIFIED NEXT-LEVEL.md:522]. Convierte el conteo "unique_cars" + el eyeball de 20 pares en una **estimacion de cardinalidad con IC bootstrap, grade-research** — el mandato `+/-dup_ci`, SOTA [VERIFIED NEXT-LEVEL.md:519-525]. **Caveat AGPL [VERIFIED NEXT-LEVEL.md:524]**: usar ER-Evaluation como CLI offline de analisis/reporte (sin servicio de red que lo exponga) para que el copyleft-de-red AGPL no alcance el producto; o portar la matematica del estimador (cluster-size bias-corrected counts + bootstrap CIs) sobre scipy/numpy (BSD, ya dependencias) para la ruta servida. La muestra etiquetada sale gratis del labeler. Complementos verificados: **Argilla** (Apache-2.0, https://github.com/argilla-io/argilla [VERIFIED NEXT-LEVEL.md:635]) como lazo de active-learning donde los veredictos VAM del Director engordan un golden-set versionado con gobernanza (profesor->alumno), cerrando que hoy NO hay donde acumular las etiquetas [VERIFIED NEXT-LEVEL.md:634]; **Snorkel** (Apache-2.0, https://github.com/snorkel-team/snorkel [VERIFIED NEXT-LEVEL.md:514]) para FABRICAR el set etiquetado mismo/distinto-coche por weak-supervision a escala censal sin anotacion manual.

#### Resolución condensada — Faceta 23

- **Costura (ES→genérico):** Dos elementos moldeados a ES: (1) province sample HARDCODE [('28','Madrid'),('08','Barcelona')] en cluster_vehicles.py:734 (codigos INE espanoles); un sello DE pondria al Director revisando densidad de provincias ESPANOLAS. (2) El subject/etiqueta del verdict es nacional-ES (acopla faceta 20 subject_key='ES_national'). NO es costura: la extraccion de host por regexp (:712, :805-809) es URL-generica; cluster_size=2 y ROW_NUMBER son agnosticos; las run stats son agnosticas.
- **Fix:** 1) Computar la province sample como top-2 por inventario del pais sellado (SELECT province_code WHERE country_code=$cc GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 2), no literal 28/08. 2) Parametrizar el subject del verdict por country_code. 3) Estratificar y aleatorizar la muestra de 20 pares por (senal x plataforma x provincia) en vez de LIMIT 20 ciego. 4) Emitir un conteo de cardinalidad con IC junto al eyeball.
- **Adversarial:** DE/FR/IT/PT: el 20-pair SI escala (el SQL no fija pais), pero la province sample sigue mostrando Madrid/Barcelona (28/08) -> el gate humano cree ver el pais nuevo y ve ES, certifica a ciegas. No-UE/ruido: 20 pares elegidos por LIMIT (no aleatorios, no estratificados) NO son representativos de millones de coches -> sesgo de muestreo; el sello descansa en una inspeccion ocular ad-hoc. Sin estratificar, los 20 pares pueden ser todos del cluster facil y ocultar el modo de fallo real.
- **Sellado multi-vía:** Sellado = el Director gatea sobre muestra REPRESENTATIVA del pais correcto + medida de incertidumbre del conteo, no eyeball de 20 pares ES. Multi-via: (1) provincias top-2 computadas por inventario del pais, subject con country_code, cero literal 28/08; (2) muestra estratificada por (senal x plataforma x provincia) y aleatorizada, cubre las 3 senales y >=N plataformas; (3) cardinalidad con IC bootstrap (el +/-dup_ci deja de ser eyeball); (4) adversarial: fixture DE muestra provincias DE y subject correcto.
- **Herramienta NEXT-LEVEL:** ER-Evaluation (cardinalidad certificada con IC) — AGPL-3.0, EUR0=True — https://github.com/OlivierBinette/er-evaluation [VERIFIED NEXT-LEVEL.md:522]. Convierte unique_cars + eyeball de 20 pares en estimacion de cardinalidad con IC bootstrap SOTA (el mandato +/-dup_ci). Caveat AGPL [VERIFIED NEXT-LEVEL.md:524]: usar como CLI offline (sin servicio de red) o portar la matematica (bias-corrected counts + bootstrap CIs) sobre scipy/numpy BSD para la ruta servida. Complementos: Argilla (Apache-2.0, NEXT-LEVEL.md:635) = lazo active-learning donde los veredictos VAM engordan un golden versionado; Snorkel (Apache-2.0, NEXT-LEVEL.md:514) = fabrica el set etiquetado mismo/distinto-coche sin anotacion manual.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-24"></a>

### Faceta 24 — Geo-grain: ancho y granularidad de la unidad geo

> **B#7 MEDIUM — CIERRA (FIX-G). GATE ESQUEMA** si se ensancha `CHAR(2)`.

#### (a) code_hints VERIFICADOS
- `migrations/0052_country.sql` [VERIFIED]: `geo_province / geo_comarca / geo_municipality / entity` reciben `country_code CHAR(2) NOT NULL DEFAULT 'ES'` :51-54; **UNIQUE compuesta** `(country_code, code)` en province :63-66 y municipality :70-77; comentario :23 "'ES' is exactly 2 chars, so CHAR(2) carries no blank-padding ambiguity"; `geo_municipality.code` es **CHAR(5)** :12; deferidos a onboarding: PK swap (a) :28-30, CHECKs ES `left(code,2)=province_code` (c) :32-35.
- `migrations/0053_country_onboarding.sql` [VERIFIED]: prueba la **colision de PK** - `INSERT geo_province(code='28',...,country_code='DE')` falla en `geo_province_pkey(code)` :3-4; **swap a PK compuesta** `(country_code, code)` :64-87; 6 FKs reescritas a compuestas `(country_code,<col>)->(country_code,code)` :93-157; **CHECKs ES-shaped relajados por pais** :159-174 - `municipality_province_prefix CHECK (country_code<>'ES' OR left(code,2)=province_code)` :166-168 y `chk_entity_muni_province` :170-174; comentario :28-33 "INE <prov2><muni3> coding"; `entity.province_code CHAR(2)`.

#### (b) Mecanismo al atomo
El grano geo cumple **dos** roles acoplados. (1) **Ancho fisico:** `geo_province.code`/`entity.province_code` son `CHAR(2)`, `geo_municipality.code` `CHAR(5)` - moldeados por INE (provincia 2 digitos, municipio prov2+muni3). (2) **Nivel administrativo:** la clave de bloque de Signal B usa `province` como "misma unidad geo" (faceta 7/8: `block_key=(make,model,year,km,province)` :397 [VERIFIED]). El ancho determina si el codigo del pais nuevo **cabe** en la columna; el nivel determina el **tamano del bucket** firma. Atomo: `CHAR(2)` es un contenedor fijo; un codigo de 3-5 chars **no cabe** (`value too long for type character(2)`). Y el nivel elegido es un dial de granularidad: grano grueso (pocas unidades grandes) -> buckets "misma provincia" enormes -> mas pares candidatos en Signal B -> el O(n^2) (faceta 3) y el riesgo de over-merge suben.

#### (c) Costura ES->generico
0052/0053 generalizan la **identidad** (PK/FK compuesta por pais) pero **NO el ancho**: las columnas siguen `CHAR(2)`/`CHAR(5)` ES/INE-moldeadas. Costuras exactas:
- **Ancho:** DE Kreis = 5 digitos, AGS municipal = 8; FR ultramar = '971'-'976' (3 chars); IT ISTAT = 6; PT freguesia = 6. Ninguno cabe en `CHAR(2)` provincia. **Fix:** migracion **0054 `CHAR(n)->VARCHAR(n)`** con `n` tomado de un **contrato de pack** (no soldado), y `geo_unit_width` como dato del `GeoProfile` por pais.
- **Nivel:** el "misma unidad geo" debe ser parametrico `geo_unit_level` (ES=provincia/NUTS3; DE podria ser Kreis, no Bundesland). **Fix:** drivear nivel + numero-de-unidades + ancho desde **ISO 3166-2** (pycountry), no desde el sentinel INE. Las CHECKs ya estan relajadas por pais (:166-174); falta que el **ancho** deje de ser `CHAR(2)`.

#### (d) Riesgo adversarial
- **No cabe (MEDIUM, mecanico):** un pais con primer nivel >2 chars revienta el INSERT en `CHAR(2)` -> seed parcial con "value too long" a mitad de carga (la faceta geo:335 lo nombra). FR ultramar (3), DE Kreis (5) son los disparadores inmediatos.
- **Bucket inflado (over-merge):** forzar DE a 16 Bundeslander (2 digitos para caber en CHAR(2)) hace el bloque "misma provincia" **enorme** -> miles de pares mismo-(make,model,year,km) en una sola region -> Signal B colapsa unidades distintas (over-merge) y el cuadratico de faceta 3 explota. El ancho equivocado **fuerza** el nivel equivocado.
- **Cross-grain leak:** si el grano de dos paises difiere y la clave no lo cualifica (faceta 8), un '28' ES (Madrid provincia) y un '28' de otro esquema podrian compartir bucket -> fusion cross-frontera (la colision que 0053:3-4 prueba a nivel PK, viva a nivel matching).
- **Ruido:** codigos con padding/letras (IT alfanumerico, PT 'NNNN-NNN') rompen el assumption numerico `left(code,2)` aunque la CHECK este relajada por pais.

#### (e) Sellado + verificacion multi-via
- **Via 1 (cabe, contrato pre-INSERT):** un Table Schema frictionless declara `geo_unit_width` por pais; un fixture con codigo que **excede** el ancho **falla** la validacion ANTES de tocar la DB (rojo si pasara). El `n` de la migracion 0054 `VARCHAR(n)` sale del **mismo** schema (una sola fuente de verdad).
- **Via 2 (manifest golden):** el manifest derivado de ISO 3166-2 reproduce **ES byte-identico** (52 provincias, ancho 2); DE/FR/IT/MX/JP dan recuentos/anchos conocidos (16/101/107/32/47) cruzados contra una 2a fuente.
- **Via 3 (bucket sano):** medir el tamano del bloque firma por pais; si el p99 del bucket "misma unidad geo" sube respecto a ES, el nivel es demasiado grueso (senal de over-merge antes de sellar).
- **Via 4 (cross-grain=0):** assert que ningun cluster cruza `(country_code, geo_unit)` (faceta 22 elevada a DISTINCT country_code), y que el ancho real `max(length(code))` por pais <= `geo_unit_width` declarado.

#### (f) Herramienta nivel-inalcanzable
**pycountry** (LGPL-2.1, EUR0) - https://github.com/pycountry/pycountry [VERIFIED NEXT-LEVEL.md:527-533]: autoridad **ISO 3166-2** (empaqueta el dataset Debian iso-codes) que convierte en DATO el numero y el **ancho de codigo** de las subdivisiones de primer nivel de cada pais, alimentando un seal-manifest por pais (`geo_unit_level`, `geo_unit_width`, caps `KNOWN_REAL_MAX_*` derivados del conteo). Retira los sentinels ES/INE (`CHAR(2)`, cap<52=provincias ES). Uso build/config-time (no hot-path) -> LGPL no contamina; alternativa estricta-permisiva `iso3166` (MIT) + iso-codes JSON. **Frictionless Framework** (MIT, EUR0) - https://github.com/frictionlessdata/frictionless-py [VERIFIED NEXT-LEVEL.md:334-340]: Table Schema que declara el `geo_unit_width` por pais y **captura el overflow de ancho ANTES del INSERT** (falla con diagnostico claro en vez de "value too long" a mitad del seed); el `n` de la migracion **0054 CHAR->VARCHAR(n)** se toma del mismo schema. Complemento: **GeoNames** (CC-BY 4.0) - https://download.geonames.org/export/dump/ [VERIFIED NEXT-LEVEL.md:374-380] como loader N-niveles->3-slots que emite el code oficial por pais.

#### Resolución condensada — Faceta 24

- **Costura (ES→genérico):** 0052/0053 generalizan la IDENTIDAD geo (PK/FK compuesta (country_code,code), CHECKs ES relajadas por pais :166-174) pero NO el ANCHO: geo_province.code/entity.province_code siguen CHAR(2) y geo_municipality.code CHAR(5), moldeados por INE (:23, :12). El nivel 'misma unidad geo' del bloque firma (block_key province :397) es un sentinel ES, no un parametro.
- **Fix:** Migracion 0054 CHAR(n)->VARCHAR(n) con n tomado de un contrato de pack (frictionless), no soldado. geo_unit_width y geo_unit_level como datos del GeoProfile drivados desde ISO 3166-2 (pycountry). Las CHECKs ya estan per-country; falta des-soldar el ancho CHAR(2).
- **Adversarial:** MEDIUM mecanico: primer nivel >2 chars (FR ultramar '971'-'976' 3, DE Kreis 5) revienta el INSERT en CHAR(2) (seed parcial 'value too long'). Over-merge: forzar DE a 16 Bundeslander (2 digitos) infla el bucket 'misma provincia' -> Signal B colapsa unidades distintas + dispara el O(n^2) de faceta 3. Cross-grain leak: '28' ES vs '28' otro esquema comparten bucket (la colision que 0053:3-4 prueba a nivel PK). Ruido: codigos alfanumericos IT / 'NNNN-NNN' PT rompen left(code,2).
- **Sellado multi-vía:** Via1 contrato pre-INSERT: frictionless declara geo_unit_width; fixture con codigo que excede el ancho falla ANTES de la DB; el n de VARCHAR(n) sale del mismo schema. Via2 manifest golden ISO 3166-2: ES byte-identico (52, ancho 2); DE/FR/IT/MX/JP recuentos 16/101/107/32/47 cruzados con 2a fuente. Via3 bucket sano: p99 del bloque 'misma unidad geo' por pais no sube vs ES. Via4 cross-grain=0: ningun cluster cruza (country_code,geo_unit); max(length(code)) por pais <= width declarado.
- **Herramienta NEXT-LEVEL:** pycountry (LGPL-2.1, https://github.com/pycountry/pycountry) [VERIFIED NEXT-LEVEL.md:527-533] = autoridad ISO 3166-2 que vuelve dato el ancho+nivel+conteo de subdivisiones por pais para el seal-manifest (retira CHAR(2)/cap<52 ES); build-time, LGPL no contamina (alt MIT iso3166). Frictionless (MIT, https://github.com/frictionlessdata/frictionless-py) [VERIFIED :334-340] = Table Schema que captura el overflow de ancho ANTES del INSERT y fija el n de la migracion 0054 CHAR->VARCHAR(n). Complemento GeoNames CC-BY (loader N-niveles, :374-380).

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

<a id="faceta-25"></a>

### Faceta 25 — Guard km=0 / stock nuevo (no-colapso de unidades distintas)

> **Guard país-blind.** Escape km=0 vía VIN (acopla B#5); sesgo declarado = over-count medido.

#### (a) Code hints [VERIFIED]
- [VERIFIED cluster_vehicles.py:267-274] `_is_new_car(v)`: `km = v.get('km'); return km is None or km == 0` (:273-274). Doc: para estos coches A y B se deshabilitan salvo `vin_ref` compartido.
- [VERIFIED cluster_vehicles.py:277-286] `_can_merge_new_cars(va, vb)`: True solo si ambos `vin_ref` no-null e identicos tras `str(...).strip().upper()` (:282-286). Unico camino de merge permitido para stock nuevo.
- [VERIFIED cluster_vehicles.py:365-367] Aplicado en Signal A (foto-URL): `if _is_new_car(va) or _is_new_car(vb): if not _can_merge_new_cars(va, vb): continue`.
- [VERIFIED cluster_vehicles.py:415-417] Aplicado IDENTICO en Signal B (firma), antes del guard non-null-price (:426) y del +/-2% (:430).
- [VERIFIED cluster_vehicles.py:108] BLOCKING_RULES doctrina: 'km=0/NULL guard: new/catalogue stock listing treated as distinct unit unless vin_ref matches; declared bias = possible cross-platform over-count of new-car stock'.
- [VERIFIED cluster_vehicles.py:101, :106] Las reglas de Signal A (:101) y B (:106) repiten 'DISABLED for km=0/NULL unless shared non-null vin_ref'.

#### (b) Mecanismo al atomo
Doctrina cross-senal, NO una senal mas. Un coche nuevo/catalogo comparte fotos de catalogo y atributos identicos (make,model,year,km=0,list-price) entre dealers distintos pero es una unidad FISICA distinta. El guard intercepta CUALQUIER par donde uno tenga `km is None or km==0` (:273-274) y deshabilita Signal A y Signal B salvo el unico escape lawful: `vin_ref` no-null compartido y exacto (:282-286). Aplicado pair-wise en ambas senales (:365-367, :415-417) - incluso si la block-key de firma ya implica km=0 para todo el bloque, el guard se reaplica por par por correctitud. El sesgo declarado y aceptado es over-count (un duplicado genuino de coche nuevo se cuenta doble) porque under-count (colapsar stock distinto de dealer) es PEOR; el over-count se MIDE y declara (faceta 20, +/-dup_ci) en vez de fusionar a ciegas.

#### (c) Costura ES->generico
La logica del guard es country-blind (opera sobre `km` y `vin_ref`, atributos fisicos). La costura es la COBERTURA DEL ESCAPE: `_can_merge_new_cars` compara `vin_ref` como STRING exacto, sin validar que sea un VIN real ni decodificarlo, y el unico camino lawful para km=0 depende 100% de capturar VINs de 17 chars. Ademas `km==0` como proxy de 'nuevo' asume que un odometro a 0 SIEMPRE significa coche nuevo.

#### (d) Riesgo adversarial concreto
**Japon: HIGH.** JDM usa numero de chasis (no VIN de 17 chars) -> `vin_ref` ausente o no-17 -> `_can_merge_new_cars` NUNCA dispara para stock nuevo JP -> over-count de coches nuevos PERSISTE sin NINGUN escape lawful (con `photo_hash` 0% poblado - faceta 13 - tampoco hay pHash). Mercados con captura de VIN baja (la mayoria): el escape casi nunca aplica -> over-count de stock nuevo persiste. `km==0` proxy: en un mercado que codifica odometro-no-fijado como 0, un coche USADO con km desconocido se trata como nuevo y se BLOQUEA del merge (lado under-count, lo opuesto al sesgo declarado). Mexico NOM-001 (VIN 17) encaja sin problema. Ruido: un `vin_ref` de parseo-junk de 17 chars que colisione entre dos coches distintos dispararia un FALSO escape-merge (hoy nada lo valida).

#### (e) Sellado + verificacion multi-via
1. Test del guard: dos listings km=0 con VINs distintos (o uno None) -> NO se fusionan; mismo `vin_ref` no-null -> se fusionan.
2. Validacion del escape (tool): un VIN de parseo-junk (check-digit invalido) NO dispara el escape (vininfo lo rechaza por check-digit ISO-3779).
3. Gating de VIN por pais: fixtures de chasis JDM se clasifican non-VIN y se EXCLUYEN del escape (aseverado); JP degrada a over-count declarado honesto en vez de un brazo VIN vacio silencioso.
4. Ledger de over-count: el sesgo declarado se MIDE por pais (faceta 20) por dos vias ortogonales, no se esconde.

#### (f) Herramienta NEXT-LEVEL
[VERIFIED NEXT-LEVEL.md:495-501] **vininfo (BSD-3-Clause)** https://github.com/idlesign/vininfo. Libreria embebida network-free: decodifica WMI/VDS de un VIN de 17 chars y valida el check-digit ISO-3779 (posicion 9). Eleva el escape km=0 en tres frentes: (a) rechaza VINs de parseo-junk gratis (evita el falso escape-merge); (b) cross-checkea el fabricante decodificado contra el make normalizado del listing (caza corrupcion OCR/scrape); (c) gatea la aplicabilidad de VIN POR PAIS - decode OK para mercados VIN-17 (EU/MX), el chasis JDM falla el test 17-char/charset y se enruta a pHash en vez de producir un brazo vacio silencioso (cierra B5). Mas VINs capturados pasan a auto-merges lawful mas alla de las 18 filas actuales. EUR0, datos embebidos, pure-Python, sin red. Alternativa ortogonal: NHTSA vPIC decode flat-file (US gov, gratis) para cross-check de WMI.

#### Resolución condensada — Faceta 25

- **Costura (ES→genérico):** La logica del guard es country-blind (opera sobre km y vin_ref). La costura es la cobertura del ESCAPE: _can_merge_new_cars (cluster_vehicles.py:282-286) compara vin_ref como string exacto sin validar ni decodificar, y el unico camino lawful para km=0 depende de capturar VIN de 17 chars. Ademas km==0 como proxy de 'nuevo' asume odometro-a-0 = coche nuevo siempre.
- **Fix:** Ensanchar+validar el escape VIN via vininfo: decode WMI/VDS + check-digit ISO-3779 + cross-check WMI->make, y gatear la aplicabilidad de VIN por pais (VIN-17 EU/MX vs chasis JDM -> ruta pHash, no brazo vacio silencioso). Distinguir 'odometro no-fijado' de 'genuino 0' por conector para que km==0 no mal-clasifique usados de km desconocido como stock nuevo.
- **Adversarial:** Japon HIGH: JDM usa chasis (no VIN-17) -> vin_ref ausente/no-17 -> _can_merge_new_cars nunca dispara -> over-count de stock nuevo persiste sin escape lawful (photo_hash 0%, faceta 13). Captura de VIN baja (la mayoria de mercados): escape casi nunca aplica. km==0 proxy falla donde el odometro no-fijado se codifica como 0 (usado tratado como nuevo, lado under-count). vin_ref junk de 17 chars colisionado dispararia falso escape-merge (hoy nada valida).
- **Sellado multi-vía:** (1) Dos km=0 con VIN distinto (o None) -> no merge; mismo vin_ref no-null -> merge. (2) VIN de parseo-junk (check-digit invalido) NO dispara el escape (vininfo). (3) Fixtures de chasis JDM clasificados non-VIN y excluidos del escape (aseverado); JP degrada a over-count declarado honesto. (4) El over-count declarado se mide por pais por dos vias (faceta 20), no se esconde.
- **Herramienta NEXT-LEVEL:** vininfo (BSD-3-Clause) https://github.com/idlesign/vininfo [VERIFIED NEXT-LEVEL.md:498] - decode WMI/VDS embebido + validacion check-digit ISO-3779 + cross-check WMI->make; ensancha el escape km=0 lawful mas alla de 18 filas, rechaza VIN junk (evita falso merge) y gatea VIN por pais (VIN-17 EU/MX vs chasis JDM->pHash). Alternativa: NHTSA vPIC flat-file (gratis) para cross-check WMI.

[⇧ Índice de sub-proyectos](#indice-subproyectos)

---

## Mejoras a nivel inalcanzable (€0, priorizadas)
1. **[P0, S] Cualificar `CountryFirmaKey` + Check 0 cross-país + watermark per-país.** La corrección de correctitud multipaís. Invisible hoy (solo filas ES); **debe enviarse ANTES del país #2** o el primer cluster global produce fusiones cross-frontera silenciosas. Es el riesgo #1 de la etapa.
2. **[P1, M] Ruta de escritura de `photo_hash` (INSERT+REFRESH) + backfill gateado por governor**, hasheando inline las fotos ya descargadas. Desbloquea strong-key pHash, PHOTO_CHANGE content-aware y la única vía de auto-merge de Japón. (Egress per-host → gate operativo, no per-país.)
3. **[P1, M] Calibrar `PHASH_HAMMING_MAX` (=10) y el umbral del watermark (≤6)** contra un set etiquetado mismo-coche/distinto-coche cosechado gratis en el scrape; separar las dos semánticas (recompresión vs identidad). Depende de (2).
4. **[P2, M] VIN-decode (WMI/VDS) como strong-key gratis:** el WMI de un VIN de 17 identifica make+planta → cruzar contra `make` para cazar junk de parseo y habilitar auto-merge lícito más allá de las 18 filas actuales. Necesita tabla WMI libre embebida.
5. **[P2, S] pHash quality-aware:** excluir de Signal A las fotos casi sin estructura (`PhotoHash.quality~0`, `delta_photo.py:74-79`) en vez de depender solo del conteo de colisión K → mata placeholders **estructuralmente**. Depende de (2).
6. **[P3, L] IA-local obrera (capa 2) para equivalencia semántica de título/trim** ("Ibiza FR" vs "Ibiza Sport"), reforzando Signal B más allá del título-exacto, **solo en lo irreducible, determinista-primero**. Riesgo de over-merge → detrás del gate VAM. Requiere modelo local (GPU) con caso de uso probado.
7. **[P3, M] Promover `vehicle_event.event_type` a ENUM** (codec de 8 valores) y **particionar el timeline por `observed_at`** para escala de serving (el doc 03 describe un particionado que no existe). Migración + swap del CHECK a ENUM sin romper los 5 valores vivos.

---

## Riesgos / open items
- **[RIESGO #1] Falso-merge cross-frontera LATENTE.** Dispara en silencio en cuanto aterriza el país #2 si no se cualifica la clave firma antes. **Ningún test lo captura hoy** porque solo hay filas ES. Mitigación: P0 de arriba. [causa: `cluster_vehicles.py` sin `country_code`; gate: antes del país #2]
- **[OPEN] Japón sin vía de auto-merge lícita.** Chasis JDM ≠ VIN-17 (`watermark:59`) **y** `photo_hash` 0% poblado → 100% del duplicado servido como ±dup_ci ancho. [causa doble; gate: plan pHash + `title_norm_policy=CJK`]
- **[OPEN] Umbrales pHash sin calibrar.** `PHASH_HAMMING_MAX=10` (`delta_photo.py:33-34`) y watermark `≤6` (`watermark:14`) ambos **ASSUMED**; confiar en ellos antes de calibrar puede over/under-fusionar. [gate: backfill `photo_hash` + set etiquetado]
- **[OPEN] `photo_hash` 0% poblado.** Dedup fuerte limitado a VIN-exact (18 filas); over-count ~131.8K persiste, servido honestamente como ±dup_ci pero con cota ancha. [gate: P1]
- **[GATE ESQUEMA] Ancho del grano geo.** Kreis DE / ultramar FR no caben en `CHAR(2)`; el ensanche es FK-breaking (mecánica `0053`), reversible pero entra por la puerta ESQUEMA de `cover(CC)`.
- **[OPERATIVO] Stack caído (PG `:5433` cerrado).** Todos los checks de cluster/anti-FP DB-backed son **no ejecutables ahora mismo**; solo lo de función-pura es verificable sin levantar el stack. Las cifras DB de este capítulo son punto-en-el-tiempo (fuente citada en cada una). [gate: levantar stack supervisado]
- **[NOTA, no rotura] Precio refrescado puede mover un vehículo de bloque firma entre runs:** `emit_change_deltas` refresca `price`/`km`/`photo_url` y la firma de cluster lee `price`. Aceptable: el dedup se recomputa cada run, idempotente, no acumula estado.
- **[NOTA] Comparación de precio currency-blind:** inocua entre dos mercados EUR; un país no-EUR sin fijar `vehicle.currency` produciría comparaciones ±2% sin sentido. Cerrada por FIX-B.
