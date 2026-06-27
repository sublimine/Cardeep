# COUNTRY-PROOF — La genericidad que se auto-impone (no se puede regresar)
> El level-up. El `SPINE-COUNTRY-THREADING` dice "enhebra country_code en 30 sitios" — un checklist que se pudre. Esto lo eleva a **INVARIANTE MECÁNICO**: el motor hace IMPOSIBLE el false-merge transfronterizo y la fuga de país, y lo PRUEBA solo en cada cambio. La misma genialidad que el VAM-por-triggers, aplicada a la dimensión país. Mandato owner 2026-06-27 ("jugar en otra liga"). Coste €0.

## El salto de liga
- **Liga normal:** "manejamos varios países" — con cuidado, query por query. Se rompe en silencio al añadir código.
- **Liga superior:** "corromper la garantía multi-país es **mecánicamente imposible**." El sistema se niega a fundir entidades de dos países y a servir una query sin país; un golden lo demuestra en CI en cada push. La corrección no depende de la disciplina del que toca el código — la impone la máquina.

## 1 · Invariante de aislamiento de país (impuesto en la DB)
**Regla:** todo cluster canónico (`entity_cluster`, `canonical_dedup`, `vehicle_cluster`) debe tener miembros con **un solo `country_code`**.
- **Fix (la vía):** el build de **cada** capa de fusión scopea por `country_code`. La Ola 2.5 (re-verificación adversarial 2026-06-27) probó que la enumeración original era **incompleta**; el censo completo de costuras country-blind es:
  - `cluster_dealers.py:410-430` aristas 1-3 block-key `(norm_name|phone|web, municipality_code)` country-blind `[VERIFIED grep -c country_code cluster_dealers.py = 0]`.
  - `cluster_dealers.py:262-392` **ARISTA-4 fuzzy SQL** (`_load_fuzzy_sql_edges`): temp table `_tmp_fuzzy_candidates(entity_ulid, muni_code, norm_name)` sin país `[VERIFIED :312-318]`, self-join `a.muni_code = b.muni_code` SOLO `[VERIFIED :366]`, `levenshtein(norm_name) <= 2` `[VERIFIED :377]` — fusión MÁS ancha que la arista-1 (une nombres NO idénticos).
  - `cluster_vehicles.py` **Signal B firma** block-key `(make, model, year, km, province)` sin país `[VERIFIED :397]` **y Signal A photo_url** indexado por `_normalize_photo_url` SOLO, sin país/provincia `[VERIFIED :326-376]` — Signal A es «suficiente solo» `[VERIFIED :10-14]` y funde con `only_photo` sin corroboración de firma `[VERIFIED :471-473]`.
  - check anti-FP `HAVING COUNT(DISTINCT province_code)>1` ciego al país `[VERIFIED :852]` **y además sólo `print`, post-write** (ver §"Vector concreto", honestidad anti-FP).
  - `resolve_entities.py` (resolver β) funde cross-province por `Jaccard>=0.30` con `signals=["fingerprint"]` sin país `[VERIFIED :690-691,:756-757]`; consume `vehicle_cluster.canonical_vehicle_ulid` `[VERIFIED :462-466]` → un cross-merge de Signal A se propaga aquí.
  - `build_canonical_dedup.py` une canonicals por `deep_link` compartido sin país `[VERIFIED :27-36, ANTI_HUB_K=3 :88]` → escribe `canonical_dedup` = **Layer-2 de la vista SERVIDA `v_dealer_resolved`** `[VERIFIED 0028:57-67]`.
  - `cross_source_dedup.py` aristas `(value, muni)` sin país `[VERIFIED :454-457]`, escribe `entity_cluster` gateado `vam_verified=FALSE` `[VERIFIED :52-53]`.
- **Guard (la garantía):** validaciones SQL que assertan `COUNT(DISTINCT country_code) = 1` por cluster **servido**, en **dos** vistas de servicio (no una): `v_dealer_resolved` (dealer, incluye la Layer-2 `canonical_dedup`) **y** `v_canonical_vehicle` (vehículo). Un build con bug que cruce países **FALLA y no sirve** — no degrada en silencio. `country_code` ya está en `entity` (mig 0052); `vehicle` NO lo tiene `[VERIFIED: ninguno en 0003]`, así que el guard de vehículo llega al país por `JOIN entity` — construible HOY igual que el de dealer.

## 2 · Golden cross-country (regresión permanente en CI)
- **Fixture dealer (arista-1):** inserta una entidad DE sintética que **COLISIONA** en `(norm_name, municipality_code)` con una ES — el vector EXACTO de false-merge confirmado (`0053:4` reusa el code '28' Madrid↔Munich).
- **Fixture dealer (ARISTA-4 fuzzy):** entidad DE `'talleres garcic'` en muni `'28001'` vs ES `'talleres garcia'` (`levenshtein=1 <= 2`) → el self-join `muni_code`-solo `[VERIFIED cluster_dealers.py:366]` las funde hoy; el golden asserta 0 merge. **Un fixture name+muni exacto (arista-1) NO ejercita la arista-4** — se necesita el par fuzzy explícito.
- **Fixture vehículo — Golden Signal A (foto compartida):** dos `vehicle` con el **mismo** `_normalize_photo_url` (feed mayorista/subasta/CDN-OEM, < `K=12` listings → pasa el guard high-collision `[VERIFIED :338-347]`), `entity` ES-`28` y DE-`28`, mismo `make/model/year`, `km>0`, `span=0` (pasa el guard cross-generación `[VERIFIED :372-373]` y el guard km=0 `[VERIFIED :365-367]`) → **0 merge** cross-país. Hoy `cluster_vehicles.py:326-376` indexa por `_normalize_photo_url` SOLO `[VERIFIED grep -c country_code = 0]` y funde con `only_photo` `[VERIFIED :471-473]`. **El fixture DEBE sembrar el `photo_url` compartido**: un `TestIsolationVehicle` que sólo ejercita Signal B (firma make/model/year/km/title) NO cubre este vector y deja el golden VERDE con el merge vivo.
- **Fixture vehículo — Signal B firma:** VW Golf ES-`28` y DE-`28`, `year/km` iguales, `price` ±2 % EUR, título idéntico → 0 merge.
- **Fixture β (inventory-fingerprint):** un dealer ES y uno DE que comparten `>=30 %` de `canonical_vehicle_ulid` (alcanzable vía un cross-merge Signal A) → β `[VERIFIED resolve_entities.py:756-757]` los funde cross-país hoy; el golden lo bloquea. (β no está servido aún `[VERIFIED: 0 refs en services/]` → ver PR-8: cerrar ANTES de gatear.)
- **Asserts:** (a) **ningún** resolver de las capas de arriba (dealer aristas 1-4, vehículo Signal A+B, β, `canonical_dedup`) las funde (0 cross-country clusters); (b) los **dos** guards SQL (`v_dealer_resolved` y `v_canonical_vehicle`) devuelven 0 filas con `COUNT(DISTINCT country_code)>1`; (c) cada vista servida (`/geo`, `/stats`, `/geo/seal`, `inventory`) devuelve **solo** el país pedido; (d) los `due-select`/`silence`/locks del scheduler llevan predicado de país.
- Corre en CI en cada push → la ceguera de país **no puede reaparecer** sin que el build se ponga rojo.

## 3 · Meta-test "toda query servida lleva país"
Un test que **enumera** las queries de `services/api/` y del pipeline que tocan `geo_*`/`entity`/`vehicle` y asserta que cada una filtra `country_code` (o lo justifica explícitamente en una allow-list con razón). Convierte "30 fixes manuales que hay que recordar" en **UNA garantía enumerada y verificable**.

## Cómo se PRUEBA (las 3 vías del blindaje — `ANTI-DRIFT-HARDENING`)
- **(a)** el golden cross-country verde en CI;
- **(b)** un inquisidor intenta construir un cross-merge a mano y el invariante lo **bloquea** (falla al romperlo);
- **(c)** verificación independiente: recompute SQL de `COUNT(*)` de clusters con `>1 country_code` en lo servido = **0**.
Sin las tres, el invariante está `[ASSUMED]`, no `[VERIFIED]`.

## Por qué es €0 y por qué AHORA
`country_code` ya existe (0052/0053). Esto es **lógica + 1 migración aditiva (trigger/validación) + 1 fixture + 1 meta-test** — cero infra, cero gasto, additive/reversible. Es el guard que transforma el spine-fix de "checklist que se pudre" en **garantía institucional**: el motor genérico defiende su propia genericidad.

## Generalización (el principio que eleva todo)
El patrón se repite para cada invariante de la liga superior: **no documentar la regla — hacer que la máquina la imponga y la pruebe sola.** Aplicable a: aislamiento de país (este doc), no-fabricación (guardrail de gramática), no-adivinar (escalado obligatorio), denominador-como-intervalo (sellado mecánico sobre CI). Cada uno = fix + guard + golden. Esa es la diferencia de liga.

## Vector concreto (verificado) y aserción del guard
**El false-merge, al átomo** [VERIFIED `pipeline/identity/cluster_dealers.py:404-440`]: la arista-1 une por `(norm_name, municipality_code)` **sin `country_code`**. Dos entidades con el mismo `municipality_code` (p.ej. DE reusa el code de Madrid `28`, `migrations/0053`) y nombre normalizado igual → misma componente union-find → mismo `resolved_cdp_code` en `v_dealer_resolved` [VERIFIED `migrations/0028_dealer_resolved.sql:35-76`]. Un dealer alemán y uno español se funden en uno.

**Aserción del guard DEALER (`v_dealer_resolved`, cubre B1 + Layer-2 `canonical_dedup`):**
```sql
-- Debe devolver 0 filas. >0 = false-merge transfronterizo en lo servido.
SELECT d.resolved_cdp_code, COUNT(DISTINCT e.country_code) AS n_countries
FROM v_dealer_resolved d
JOIN entity e ON e.cdp_code = d.cdp_code   -- [VERIFIED 0028:70-76 — la vista proyecta cdp_code de la entidad-miembro]
GROUP BY d.resolved_cdp_code
HAVING COUNT(DISTINCT e.country_code) > 1;
```
> `v_dealer_resolved` resuelve por DOS capas `[VERIFIED 0028:35-76]`: B1 (`v_canonical`) **y** `canonical_dedup` (Layer-2, `deep_link`). Por eso este guard único **también** atrapa un cross-merge de `build_canonical_dedup.py` — pero sólo si las dos entidades llevan etiqueta de país distinta (precondición que el write-site country-blind de `discover.py:91-104` y `ON CONFLICT (cdp_code)` `[VERIFIED :101]` derrota hasta PR-7; ver blueprint).

**Aserción del guard VEHÍCULO (`v_canonical_vehicle`) — NUEVO, exigido por la Ola 2.5 (Signal A):**
```sql
-- Debe devolver 0 filas. >0 = false-merge de vehículo transfronterizo servido.
-- vehicle NO tiene country_code [VERIFIED: ninguno en 0003]; el país llega vía entity (0052).
SELECT vc.canonical_vehicle_ulid, COUNT(DISTINCT e.country_code) AS n_countries
FROM v_canonical_vehicle vc                       -- [VERIFIED 0023:57-76 — vista servida del run vam_verified]
JOIN vehicle v ON v.vehicle_ulid = vc.vehicle_ulid
JOIN entity  e ON e.entity_ulid  = v.entity_ulid  -- [VERIFIED entity.country_code 0052]
GROUP BY vc.canonical_vehicle_ulid
HAVING COUNT(DISTINCT e.country_code) > 1;
```
> Es el espejo exacto del check anti-FP que ya existe `[VERIFIED cluster_vehicles.py:843-853]`, cambiando `province_code` por `country_code`. Hasta hoy NO existía guard de vehículo: el invariante nombraba `vehicle_cluster` (§1) pero la única aserción era dealer-only — la Ola 2.5 lo rompió por ahí.

**Honestidad anti-FP (no maquillar):** el check in-pipeline `_run_anti_fp_checks` `[VERIFIED cluster_vehicles.py:834-859]` (a) cuenta `province_code`, ciego al país, y (b) sólo hace `print` `[VERIFIED :858-859]` y corre en `main()` **DESPUÉS** del write+commit (Step 4 `_write_to_pg` :939 → `autocommit=True` :942 → Step 5 :944) `[VERIFIED :938-944]`. Es decir: un cross-merge se **escribe y sirve** y el check sólo lo imprime. El fix de PR-2 lo convierte en chequeo **pre-write BLOQUEANTE** (raise + rollback de la txn), no un `print` posterior.

**El fix (la vía):** añadir `country_code` a la clave de bloque de **cada** arista (1-3 **y 4-fuzzy**) en `cluster_dealers.py`, a Signal A **y** Signal B en `cluster_vehicles.py`, convertir el check anti-FP en pre-write bloqueante por `(country_code, province_code)`, scopear `resolve_entities.py` (β), `build_canonical_dedup.py` (`deep_link`) y `cross_source_dedup.py` (`(value, muni)`), y las queries servidas de `geo.py`. El orden ejecutable PR-por-PR vive en [`REMEDIATION-BLUEPRINT.md`](REMEDIATION-BLUEPRINT.md) (PR-1, PR-2, PR-8, PR-9).

## Honestidad de ejecución (blindaje — no maquillar)
Stack vivo CAÍDO → **no puedo ejecutar el golden ahora**; declararlo "probado/funcional" sin correrlo sería el maquillaje que el mandato prohíbe. Estado del invariante:
- **`[ASSUMED-por-lectura-de-código]`**: la arista-1 es country-blind (verificado en `:404-440`) → el merge ocurriría.
- **`[VERIFIED]` pendiente de** correrlo contra `:5434`.

**Secuencia al levantar la DB (restart owner):** (1) golden RED **prueba** el merge → la afirmación del inquisidor pasa de palabra a hecho mecánico; (2) aplico fix + guard (migración aditiva + scope de aristas); (3) golden GREEN + recompute=0; (4) las 3 vías del blindaje. Hasta entonces: **spec + vector verificado**, NO afirmación de funcional. El guard es el **criterio de aceptación** de toda la transformación spine: ninguna etapa se declara country-proof sin su golden cross-country en verde.
