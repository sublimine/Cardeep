# Etapa 4 · Identidad — Biblia (v2 PROFUNDO)

> Estado adversarial: **NEEDS_REWORK** (`holds=false`). Fuente: Wave 1 (insumo `04-identity.json`) + **deep-dive v2 por faceta** (24 sub-proyectos, `relleno/04-identity/g0..g6.json`), con `path:linea` **re-verificado en vivo**. Stack vivo **CAÍDO** al auditar (PG `:5433` cerrado): toda cifra de DB es **punto-en-el-tiempo**, no entero eterno.
>
> Hallazgo transversal (confirmado por todos los inquisidores): `country_code` se enhebró en el **esquema** (`0052/0053`) y en el prefijo `cdp_code` (`codes.py`), pero **NO** en la lógica de `pipeline/identity` ni en las vistas servidas. La etapa es **country-BLIND** por debajo del esquema. **[VERIFIED grep: `country_code` en `pipeline/identity` → 0 matches]**.
>
> **Novedad v2:** este capítulo añade **`## Sub-proyectos institucionales (360 por faceta)`** — las **24 facetas** de la etapa, cada una un proyecto navegable con deep-spec verificado + costura + fix + adversarial + sellado + herramienta NEXT-LEVEL (€0). El deep-dive **corrige** a v1 en cinco puntos (marcados `[CORRIGE v1]`): (1) las 5-6 copias de `UnionFind` **ya divergen** en algoritmo y nombres, no son duplicación inerte; (2) son **62** los archivos con literal `CDP-ES-`, no 41 **[VERIFIED grep=62]**; (3) la clave de nombre del residual (Layer 4) **ya diverge** de B1 (sin strip de sufijo) + una **4.ª** normalización en SQL; (4) la contradicción doc↔código de `build_canonical_dedup` (`:96` "non-fatal" vs `:463` `sys.exit(1)`) está **confirmada al átomo**; (5) la etiqueta `rep=MIN(cdp)` de `build_particular_dedup` **está obsoleta** vs el `most-available` vivo.

---

## Navegación (funnel)

**Capítulo (estructura A→Z):**
[Misión](#misión) · [Lo que existe HOY](#lo-que-existe-hoy-verificado) · [Motor](#motor-invariante-reusado-byte-idéntico-por-país) · [Pack por país](#pack-por-país-lo-que-cada-país-aporta-para-esta-etapa) · [Costuras → fix](#costuras-es-hardcoded--fix) · [Diseño genérico A→Z](#diseño-genérico-az) · [Onboarding](#onboarding-de-país-nuevo-pasos-de-biblia-para-esta-etapa) · [Sellado + rollback](#sellado--verificación-multi-vía--rollback) · [Veredicto adversarial](#veredicto-adversarial-roturas--resolución) · [**Sub-proyectos (360 × 24)**](#sub-proyectos-institucionales-360-por-faceta) · [Mejoras nivel-inalcanzable](#mejoras-a-nivel-inalcanzable-0-priorizadas) · [Riesgos / open items](#riesgos--open-items)

**Los 24 sub-proyectos (por familia):**

| Familia | Sub-proyectos |
|---|---|
| **A · Primitiva del motor** | [F1 UnionFind](#f1-unionfind-primitiva-de-cierre-transitivo-unificada) |
| **B · Pack de normalización (autoridades locale)** | [F2 Teléfono E.164](#f2-autoridad-telefonica-e164-generica-por-plan-de-numeracion) · [F4 Nombre + sufijos legales](#f4-autoridad-de-normalizacion-de-nombre-y-lexico-de-sufijos-legales) · [F5 Script / transliteración](#f5-politica-de-script-y-transliteracion-unicode-con-guardia-de-nombre-vacio) · [F6 Cadenas / multisucursal](#f6-autoridad-de-exclusion-de-cadenas-y-multisucursal) · [F20 Registral / tax-id](#f20-esquema-registral-y-tax-id-cif-a-id-nacional-generico) · [F21 Dirección](#f21-autoridad-de-normalizacion-de-direccion-guard-de-sucursal) · [F12 Taxonomía de source-keys](#f12-pack-de-taxonomia-de-source-keys) |
| **C · Minteo de identidad inmutable** | [F7 Mint cdp_code/canonical_key](#f7-autoridad-de-minteo-cdp_code-y-canonical_key) · [F3 Validador de prefijo + G1](#f3-validador-de-prefijo-cdp_code-gate-g1-y-los-62-literales) |
| **D · Clustering B1 + topología** | [F9 B1 scoping + dispatch](#f9-b1-clusterer-scoping-de-run-y-dispatch-de-locale) · [F10 Topología 4 aristas](#f10-topologia-de-blocking-de-4-aristas-y-guardas-fuzzy) · [F23 Selección de representante](#f23-seleccion-de-representante-canonico-consistente-entre-4-capas) |
| **E · Cadena de overlays dedup** | [F11 Cross-source B6.1](#f11-motor-de-dedup-cross-source-b61-ortogonalidad-osm-y-digital) · [F13 Deep-link L2](#f13-dedup-super-canonico-deep-link-layer-2-y-asserts-de-censo) · [F14 Particular L3](#f14-dedup-particular-province-split-layer-3-y-modelo-de-identidad-del-particular) · [F15 Residual L4](#f15-dedup-residual-name-muni-layer-4-y-fix-bystander-drag) · [F16 Backfill canonical_key](#f16-backfill-forward-coverage-de-canonical_key) · [F18 Composición coarsen-only](#f18-arquitectura-de-composicion-de-la-cadena-de-overlays-coarsen-only) |
| **F · Capa beta (no servida)** | [F8 resolve_entities](#f8-capa-beta-resolve_entities-desacople-es-y-seguridad-de-activacion) |
| **G · Espina servida + sellado + red** | [F17 Vistas servidas (LA ESPINA)](#f17-vistas-de-resolucion-servida-y-gate-por-pais-la-espina) · [F24 No-destructivo + rollback](#f24-disciplina-no-destructiva-idempotente-y-rollback-por-pais) · [F19 Red anti-over-merge](#f19-red-de-regresion-anti-over-merge-country-aware) · [F22 Registro IdentityLocale + CI gate](#f22-registro-identitylocale-y-gate-ci-fail-fast) |

---

## Misión

Resolver **identidad de punto de venta**: colapsar las N apariciones de un mismo dealer físico (a través de fuentes ortogonales) en **un único canónico** sin fusionar de más (over-merge) ni de menos (under-merge), de forma **determinista, idempotente, append-only y no destructiva**, y servir esa resolución bajo gate VAM.

El norte genérico: el **motor** de identidad (UnionFind, topología de 4 aristas muni-bloqueadas, escalera de selección canónica, cadena de overlays vam-gated, red anti-over-merge) es **invariante byte-idéntico por país**. Lo único que cambia por país es un **pack profundo de normalización local** (plan telefónico, léxico de sufijos societarios, cadenas/consolidadores, autoridad de id fiscal, léxico de direcciones). País nuevo en esta etapa = **una fila `IdentityLocale` + un golden de teléfono + correr los mismos 5 scripts country-scoped**. El motor, el esquema, las vistas, el gate y la red de regresión se tocan **cero veces**.

Hoy ese norte **no se cumple en código**: el pack está incrustado y duplicado, las corridas y el gate son **globales únicos**, y el bloqueo puede **false-merge transfronterizo**. Este capítulo integra cada rotura con su resolución de diseño (o la marca como open item con causa y gating), y la baja al átomo en los 24 sub-proyectos.

---

## Lo que existe HOY (verificado)

> Provenance: evidencia VERIFIED del objeto de diseño Wave 1 + deep-dive v2. Los ítems marcados ★ los **re-leí de la fuente**; el resto porta la línea verificada del objeto.

- ★ **B1 — clusterizador determinista de dealers.** `UnionFind` (path-compression + union-by-rank sobre ULIDs string) sobre 4 tipos de arista reproducibles (name+muni, phone≥7+muni, web_host+muni, levenshtein SQL ≤2 mismo muni), idempotente (delete `RUN_ID` + reinsert), escribe `entity_cluster_run`+`entity_cluster`. **[VERIFIED `cluster_dealers.py:194` UnionFind, `:400` aristas 1-3, `:262` arista 4 fuzzy, `:56` `RUN_ID='dealer-identity-det-v1'`, `:558` `_write_to_pg`]**.
- ★ **Autoridad de teléfono ES E.164** (pure-stdlib): valida el plan español (nacional=9 dígitos, leading ∈ {6,7,8,9}), quita `+34`/`0034`, devuelve clave de 9 dígitos o `+34XXXXXXXXX` canónico; nunca un substring frágil. **[VERIFIED `phone_es.py:20` `_VALID_LEADING=frozenset("6789")`, `:23-38` `_national`, `:41-49` `phone_match_key`/`normalize_es_phone`]**.
- **Dedup cross-source (B6.1)**: aristas ortogonales phone/website/name OSM↔plataformas digitales, muni-required, chain-guard, rechazo por divergencia Jaccard; el teléfono ya delega en la autoridad única `phone_es`. **[VERIFIED `cross_source_dedup.py:91` import `phone_match_key`, `:231-240` delega, `:163-176` `_CHAIN_PATTERNS`, `:322` UnionFind]**.
- ★ **Normalizador frágil legacy aún vivo** en la capa beta `resolve_entities`: "últimos 9 dígitos, ≥7" SIN validación de forma española y SIN delegar en `phone_es`. **[VERIFIED `resolve_entities.py:135-146` `_normalize_phone` → `digits[-9:]`, usado en `:569`]**. (Es deuda latente — ver costuras / F8.)
- **Overlay de cluster no destructivo + vista servida vam-gated**: `entity_cluster_run`/`entity_cluster`; `v_canonical` resuelve cualquier entity→canónico desde la **única** corrida más reciente con `vam_verified=TRUE`; `cdp_code` inmutable nunca se muta. **[VERIFIED `0020_entity_cluster.sql:16` run, `:34` member, `:51-67` `v_canonical`]**.
- **Overlay deep-link super-canónico** (arregla split de geocoding aguas arriba): union-find sobre canónicos que comparten una URL de listing, anti-hub `K=3` excluye hubs, exclusión `kind<>'particular'` evita el over-merge de 113k, idempotente con asserts de divergencia ruidosos. **[VERIFIED `0027_canonical_dedup.sql:43/69`, `build_canonical_dedup.py:88` `ANTI_HUB_K=3`, `:191` `kind<>'particular'`, `:441-463` asserts]**.
- **Resolución servida de dos capas** `v_dealer_resolved` = B1 (`v_canonical`) → deep-link/particular/residual (`canonical_dedup`), ambas vía COALESCE-to-self, **una sola** corrida dedup `vam_verified` más reciente; es la fuente de cardinalidad de API/health. **[VERIFIED `0028_dealer_resolved.sql:35-76`]**.
- **Dedup particular province-split**: `canonical_key` (`particular:{platform}:{sellerId}`) funde los N `cdp_code` provinciales del mismo vendedor privado; superconjunto ESTRICTO de la corrida servida, INERTE (`vam_verified=FALSE`) hasta gatear. **[VERIFIED `build_particular_dedup.py:65-71`, `:86-114` casos A/B/C, `:132` `vam_verified=FALSE`]**.
- **Dedup residual name+muni** con fix de bystander-drag: funde stragglers exactos `(norm_name,muni)` solo si ninguna base tocada arrastra un miembro fuera de los códigos del grupo; guards same-address + chain-token + ambigüedad; `--commit` gatea VAM; snapshot previo. **[VERIFIED `build_residual_namemuni_dedup.py:209-218`, `:69-72` `CHAIN_TOKENS`, `:279-341` asserts, `:360-366` snapshot]**.
- **Backfill de `canonical_key` (forward-coverage)**: recomputa la pre-imagen del `cdp_code` desde inputs guardados y escribe `canonical_key` SOLO si re-hashea al `cdp_code` almacenado (una clave errónea es imposible de escribir); consistencia eventual, cadencia de scheduler. **[VERIFIED `canonical_key_backfill.py:41-69`, `:88` gate `code==row['cdp_code']`]**.
- ★ **Autoridad `cdp_code`/`canonical_key` YA country-paramétrica**: `country_code` enhebrado en cada coder, vive SOLO en el prefijo humano de `mint_code`, **deliberadamente excluido** de la pre-imagen hash de `canonical_key` para que enhebrarlo no pueda re-key ninguna entity ES. **[VERIFIED `codes.py:44-53` `mint_code` (`:53` `f"CDP-{country_code}-{province_code}-{_base32(digest)}"`), `:56-65` `canonical_key` acepta-pero-no-usa `country_code`, `:100-118` `cdp_pair`]**.
- **Red anti-over-merge** (SQL ortogonal, no los asserts del propio build): 0 componentes cross-kind, componente máx ≤30, trade-names distintos ≤12, 0 miembros groseramente más ricos que el rep, conteo servido == recomputo independiente; test unit DB-free de cap-sanity. **[VERIFIED `test_dedup_invariants.py:142` `_CROSS_KIND_COMPONENTS`, `:75-76` caps 30/12, `:184` `_RICHER_THAN_REP`, `:357-394` served==recompute, `:228-258` cap-meaningfulness]**.
- **Golden de la autoridad de teléfono**: válido→E.164 y malformado→None exhaustivos (extensión, longitud, leading inválido, no-español), más colapso de variantes de prefijo. **[VERIFIED `test_phone_es.py:18-64`, `test_cross_source_phone.py:23-27` paridad-legacy + malformado-rechazado]**.
- ★ **Dimensión `entity.country_code`** existe (`CHAR(2) NOT NULL DEFAULT 'ES'`) con índice de país — el linchpin de scoping para corridas de identidad por país y dispatch de locale. **[VERIFIED `0052_country.sql:54` ALTER, `:80` `idx_entity_country`]**.
- **Strip de sufijo legal ES (FIX-B)**: formas societarias finales (`sl/sa/slu/sau/sll/scp/scoop/sociedadlimitada…`) eliminadas del nombre normalizado; guard de mín-3-char tras strip. **[VERIFIED `cluster_dealers.py:117-167`, duplicado en `cross_source_dedup.py:196-211`]**.
- **Exclusión de cadenas / multi-sucursal ES**: nombres tipo `flexicar/ocasionplus/clicars/carplus/stellantis/…` vetados de merges name-only y geo-only (requieren phone O website). **[VERIFIED `cross_source_dedup.py:163-176`, `build_residual_namemuni_dedup.py:69-72`]**.

### Refinamientos verificados (v2) — `[CORRIGE v1]`

- **UnionFind: la duplicación YA es divergencia activa.** Las 5 copias no son byte-idénticas: hay **dos algoritmos de compresión** — path-halving una-pasada (`cluster_dealers.py:209`, `cross_source_dedup.py:337`) vs **two-pass full compression** (`build_canonical_dedup.py:119-131`, `build_residual_namemuni_dedup.py:92-100`) — y **dos esquemas de atributo** — `_parent/_rank` vs **`_p/_r`** (`build_residual_namemuni_dedup.py:82`). Más una **6.ª** variante semántica: `ConstrainedUnionFind` (`resolve_entities.py:299-380`) que propaga `city_set/org_set`. El riesgo "versión recursiva desborda pila" es **HIPOTÉTICO**: ninguna es recursiva hoy **[VERIFIED]**. Lo real es el drift `_p/_r` y halving↔two-pass. → F1.
- **62, no 41, literales `CDP-ES-`.** **[VERIFIED `grep -rl 'CDP-ES-' --include=*.py --include=*.sql | wc = 62`]**. El **mint ya es genérico** (`mint_code('DE')→CDP-DE-*`, `canonical_key` country-blind **[VERIFIED test_country_coexistence.py:13-16]**); el **VALIDADOR** `complete.py:89` es el blocker, y `[A-Z]{2}` flojo aceptaría `CDP-ZZ-`/`CDP-QQ-` no-ISO. → F3.
- **La clave de nombre del residual YA diverge de B1.** `build_residual_namemuni_dedup.py:75-79` `_norm` **no** aplica strip de sufijo legal (`"autosl"` residual vs `"auto"` B1), y hay una **4.ª** normalización en SQL (`:148` `lower(regexp_replace(...,'[^a-zA-Z0-9]',''))`) sin NFKD ni strip. El supuesto "misma key que B1" es **FALSO** para nombres sufijados. El **DSN del residual sí** tiene override `CARDEEP_DSN` (`:60`) — limpio; el hardcode sin override es de `build_particular_dedup.py:38`. → F4/F15.
- **`build_canonical_dedup` es FATAL pese a documentarse "non-fatal".** Comentario `:95-97` dice "non-fatal DIVERGENCE warning"; código `:455-463` hace `sys.exit(1)`. **[VERIFIED contradicción doc↔código]**. → F13/B18.
- **Etiqueta `rep=MIN(cdp)` obsoleta.** `build_particular_dedup.py` docstring `:14-18` y label dry-run `:118` dicen `rep=MIN(cdp_code)`, pero el código vivo `:109` hace **`most-available-vehicle`** (fix FASE 3, `:104-107`). Trampa para quien onboardea leyendo la invariante equivocada. → F14/F23.
- **Imprecisiones de hint corregidas.** `cluster_dealers` **no tiene `_is_chain`**; el hint "254-258" es el **cursor SQL** de `_load_entities`, no un normalizador. `cross_source_dedup._normalize_phone` ya delega a `phone_match_key(phone)` pero **sin `cc`** en el call-site (`:240`). → F22/F2.

---

## Motor (invariante, reusado byte-idéntico por país)

1. **`UnionFind`** (path-compressed, union-by-rank sobre ULIDs string) — la primitiva determinista de clausura transitiva; **matemática idéntica en todo país** (`cluster_dealers.py:194`). *(Hoy en 5-6 copias divergentes — F1.)*
2. **Topología de bloqueo de 4 aristas**: cada arista se clavija en `(normalized_key, municipality_code)`. `municipality_code` es un **token geo opaco** consumido de la etapa Geo → la estructura de arista ya es country-agnóstica; solo el **normalizador** que produce la clave es locale-specific.
3. **Escalera de selección canónica**: `source_group rank > field richness > first_seen > cdp_code lexicográfico` — orden puramente estructural, sin supuesto ES (`cluster_dealers.py:481-500`).
4. **La CADENA de overlays como arquitectura**: B1 (`entity_cluster`) → deep-link (`canonical_dedup`) → particular (`canonical_key`) → residual (name+muni), cada una corrida vam-gated separada, compuesta por `v_dealer_resolved` vía COALESCE-to-self (`0028`).
5. **Semántica de gate `vam_verified`**: solo la **única** corrida `vam_verified=TRUE` más reciente sirve; entities/canónicos ausentes de una corrida verificada resuelven a sí mismos. Contrato idéntico para cualquier país (**en intención** — hoy es global-único, ver §Veredicto / F17).
6. **Escritura append-only, no destructiva, idempotente** (delete `RUN_ID` luego reinsert); las filas `entity` **NUNCA** se mutan y ningún `cdp_code` se reescribe.
7. **La RED anti-over-merge**: exclusión cross-kind (particular vs dealer), anti-hub `K`, `FUZZY_BLOCK_CAP` + `FUZZY_MIN_NAME_LEN`, cap de tamaño de componente, cap de nombres distintos, richest-is-canonical, elegibilidad bystander-drag, y served==recomputo-SQL-independiente. Todo **estructural/relacional**, no ES-específico (**salvo las constantes calibradas a ES**, ver §Costuras / F19).
8. **Autoridad `cdp_code`/`canonical_key`** (`codes.py`): ya paramétrica — el país vive solo en el prefijo de mint, la pre-imagen hash es country-free → claves dedup estables por tenant.
9. **Axioma de evidencia deep-link**: una URL de listing atribuida a >1 canónico = el mismo dealer físico. Universal en cualquier marketplace de cualquier país.
10. **La gramática de tabla overlay**: `*_run` (params + counts + `vam_verified` + FK al verdict) emparejada con tabla per-member, replicada por cada capa (`0020/0027`) — el molde de esquema reusable.

---

## Pack por país (lo que cada país aporta para esta etapa)

| # | Pieza del pack | Qué es | ES (referencia) |
|---|---|---|---|
| P1 | **Plan de numeración telefónica** | calling code + conjunto/rango de longitudes nacionales válidas + regla de leading-digit → produce la clave E.164 | cc=34, len=9, leading ∈ {6,7,8,9} |
| P2 | **Léxico de sufijos legales** | formas societarias finales a quitar antes de keyear el nombre | `sl/sa/slu/sau/sll/scp/scoop/sociedadlimitada…` (DE: `gmbh/ag/ug/kg/ohg`; FR: `sarl/sas/sa/eurl/sci`; IT: `srl/spa/snc`) |
| P3 | **Lista de cadenas / multi-sucursal** | marcas compartidas por POS físicos distintos que **nunca** deben name-merge | `flexicar/ocasionplus/clicars/carplus/stellantis…` (cada mercado tiene sus consolidadores) |
| P4 | **Autoridad de id fiscal/registral** | qué identificador es la id fuerte de dedup y su token de prefijo | ES: CIF → `cif:`; pan-UE: VAT — alimenta la rama id de `canonical_key` |
| P5 | **Reglas de normalización de dirección** | léxico de tipos de vía por locale para el guard de detección de sucursal | ES: `C/`, `Avda`, `Pza`; DE: `Str.`, `Pl.`; FR: `Rue`, `Av.`, `Bd` — **hoy solo existe un alnum-strip naíf** |
| P6 | **Country code del prefijo cdp** (`CDP-{CC}-`) | ya consumido por `mint_code`; el único lugar donde el literal pertenece | `ES` |

> **NOTA crítica:** `municipality_code` **NO** está en este pack — lo entrega el adaptador de la etapa Geo (INE para ES); identidad solo consume el **código opaco**, manteniendo las aristas geo-agnósticas. La fronteridad del pack acaba en el normalizador.

---

## Costuras ES-hardcoded → fix

| location | issue | fix |
|---|---|---|
| `phone_es.py:20,32-37,49` (módulo entero) | Autoridad cableada a España: `+34`, nacional fijo 9, leading {6,7,8,9}. Sin dispatch de locale. Un teléfono DE/FR/IT devuelve `None` → la **arista phone (señal cross-source muy fuerte) se DROPEA en silencio** para todo país no-ES. | Promover a registro de planes data-driven: `phone_match_key(raw, country_code='ES')` y `normalize_e164(raw, country_code='ES')` despachando a `PHONE_PLANS[cc]=(calling_code, valid_national_lengths, leading_rule)`. La fila ES reproduce hoy byte-idéntico (golden lo clavija); la clave devuelta pasa a **E.164 completo** (`+CC`+nacional) para que un índice pan-UE nunca false-merge transfronterizo. Fallback opcional a la lib `phonenumbers` tras la misma interfaz; default pure-stdlib €0. → F2 |
| `resolve_entities.py:135-146` (usado en `:569`) | Normalizador legacy "últimos 9 dígitos, ≥7" SIN validación de forma española y SIN delegar — exactamente el substring frágil que `phone_es` nació para matar. Latente en la capa beta/fingerprint, pero **false-mergeará** en cuanto esa capa se sirva, y hornea el supuesto ES de 9 dígitos. | Borrar el cuerpo y delegar en `pipeline.identity.phone_es.phone_match_key(phone, country_code)`, exactamente como `cross_source_dedup.py:231-240` ya hace. Autoridad única, sin segunda copia. → F8 |
| `cluster_dealers.py:117-135` + `cross_source_dedup.py:196-211` (sufijos); normalizadores sin param país (`cluster_dealers.py:138/170`, `cross_source_dedup.py:214/231/254`) | Lista de sufijos legales ES y normalizadores name/phone/chain **duplicados** entre módulos y hard-ES sin argumento de país. Un 2º país exige editar ≥2 archivos y arriesga **drift** entre la copia B1 y la cross-source. | Extraer **un** objeto `IdentityLocale(country_code)` que exponga `legal_suffixes`, `chain_tokens`, `normalize_name`, `phone_key`, `normalize_address`. Enhebrar `country_code` (default `'ES'`) en `_normalize_name`/`_normalize_phone`/`_is_chain`; el locale ES devuelve las listas exactas de hoy → hash/aristas byte-idénticos. → F4/F22 |
| `cross_source_dedup.py:163-176` + `build_residual_namemuni_dedup.py:69-72` | Patrones chain/multi-sucursal ES-específicos y duplicados en dos formas divergentes (regex vs tupla de substrings; intersección de solo 5 tokens). Las cadenas de país nuevo son **invisibles** → sus consolidadores over-mergean sucursales. | `IdentityLocale.chain_tokens(country_code)` único, consumido por el guard cross-source y el residual; lista per-country, una sola fuente de verdad. → F6 |
| `complete.py:89` (`_CDP_CODE_RE = ^CDP-ES-…`) + literal `CDP-ES-` esparcido por el repo (**62 archivos [VERIFIED grep=62]**) | El validador de código de entity **hard-asserta el prefijo ES** (el 6º blocker de onboarding G1, xfail-guarded). El mint ya está centralizado (`codes.py:53`) pero callers/validators lo **bypassean**. Una entity de país #2 falla la validación 5-gate. **[VERIFIED `complete.py:89` re-leído]** | Ensanchar a `^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$` (1 línea, quitar el xfail) **validando el cc contra ISO-3166-1 alpha-2 (pycountry)**; enrutar los literales restantes por `codes.mint_code` o un builder `PREFIX` compartido → `CDP-{CC}-` en exactamente un lugar (62→1). → F3 |
| `cluster_dealers.py:59` (`SCOPE_CONDITION`) y `:56` (`RUN_ID`) | B1 carga **TODAS** las entities sin filtro de país y escribe un `RUN_ID` fijo único. Para un país (toda fila ES) va bien; para un 2º **mezcla tenants en una corrida**, elige el normalizador locale equivocado y **impide sellado/rollback limpio por país**. **[VERIFIED `:56`,`:59` re-leídos]** | Añadir `AND country_code = %s` a `SCOPE_CONDITION` y sufijar `RUN_ID` por país (`dealer-identity-det-v1-{cc}`); cargar el `IdentityLocale` de ese cc una vez. `v_canonical` ya sirve la corrida verificada → aditivo. → F9 |
| `cluster_dealers.py:194`, `cross_source_dedup.py:322`, `resolve_entities.py:257`, `build_canonical_dedup.py:107`, `build_residual_namemuni_dedup.py:82` | `UnionFind` **copy-pasteado 5 veces** en la etapa (un 6º en `cluster_vehicles.py`) y **ya divergente** (halving vs two-pass; `_parent/_rank` vs `_p/_r`). Un fix a una (recursión, tie-break) falla silenciosamente las otras. | Extraer `pipeline/identity/union_find.py` (una implementación, two-pass full compression) e importar en todas; comportamiento idéntico → sin drift numérico. → F1 |
| `build_particular_dedup.py:38` (DSN hardcoded, sin override de env) | DSN literal `127.0.0.1:5433` sin fallback a `os.environ` mientras los scripts hermanos usan `os.environ.get('CARDEEP_DSN',…)`. No es costura de país sino de **entorno**: bloquea correr la cadena contra otra DB (la instancia dry-run `:5434`) para un tenant nuevo. | `DSN = os.environ.get('CARDEEP_DSN', '…')` para igualar `build_canonical_dedup.py:82` y `build_residual_namemuni_dedup.py:60`. → F14 |

---

## Diseño genérico A→Z

La etapa de identidad **ya es** un motor country-agnóstico envuelto alrededor de **cuatro autoridades de normalización ES-hardcoded**. La genericidad se logra **extrayendo** esas autoridades a un pack `IdentityLocale` per-country y despachando por `entity.country_code` — **sin reescribir el motor** y **sin re-key ninguna entity ES**.

**ABSTRACCIÓN.** Definir `IdentityLocale(country_code)` como el **único portador de costura**, un value object congelado construido una vez por corrida desde datos declarativos:
- `PhonePlan = (calling_code: str, national_lengths: frozenset[int]|range, leading_rule)` → `phone_key(raw) -> E.164|None` y `national_key(raw) -> str|None`.
- `legal_suffixes: tuple[str,…]` (longest-first) + regex compilada de strip.
- `chain_tokens: tuple[str,…]` + patrones compilados.
- token de `tax_id` (`'cif'` para ES) + validador opcional de forma.
- léxico de dirección (abreviaturas de tipo de vía) para `normalize_address`.

Un `REGISTRY: dict[str, IdentityLocale]` a nivel módulo, keyado por ISO-2, con `get_locale(cc)` que **lanza `KeyError` ruidoso** si el país no está registrado (fail-fast, espeja `config_guard`). ES se registra con **exactamente** las listas de hoy → toda clave producida es byte-idéntica y los suites golden/Ferrari siguen verdes.

**INTERFACES.** Los tres normalizadores del motor ganan argumento de país con default ES para preservar cada call-site: `_normalize_name(name, country_code='ES')`, `_normalize_phone(raw, country_code='ES')` (delega en `get_locale(cc).phone_key`), `_is_chain(name, country_code='ES')`. La superficie pública del módulo de teléfono pasa a `phone_match_key(raw, country_code='ES')` y `normalize_e164(raw, country_code='ES')`; las funciones ES desnudas quedan como wrappers finos `country_code='ES'`. `codes.py` **no cambia** — ya es paramétrico; solo sus **callers hard-ES** (regex de `complete.py`, los 62 literales) se ensanchan a `^CDP-([A-Z]{2})-`.

**ESTRUCTURA DE DATOS.** Ningún cambio de esquema para el núcleo: `entity.country_code` (`0052`) ya existe e indexa. El único cambio estructural es **RUN SCOPING** — la query de carga de B1 gana `AND country_code = %s` y el run id se sufija por país (`dealer-identity-det-v1-{cc}`); los run ids de la cadena dedup igual. `v_canonical` y `v_dealer_resolved` ya seleccionan "la corrida `vam_verified` más reciente" y resuelven vía COALESCE-to-self → **deben pasar a filtrar por `country_code`** (ver §Veredicto SH1 / F17) para servir transparente una DB multi-país donde cada país tiene su propia corrida verificada; entities de un país sin corrida verificada resuelven a sí mismas (degradación elegante, nunca errónea).

**POR QUÉ LAS ARISTAS SIGUEN COUNTRY-AGNÓSTICAS.** Aristas 1/2/3 son buckets `(normalized_key, municipality_code)`; `municipality_code` es token opaco minteado por el adaptador per-country de **Geo** (INE para ES, otra autoridad para DE) → identidad nunca embebe un supuesto geo, solo bloquea con el código que Geo le dio. Arista 4 (levenshtein sobre `normalized_name`) es métrica de string, neutra al idioma. La arista phone es la **única** que carga un supuesto locale, y ese supuesto ahora vive entero dentro de `PhonePlan`. Como todo match es **muni-bloqueado** y la clave phone genérica es **E.164 completo** (CC-prefijada), dos países no pueden false-merge ni en DB compartida: sus muni-codes difieren **Y** sus claves E.164 difieren por calling code. **(Pre-condición: el muni-code debe ser country-namespaced — ver §Veredicto B2 / F10.)**

**E.164 GENÉRICO.** La tabla de planes es la generalización €0 pure-stdlib de `phone_es`: quitar no-dígitos, quitar prefijo internacional/troncal del país, validar longitud nacional contra el set del plan y la regla de leading, re-emitir como `+{cc}{national}`. Para mercados de plan irregular la misma interfaz delega opcionalmente en la lib gratis `phonenumbers`, pero el camino default no necesita dependencia y es exhaustivamente unit-testeable offline por país (un golden por locale, espejando `test_phone_es.py`). La **clave** para indexado cross-source/pan-UE es el E.164 completo.

**COMPOSICIÓN / DEGRADACIÓN.** La cadena de cuatro capas compone por país exactamente como para ES. La red anti-over-merge se reusa **verbatim** porque cada guard es estructural: cross-kind, anti-hub `K`, fuzzy caps, component/name caps, richest-rep, bystander-drag, y served==recomputo-independiente. Las **constantes** (size≤30, names≤12) son censo-estadísticas, no ES-legales → un país nuevo **re-clavija** `KNOWN_REAL_MAX_*` desde su primera corrida sellada pero mantiene la **forma** del guard. Resultado neto: onboarding de un país en esta etapa = **una fila `IdentityLocale` + un golden de teléfono + correr los mismos cinco scripts country-scoped**; el motor, esquema, vistas, gating y red de regresión se tocan cero veces (una vez aplicados los fixes estructurales de §Veredicto, que son **one-time** no per-country).

---

## Onboarding de país nuevo (pasos de biblia para esta etapa)

1. **Registrar el locale**: añadir `IdentityLocale('XX')` al registry con (a) `PhonePlan(calling_code, national_lengths, leading_rule)`, (b) `legal_suffixes` longest-first, (c) `chain_tokens` (consolidadores multi-sucursal del país), (d) token `tax_id` + check opcional de forma, (e) léxico de tipos de vía. Datos declarativos puros, €0. → F22
2. **Escribir el golden de teléfono** `tests/test_phone_<xx>.py` espejando `test_phone_es.py`: válido→E.164 y malformado→None exhaustivos (extensión, longitud errónea, leading inválido, CC extranjero). RED antes de la fila del plan, GREEN después. → F2
3. **Ensanchar el validador de código UNA vez** (compartido, no per-country): `complete.py:89` → `^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$`, quitar su xfail, validar cc ∈ ISO-3166-1; confirmar que los 62 literales `CDP-ES-` se enrutan por `codes.mint_code`. Fix de genericidad one-time. → F3
4. **Asegurar que Geo selló** el espacio de `municipality_code` del país (el token de bloqueo opaco, **country-namespaced**) y que las entities ingeridas portan `country_code='XX'` y `municipality_code` poblado — identidad bloquea sobre él. → F10 / MP8
5. **Correr B1 country-scoped**: `cluster_dealers` con `SCOPE_CONDITION += country_code='XX'` y `RUN_ID='dealer-identity-det-v1-xx'`; construye `entity_cluster_run`/`entity_cluster` usando `get_locale('XX')`. → F9
6. **Correr la capa deep-link**: `build_canonical_dedup` country-scoped (run id sufijado), **re-clavijando** sus `EXPECTED_*` desde la primera build limpia de este país (los asserts son censo-sensibles, no ES-congelados) — ver §Veredicto B18 / F13.
7. **Correr particular y residual** (`build_particular_dedup`, `build_residual_namemuni_dedup`) country-scoped, usando `get_locale('XX').chain_tokens` en el guard residual; mantener INERTE (`vam_verified=FALSE`) hasta verificar. → F14/F15
8. **Verificar con la red anti-over-merge**: correr `test_dedup_invariants` contra la corrida servida del país (auto-ancla a la última `vam_verified`), re-clavijando `KNOWN_REAL_MAX_*` desde los máximos reales del país; confirmar 0 cross-kind, size≤cap, names≤cap, 0 richer-than-rep, served==recomputo, **y 0 componentes multi-country**. → F19
9. **2ª pasada adversarial** de los componentes mayores y cualquier grupo `excluded_ambiguous`, luego gatear `vam_verified=TRUE` en la corrida de la cadena (un flip deliberado). `v_dealer_resolved` sirve el país XX con ES intacto. → F17
10. **Registrar un CI fail-fast**: todo `country_code` presente en `entity` debe tener un `IdentityLocale` registrado y todo `source_key` clasificado (sin fallback silencioso a la normalización ES ni no-op de B6.1 para datos extranjeros). → F22/F12

---

## Sellado + verificación multi-vía + rollback

**SELLADO** (identidad, **por país**) significa TODO esto a la vez:
1. Existe **una** `canonical_dedup_run` con `vam_verified=TRUE` para el país y `v_dealer_resolved` la sirve.
2. Las filas `entity` están **sin mutar** y cada `cdp_code` original sobrevive (el overlay es el único sitio donde se resuelve identidad).
3. La red anti-over-merge pasa contra esa corrida servida: 0 componentes cross-kind, `component_size ≤ MAX_COMPONENT_SIZE_CAP`, trade-names distintos por componente `≤ MAX_DISTINCT_NAMES_CAP`, 0 no-reps groseramente más ricos que su rep, el conteo de dealers `kind<>'particular'` servido **igual** a un recomputo independiente, **y 0 componentes super-canónicas multi-country** (invariante nuevo F19).
4. La cadena solo **engruesa** (coarsen), nunca deshace un merge B1/deep-link (`test_dedup_invariants.py:406`).

El conteo sellado se reporta como **cardinalidad certificada con su snapshot de build-time**, jamás como entero eterno (el censo crece).

**2ª VÍA ORTOGONAL.** Los scripts de build assertan sus **propios** conteos (`build_canonical_dedup.py:441-463`), pero la verificación es por **camino independiente**: `test_dedup_invariants.py` recomputa la matemática de over-merge en SQL crudo directo contra `canonical_dedup`/`canonical_dedup_run`/`v_dealer_resolved`, **bypaseando el build** e incluso bypaseando `v_dealer_resolved` para el cross-check de conteo servido (re-deriva b1→dedup a mano y asserta igualdad a la vista, `:374-394`). Dos caminos disjuntos (build Python vs auditoría SQL) deben coincidir a la fila. La autoridad de teléfono se clavija por golden (`test_phone_es` / espejo per-country) **Y** un test de paridad-legacy (`test_cross_source_phone.py:23`). **Pre-condición de genericidad:** el SQL de auditoría **debe ganar `WHERE country_code`** (ver §Veredicto SH2 / F19) para que la ortogonalidad valga país-a-país.

**ROLLBACK.** Cada capa es overlay no destructivo, append-only. Para revertir el sello de un país: flip `vam_verified=FALSE` (o `DELETE` de la corrida CASCADE) — el COALESCE-to-self de `v_dealer_resolved` cae instantáneo a la corrida verificada previa, o al `cdp_code` crudo si no hay, con filas `entity` intactas (`0028` latest_run CTE devuelve 0 filas → NULLs → B1/self). El builder residual además **snapshotea** `canonical_dedup` antes de escribir (`build_residual_namemuni_dedup.py:360-366`) para restore byte-exacto. Como las corridas son **per-país** (run-id sufijado), revertir XX no perturba la corrida sellada ES **(condicionado a que el run scoping y el filtro de vistas estén aplicados — hoy NO lo están, ver §Veredicto SH1 / F17/F24)**.

---

## Veredicto adversarial: roturas → resolución

> Cobertura exhaustiva: **19 breaks (B1–B19) + 10 missing_pack (MP1–MP10) + 8 sealing_holes (SH1–SH8)**. Ninguna se oculta. Cada una lleva su resolución de diseño o se marca **OPEN ITEM** con causa y gating. La columna **F#** liga cada rotura a su sub-proyecto-360 (donde se baja al átomo).

### Roturas CRÍTICAS de espina dorsal (country-blindness)

| ID | País | Rotura (verificada) | Severidad | Resolución | F# |
|---|---|---|---|---|---|
| **B1** | TODOS | **SPINE BREAK**: `country_code` en esquema y prefijo `cdp_code` pero en **ningún sitio** de `pipeline/identity` (**[VERIFIED grep → 0]**). `_load_entities` sin filtro de país, **un** `RUN_ID` global (`cluster_dealers.py:56,253`). `v_canonical`/`v_dealer_resolved` sirven la **única** corrida global. País #2 **re-clusteriza/sobrescribe** la corrida de ES; comparten gate. | CRITICAL | **CIERRA** (one-time): `SCOPE_CONDITION += AND country_code=%s` + `RUN_ID` sufijado; vistas filtran `country_code`. ES byte-idéntico. **Bloquea todo onboarding.** | F9·F17 |
| **B2** | TODOS | Clave de bloqueo `(norm_name, municipality_code)` (`cluster_dealers.py:410-430`) puede **false-merge transfronterizo**: `0053:4` prueba colisión de provincias en códigos de 2 dígitos, y `entity.municipality_code` no porta país. Ningún test asserta componente single-country. | CRITICAL | **CIERRA** por doble defensa: run scoping per-país + clave phone E.164 CC-prefijada + muni-code country-namespaced (MP8). Más invariante single-country (MP10/SH6). | F10·F19 |
| **SH1** | TODOS | Sello = **flag `vam_verified` GLOBAL**: `test_dedup_invariants.py:117-126` toma la única última `vam_verified` de **todos** los países; asserta exactamente una global. Sellar país #2 voltea el switch de ES. | CRITICAL | **CIERRA**: vistas y `_served_run()` ganan `country_code`; unicidad pasa a **"una corrida servida por país"**. | F17·F19 |

### Roturas de la autoridad de teléfono (el pack más load-bearing)

| ID | País | Rotura (verificada) | Severidad | Resolución | F# |
|---|---|---|---|---|---|
| **B3** | DE | `phone_es` rechaza **todo** número alemán (`_VALID_LEADING={6,7,8,9}` + nacional fijo 9, `phone_es.py:20,36`); `+49` no stripeado → **0 aristas phone** (clave cross-source más fuerte) para DE. | CRITICAL | **CIERRA**: `PHONE_PLANS['DE']`; clave = E.164 completo; golden DE. | F2 |
| **B8** | FR | `phone_es` **MIS-VALIDA en silencio**: móvil FR 06/07/09 (9 díg, leading ∈{6,7,8,9}) se **acepta como español** → FR y ES con mismos 9 dígitos comparten clave (merge cross-country). **Wrong-accept es peor que rechazo.** | CRITICAL | **CIERRA**: clave E.164 (`+33…`≠`+34…`) hace imposible la colisión. | F2 |
| **B10** | IT | `phone_es` rechaza italianos en bloque (0 inicial en fijos, longitud variable, `+39` no stripeado). Aristas phone = 0 para IT. | CRITICAL | **CIERRA**: `PHONE_PLANS['IT']` leading-0 + longitudes variables; golden IT. | F2 |
| **B12** | PT | `phone_es` acepta móviles PT de 9 díg como ES, dropea fijos PT y falla `00351…`. | HIGH | **CIERRA**: `PHONE_PLANS['PT']`; clave `+351…`≠`+34…`. | F2 |
| **B14** | MX | `phone_es` rechaza todos los mexicanos (10 díg, `+52`). Clave phone muerta. | CRITICAL | **CIERRA**: `PHONE_PLANS['MX']`; golden MX. | F2 |
| **B17**(phone) | JP | `phone_es` rechaza japoneses (trunk-0, `+81`, longitud variable). | HIGH | **CIERRA** (faceta phone): `PHONE_PLANS['JP']`. | F2 |

### Roturas de léxico (sufijos legales y cadenas)

| ID | País | Rotura (verificada) | Sev. | Resolución | F# |
|---|---|---|---|---|---|
| **B5** | DE | Léxico ES-only (`cluster_dealers.py:117-128`): `gmbh/ag/ug/kg/ohg/e.k.` no se quitan → under-merge sistemático DE. | HIGH | **CIERRA**: `IdentityLocale('DE').legal_suffixes`. | F4 |
| **B6** | DE | Cadenas DE (`Auto1/Sixt/Emil Frey…`) ausentes de `_CHAIN_PATTERNS`/`CHAIN_TOKENS` → sucursales **OVER-MERGE**. | HIGH | **CIERRA**: `IdentityLocale('DE').chain_tokens`, fuente única. | F6 |
| **B9** | FR | `sarl/sas/sasu/eurl/sci` ausentes → under-merge; `sa` puede sobre-clipear palabras FR. | HIGH | **CIERRA**: `IdentityLocale('FR').legal_suffixes`. | F4 |
| **B11** | IT | `srl/spa/snc/sas/sapa` ausentes → under-merge IT. | HIGH | **CIERRA**: `IdentityLocale('IT').legal_suffixes`. | F4 |
| **B13** | PT | `lda/unipessoal` no stripeadas → under-merge PT. | MEDIUM | **CIERRA**: `IdentityLocale('PT').legal_suffixes`. | F4 |
| **B17**(sfx) | JP | K.K./G.K. sin manejar (faceta no-phone de B17). | HIGH | **CIERRA parcial**: `IdentityLocale('JP').legal_suffixes`; script → B16/F5. | F4·F5 |

### Roturas de script / Unicode (folding ASCII destructivo)

| ID | País | Rotura (verificada) | Sev. | Resolución | F# |
|---|---|---|---|---|---|
| **B7** | DE | `NFKD+encode('ascii','ignore')` (`cluster_dealers.py:154-156`, `codes.py:30-31`) dropea eszett/diacríticos: "Straße"→"strae" → under-merge. **[VERIFIED `codes.py:30-31`]** | MEDIUM | **CIERRA**: transliteración por locale (anyascii) en `normalize_name`. ES byte-idéntico. | F5 |
| **B16** | JP | **OVER-MERGE EN MINT-TIME**: `codes._normalize` NFKD+ascii-ignore → kanji foldea a `''`, y `codes.canonical_key` (`:92-94`) igual devuelve `name:|{muni}` → **TODO** dealer JP de un muni colapsa a **UN** `cdp_code` en insert-time. A la inversa, `cluster_dealers._normalize_name` → `None` (under-merge). **[VERIFIED `codes.py:30-31,92-94`]** | CRITICAL | **CIERRA**: (1) normalizador transliterante por locale; (2) **empty-name guard en `codes.canonical_key`** → `raise ValueError`. **Gating: pre-requisito de cualquier país no-latino.** | F5·F7 |

### Roturas de taxonomía de fuentes y registral

| ID | País | Rotura (verificada) | Sev. | Resolución | F# |
|---|---|---|---|---|---|
| **B4** | DE | Taxonomía ES-only: `mobile.de` desconocido → `_is_orthogonal` (`:417-430`) nunca se satisface → **B6.1 es no-op silencioso** para DE. | CRITICAL | **CIERRA** vía MP1: taxonomía source-keys = pieza de pack per-país. | F11·F12 |
| **B15** | MX | Plataformas MX desconocidas a `_PARTICULAR_PLAT` y a los source sets → particulares sin `canonical_key` Y B6.1 no-op. "S.A. DE C.V."→"sadecv" pegado. | CRITICAL | **CIERRA** vía MP1 (taxonomía MX) + P2 (sufijo multi-word). | F12·F14·F4 |
| **B18** | TODOS | `build_canonical_dedup.py:98-101` hardcodea censo ES y lo asserta con **`sys.exit(1)`** (`:447-463`). El docstring (`:95-96`) afirma "non-fatal" pero **el código es FATAL** **[VERIFIED contradicción]**. Cualquier fila no-ES diverge → `sys.exit(1)` → sellado aborta. | HIGH | **CIERRA**: expectativas country-keyed + honrar el docstring (warn+re-verify, no `sys.exit(1)`); `--force` tras flag. **Se corrige el código a lo que el doc promete.** | F13 |
| **B19** | TODOS | `entity.cif` (`0002:11`) único campo registral; `alias_kind` cerrado a `('name','domain','cif','phone')` (`0002:57`); `canonical_key` namespacea `'cif:'` SIN validar (`codes.py:88-89`). DE/FR/IT/PT/MX/JP tienen formatos distintos y a menudo 2 ids. | MEDIUM | **CIERRA** vía MP3 (migración aditiva): `registral_id` + `id_scheme` + ensanchar enum; token `{scheme}:{value}`. ES `cif:` preservado. | F20 |

### Pack faltante (MP)

| ID | Pieza faltante | Resolución | F# |
|---|---|---|---|
| **MP1** | Taxonomía de source-keys por país (`GEO/DIGITAL/PHONE/WEBSITE_SOURCES` + `_PARTICULAR_PLAT`). Sin ella la B6.1 es no-op. | **CIERRA**: pieza del pack, poblada en onboarding. | F12 |
| **MP2** | Clave phone country-NAMESPACED (E.164 `+CC…`). | **CIERRA**: clave = E.164 completo. | F2 |
| **MP3** | Esquema registral/fiscal + extensión del enum `alias_kind`. | **CIERRA**: migración aditiva (B19). | F20 |
| **MP4** | Política de script/transliteración + empty-name guard. | **CIERRA**: tabla de transliteración + guard. | F5·F7 |
| **MP5** | Namespace de `RUN_ID` per-país + gate servido per-país. | **CIERRA**: run-id sufijado + filtro de vista. | F9·F17·F24 |
| **MP6** | Constantes de over-merge per-país (`MAX_*` + cota "<52"). | **CIERRA**: seal manifest country-parametrizado. | F19 |
| **MP7** | Reemplazo de asserts de censo ES `sys.exit(1)`. | **CIERRA**: idéntico a B18. | F13 |
| **MP8** | Contrato del adaptador geo: muni-code country-namespaced y self-describing. | **CIERRA**: contrato con Geo-6. **Cross-etapa.** | F10 |
| **MP9** | Nombre legal multi-palabra + precedencia trade vs legal. | **CIERRA**: `legal_suffixes` multi-palabra longest-first. | F4 |
| **MP10** | Invariante single-country en el suite del pack. | **CIERRA**: test `0 componentes con >1 country_code`. | F19 |

### Agujeros de sellado (SH)

| ID | Agujero (verificado) | Resolución | F# |
|---|---|---|---|
| **SH1** | Sello = flag `vam_verified` GLOBAL único. | **CIERRA**: per-país (B1/SH1). | F17 |
| **SH2** | Guards over-merge country-BLIND (sin `WHERE country_code`). | **CIERRA**: cada query gana `WHERE country_code`; caps desde manifest. | F19 |
| **SH3** | Cap-meaningfulness clava `< 52` (provincias ES). | **CIERRA**: parametrizar desde seal manifest per-país. | F19 |
| **SH4** | `served==recompute` es entero global sin split de país. | **CIERRA**: per-país + intervalo certificado. | F19 |
| **SH5** | Deep-link **aborta** (`sys.exit(1)` en divergencia). | **CIERRA**: idéntico a B18. | F13 |
| **SH6** | FALTA invariante single-country super-canónico. | **CIERRA**: idéntico a MP10. | F19 |
| **SH7** | Sello de clave phone ES-exhaustivo solo. | **CIERRA**: golden phone per-país + clave E.164. | F2·F8 |
| **SH8** | `resolve_entities._load_ine_municipalities` (`:245`) sin filtro de país + ASCII-fold → city-guard mezcla munis de todos los países, ciego a JP. | **CIERRA**: `WHERE country_code=%s` + normalizador transliterante. **Capa beta — cerrar ANTES de gatear.** | F8 |

### OPEN ITEMS reales (no cierran solo por diseño)

- **OI-1 · Re-verificación contra DB viva.** Stack **CAÍDO** al auditar (PG `:5433` cerrado). Todo conteo (incl. `EXPECTED_DEDUPED_COUNT=54489`) es punto-en-el-tiempo. **Gating:** el sello per-país se re-verifica contra DB corriendo. Causa: infra apagada.
- **OI-2 · Adjudicador capa-2 (LLM local) para `excluded_ambiguous`.** Hoy capa-2 = 0 en código. **Gating:** GASTO/GPU (€>0) + caso probado + firma. €0 solo en hardware existente. Causa: palanca de coste.
- **OI-3 · MP8 contrato geo cross-etapa.** Depende de la etapa **Geo (6)**; se cierra en conjunto. Causa: dependencia inter-etapa.

---

## Sub-proyectos institucionales (360 por faceta)

> **Qué es esta sección.** La etapa de identidad descompuesta en sus **24 átomos de código** (F1–F24), cada uno tratado como un proyecto institucional independiente con su **deep-spec verificado** (mecanismo al átomo) + **costura** ES→genérico + **fix** exacto + **adversarial** concreto + **sellado** multi-vía + **herramienta NEXT-LEVEL €0**. Es el mismo sistema que el §Veredicto, visto por **autoridad-de-código** en vez de por **síntoma**: las 37 roturas (B/MP/SH) viven distribuidas en estas 24 facetas (columna `F#` del veredicto, y la línea `↳ Veredicto` de cada faceta cierran el mapa en ambos sentidos).
>
> **Cómo leerla (funnel).** Cada faceta es autocontenida: salta por la [tabla de familias](#navegación-funnel), lee su `↳ Veredicto`/`Cross-ref` para situarla, y baja al deep-spec. Todo `path:linea` es `[VERIFIED]` leído de la fuente; los `[ASSUMED]` y open-items se marcan con su causa. **Honestidad cruda: nada se transcribe como sano si el código dice lo contrario** (los cinco `[CORRIGE v1]` del banner nacen aquí).

---

### Familia A · Primitiva del motor

---

#### F1 UnionFind primitiva de cierre transitivo unificada

> **Una línea:** la primitiva de clausura transitiva más load-bearing, hoy en **5-6 copias que ya divergen** en algoritmo y nombres de atributo.
> **↳ Veredicto:** Mejora 1 + costura `UnionFind`. **Familia:** A. **Cross-ref:** alimenta F9·F10·F11·F13·F14·F15·F18; `ConstrainedUnionFind` → F8.

**Deep-spec (al átomo, verificado).** `union(a,b)`: `ra,rb=find(a),find(b)`; si iguales return; union-by-rank con **tie-break uniforme `ra` gana en empate** — observable: fija qué nodo queda root (= representante que puntúa `_select_canonical`). Dado el MISMO orden de `union()`, el root es determinista. `find(x)` difiere entre copias: **path-halving una-pasada** `self._parent[x]=self._parent[self._parent[x]]` **[VERIFIED `cluster_dealers.py:194-228` (`:209`), `cross_source_dedup.py:322-355` (`:337`, comentario `:318` "identical to cluster_dealers")]** vs **two-pass full compression** (bucle 1 halla root, bucle 2 re-apunta) **[VERIFIED `build_canonical_dedup.py:107-148` (`:119-131`), `build_residual_namemuni_dedup.py:82-116` (`:92-100`)]**. Ambas producen el mismo `components()`. Dos divergencias REALES hoy: (1) **`_p`/`_r` en `build_residual` vs `_parent`/`_rank`** en el resto **[VERIFIED `:82`]** — un parche al patrón `_parent` **NO toca** build_residual; (2) **6.ª variante semántica** `ConstrainedUnionFind` que propaga `city_set`/`org_set` y rechaza uniones cross-ciudad **[VERIFIED `resolve_entities.py:299-380`]**. `[CORRIGE v1]` ninguna es recursiva → el riesgo "desborda pila" es **HIPOTÉTICO**, no el código de hoy. **No hay lógica ES**: la costura es DRY pura.

**Costura.** 5-6 copias que pueden driftar independientes (ya lo hacen en compresión y nombres). El movimiento genérico no es ES→XX sino **extracción a `pipeline/identity/union_find.py`** importado por todos, eliminando drift `_p`/`_r` y halving↔two-pass.

**Fix.** Crear `pipeline/identity/union_find.py` con UNA `UnionFind` (elegir **two-pass full compression**: amortización mejor, la usan los 2 scripts de componentes mayores). Reemplazar las 5 defs in-line por `from pipeline.identity.union_find import UnionFind`. `ConstrainedUnionFind` subclasea/compone `find/union` compartidos manteniendo su semántica `city_set/org_set`. **Preservar el orden de `union()`**. Golden de equivalencia (Hypothesis): `components()` idéntico old-vs-new en los 5 sitios.

**Adversarial.** Drift real: parche de tie-break a las `_parent/_rank` **salta** `build_residual` (`_p/_r`) → el clustering del Layer-4 se separa del de B1 en silencio. Escala multi-tenant: componente de decenas de miles; un futuro rewrite recursivo ingenuo desborda pila → la consolidación debe blindar iterative-only con test de cadena 100k. Orden: alterar el orden de `union()` cambia el root en empates de rango → cambia el `cdp_code` representante servido.

**Sellado (multi-vía).** (1) **Hypothesis**: `components(old)==components(new)` normalizado-por-root, byte-idéntico, en los 5 call sites para edge-sets aleatorios. (2) **CI grep**: 0 `class UnionFind` in-line restantes. (3) **Stack test**: cadena de 100k nodos sin `RecursionError` (iterative-only). (4) **Re-run** B1 + 4 capas → `v_canonical`/`v_dealer_resolved` cardinalidad byte-idéntica. (5) **pyJedAI** clustering independiente concuerda en componentes (2-vía).

**Herramienta NEXT-LEVEL (€0).** **pyJedAI** (Apache-2.0) https://github.com/AI-team-UoA/pyJedAI **[VERIFIED NEXT-LEVEL.md:546]** — oráculo de clustering independiente para el golden de equivalencia 2-vía. **Hypothesis** (MPL-2.0) https://github.com/HypothesisWorks/hypothesis **[VERIFIED NEXT-LEVEL.md:38/:320]** — fuzzing property-based de la equivalencia. (Splink MIT `:450` es el reemplazo APRENDIDO posterior — cambia a semántica probabilística, fuera del alcance byte-idéntico.)

---

### Familia B · Pack de normalización (autoridades locale)

---

#### F2 Autoridad telefonica E164 generica por plan de numeracion

> **Una línea:** la única fábrica de la señal cross-source más fuerte (`PROB_PHONE=0.97`), hoy cableada a ES y emitiendo clave **sin namespace de país**.
> **↳ Veredicto:** B3·B8·B10·B12·B14·B17(phone)·MP2·SH7. **Familia:** B. **Cross-ref:** consumida por F11; segunda copia frágil en F8; dispatch por F22.

**Deep-spec (al átomo, verificado).** `_national(raw)`: (1) `digits` = solo dígitos; (2) strip de prefijo internacional **único** (`startswith('0034')→[4:]` / `len==11 and startswith('34')→[2:]`); (3) `len==9 and digits[0] ∈ {6,7,8,9}` → 9 dígitos, else `None` **[VERIFIED `phone_es.py:23-38`, `:20` `_VALID_LEADING=frozenset("6789")`]**. `phone_match_key(raw)→_national` (9 díg o None) **[VERIFIED `:41-43`]**; `normalize_es_phone→f"+34{national}"` **[VERIFIED `:46-49`]**. Consumidor único `cross_source_dedup.py:91/231-240` (delega, key STRICT-SUBSET de la vieja last-9). **La key emitida es el nacional desnudo (9 díg), SIN calling-code** → correcta dentro de ES pero **ciega a la frontera**: cualquier número extranjero en forma nacional-desnuda de 9 díg con lead 6/7/8/9 produce la MISMA key que un ES real → colisión de key = arista phone = **falso merge** en union-find. Raíz: la key carece de **namespace de país**; validar la forma ES no basta.

**Costura.** Promover a `phone_match_key(raw, cc='ES')` / `normalize_e164(raw, cc='ES')` respaldado por `PHONE_PLANS[cc]=(calling_code, national_lengths, leading_rule)`; la key SERVIDA pasa a **E.164 COMPLETA** (`+CC`+national). ES reproduce byte-idéntico (golden `test_phone_es.py` lo fija), `phone_es` queda como fast-path ES tras la nueva firma.

**Fix.** (1) Añadir `cc='ES'` sin romper el único call-site. (2) Match-key servida = `f"+{calling_code}{national}"` → `+33…`≠`+34…` por construcción. (3) ES: `_national` puro-stdlib como ruta rápida. (4) No-ES: autoridad genérica. (5) Anclar strip/longitud por `PHONE_PLANS[cc]`. **El índice cross-source migra a E.164-completa atómicamente** (un solo run, no parcial).

**Adversarial.** FR/PT (**false-accept silencioso**, peor que rechazo): móvil FR `6XXXXXXXX` / PT `9XXXXXXXX` desnudos = 9 díg lead ∈{6,7,8,9} → ACEPTADOS como ES → colisión con ES real **[VERIFIED `:36` sin discriminación de país]**. DE/IT/MX/JP (**rechazo total**): `+49/+39/+52/+81` no stripeados → `len!=9` → None → 0 aristas phone → recall de la señal más fuerte cae a CERO. Ruido: número de 9 díg casuales con lead 6/7/8/9 mintea key ES espuria.

**Sellado (multi-vía).** (1) **Paridad ES**: nueva key superset estricto de `phone_es` (extiende `test_cross_source_phone.py:23`); cero re-key de aristas ES. (2) **Golden por país** auto-generado tomando como **oráculo las example-number tables de la librería upstream** (mecanismo distinto a nuestra lógica). (3) **Invariante anti-colisión**: dos calling-codes distintos JAMÁS comparten key (`+33…`≠`+34…`). Pares sintéticos (ES,FR),(ES,PT),(ES,IT).

**Herramienta NEXT-LEVEL (€0).** **python-phonenumbers** (port de Google libphonenumber, Apache-2.0) https://github.com/daviddrysdale/python-phonenumbers **[VERIFIED NEXT-LEVEL.md:466]** — metadata VALIDADA de ~250 regiones + `is_valid_number` como gate de basura cross-border; mata el false-accept FR/PT y los rechazos DE/IT/MX/JP en UNA dependencia, pure-Python offline €0. Envolver tras `phone_match_key(raw, cc)`, ES byte-idéntico (`:467-468`).

---

#### F4 Autoridad de normalizacion de nombre y lexico de sufijos legales

> **Una línea:** el léxico de 10 formas societarias ES y el fold de nombre, **duplicados en 2-3 copias ya divergentes**.
> **↳ Veredicto:** B5·B9·B11·B13·B17(sfx)·MP9. **Familia:** B. **Cross-ref:** fold compartido con F5; drift residual con F15; dispatch por F22.

**Deep-spec (al átomo, verificado).** `_LEGAL_SUFFIXES` = 10 formas **longest-first** (`sociedadlimitadaunipersonal…sl, sa`) **[VERIFIED `cluster_dealers.py:117-128`]**; regex anclada al final `(…)$` **[VERIFIED `:130-132`]**; guard `_MIN_NAME_LEN_AFTER_STRIP=3` **[VERIFIED `:135`]**. `_normalize_name`: NFKD → `encode('ascii','ignore')` → lower → strip `[^a-z0-9]` → strip de ≤1 sufijo iff remanente ≥3 **[VERIFIED `:138-167`]**. El **orden longest-first es load-bearing**: `sociedadlimitada` antes que `sl/sa` o solo recortaría el `sa` final. **DUPLICADO byte-idéntico** en cross-source **[VERIFIED `:196-228`]**. `[CORRIGE v1]` **TERCERA copia divergente REAL**: el `_norm` del residual **NO** aplica strip de sufijo **[VERIFIED `build_residual_namemuni_dedup.py:75-79`]** → `"autosl"` (residual) vs `"auto"` (B1) para todo nombre sufijado → el supuesto "misma key que B1" de F15 es **FALSO**.

**Costura.** Promover `_LEGAL_SUFFIXES`+regex a `IdentityLocale.legal_suffixes(cc)` (longest-first) en UN módulo, consumido por B1, cross-source (mata el dup `:196-228`) Y el residual (que **además adopta el strip**, cerrando su divergencia). Por país: DE `gmbh/ag/ug/kg/ohg/mbh/gmbhcokg`; FR `sarl/sas/sasu/eurl/sci`; IT `srl/spa/snc/sas/srls`; PT `lda/unipessoallda`; MX `sadecv`.

**Fix.** (1) `pipeline/identity/identity_locale.py` con `LEGAL_SUFFIXES: dict[cc,tuple]` + `legal_suffix_re(cc)`; ES registra la tupla EXACTA de 10 → hash byte-idéntico. (2) Reemplazar las 3 defs por import único; el residual adopta el strip. (3) Anclar al final (ya `$`) + conservar min-3. (4) Thread `country_code='ES'` por `_normalize_name(name, cc)` sin romper call-sites.

**Adversarial.** DE: `'Mueller Automobile GmbH'`→`gmbh` no en lista ES → key ≠ su gemelo sin sufijo → **sub-merge sistemático** de cada GmbH. FR: token ES `'sa'` **sobre-recorta** palabras FR (`'Garage Vosa'`→`'garagevo'`) → corrompe token real, riesgo false-merge. IT `'srl'/'spa'`, PT `'lda'` no recortados → sub-merge. MX `'S.A. DE C.V.'`→`'sadecv'` pegado → core permanentemente erróneo. **DRIFT YA VIVO**: el `_norm` residual sin strip rompe la igualdad de clave que el Layer-4 asume.

**Sellado (multi-vía).** (1) **Golden byte-identidad** ES: corpus por el normalizador locale-dispatched == salida actual char-for-char (cdp goldens + Ferrari verdes, cero re-key). (2) **Assert de fuente única**: test que verifica que B1, cross-source y residual referencian el MISMO objeto (drift estructuralmente imposible). (3) **Golden por país** DE/FR/IT/PT/MX (con-sufijo vs sin-sufijo → keys idénticas; FR `vosa`/MX `sadecv` aseveran no-sobre-recorte/strip correcto). (4) **Property test** (Hypothesis): strip idempotente, nunca vacía por debajo de min-3.

**Herramienta NEXT-LEVEL (€0).** **LaBSE / BGE-M3 embeddings** (multilingual semantic blocking, Apache-2.0) https://huggingface.co/sentence-transformers/LaBSE **[VERIFIED NEXT-LEVEL.md:455-461]** — recupera `Mueller Automobile GmbH ~ Mueller Autos` por **significado** antes de que exista el normalizador del país; **complementa** (no reemplaza) el léxico determinista (piso €0 byte-idéntico), ensancha recall capa-2; los guards muni+single-country siguen decidiendo el merge. Alternativa: **Splink** **[VERIFIED `:447-453`]** aprende los pesos de comparación de nombre desde el dato.

---

#### F5 Politica de script y transliteracion Unicode con guardia de nombre vacio

> **Una línea:** el fold `NFKD+ascii-ignore` rompe en **dos direcciones opuestas** fuera de Latin-1, y es el **único fallo que corrompe la clave INMUTABLE** (cdp_code) en mint-time.
> **↳ Veredicto:** B7·B16·MP4. **Familia:** B. **Cross-ref:** aterriza en el mint F7; 4.º fold en F15; city-guard en F8.

**Deep-spec (al átomo, verificado).** El fold vive en **4 sitios**: `codes._normalize` `NFKD→encode('ascii','ignore')→re.sub('[^a-z0-9]+','')` **[VERIFIED `codes.py:29-32`]**; `cluster_dealers._normalize_name` **[VERIFIED `:154-156`]**; `build_residual._norm` **[VERIFIED `:75-79`]**; y `[CORRIGE v1]` un **4.º fold en SQL** `lower(regexp_replace(coalesce(trade_name,legal_name),'[^a-zA-Z0-9]','','g'))` **[VERIFIED `build_residual_namemuni_dedup.py:148`]** que también aniquila no-ASCII. **Dos roturas opuestas del MISMO fold:** (1) **colapso-a-vacío**: `"トヨタ"`→`encode('ascii','ignore')`→`""`; y `codes.canonical_key` **NO tiene guardia** — emite literalmente `name:|{municipality_code}` **[VERIFIED `codes.py:92-96`, el `raise` de `:97` solo se alcanza por kwargs faltantes, nunca por nombre vacío]** → TODO dealer name-only de un muni colapsa a UN `cdp_code` en INSERT (over-merge irreversible). (2) **pérdida parcial**: `"Straße"`→`"strae"` vs `"Strasse"`→`"strasse"` (under-merge); `ä/ö/ü`→`a/o/u` (no `ae/oe/ue`). En B1 hay guard `if not clean: return None` (`:157-158`) → under-merge; en `codes.py` no → over-merge. **Asimetría catastrófica.**

**Costura.** Dos mitades que se sellan juntas: **(Fix-1 transliteración)** reemplazar `encode('ascii','ignore')` por `anyascii(text)` antes del `re.sub`, en los 3 fold Python + portar/materializar el fold-SQL; ES byte-idéntico (ASCII pasa inalterado). El handler de script lo decide `IdentityLocale.normalize_policy(cc)` (F22): para JP, **romaji-de-la-fuente** (GeoNames `asciiname`) primero, anyascii fallback (anyascii romaniza Han vía pinyin chino, **incorrecto** para topónimos JP). **(Fix-2 guardia anti-vacío)** en `codes.canonical_key`, antes de la rama name, si `_normalize(name)==''` → `raise ValueError` (mismo contrato que el branch None de B1).

**Fix.** Ambos fixes necesarios y simultáneos: transliteración sin guardia aún puede vaciar (nombre solo-símbolo/emoji); guardia sin transliteración convierte el over-merge en under-merge masivo (todo JP a ValueError). Fix-1 reduce la frecuencia del vacío; Fix-2 lo elimina como posibilidad → `name:|{muni}` estructuralmente inalcanzable.

**Adversarial.** JP/CN/KR: **catástrofe de identidad en minteo** — el único fallo que corrompe la clave INMUTABLE (sample-verify-delete y rollback por-país **NO lo revierten**, el daño ya está en el sha256 sellado). Dos concesionarios JP distintos name-only en Yokohama → mismo `cdp_code` para siempre. DE: eszett/diéresis → under-merge sistemático en edge-1 y B6.1. Ruido: nombre puro-símbolo → vacío → over-merge con cualquier basura del muni (lo captura el guard).

**Sellado (multi-vía).** (1) **Golden byte-identidad ES** sobre 431k+ cdp_code, diff==0, Ferrari verde. (2) **Fixture 2 dealers JP** distintos → 2 keys distintas, CJK no produce `''`. (3) **Unit guardia**: `canonical_key(name="トヨタ")` con política nula DEBE `raise` (no `name:|{muni}`). (4) **Convergencia 2-vía**: `key("Straße")==key("Strasse")`, `key("Müller")==key("Mueller")`. (5) **Vía ortogonal**: conteo de entidades distintas DE/JP **sube** con transliteración vs oráculo de nombres crudos. (6) **Test de igualdad 4-sitios** (3 Python + SQL residual) sobre batería multiscript.

**Herramienta NEXT-LEVEL (€0).** **anyascii** (ISC) https://github.com/anyascii/anyascii **[VERIFIED NEXT-LEVEL.md:224/:329/:482]** — transliterador data-driven, dependency-free, CPU puro. La biblia lo mina **tres veces** sobre exactamente este fallo; `:479-485` **empareja anyascii con la guardia anti-vacío** en `codes.canonical_key` (los dos fixes de la faceta). **ISC = comercial-limpia** vs `unidecode` (GPL-2.0+) que contaminaría el API público (`:225,:483`). Para JP: GeoNames `asciiname`/`alternateNames` (romanización oficial de fuente) primero, anyascii fallback; PyICU como opción reversible más rica.

---

#### F6 Autoridad de exclusion de cadenas y multisucursal

> **Una línea:** la lista de consolidadores que **nunca** deben name-merge, hoy ES-only y duplicada en **dos formas incompatibles** con intersección de solo 5 tokens.
> **↳ Veredicto:** B6·MP9. **Familia:** B. **Cross-ref:** guard consumido por F11 y F15; dirección complementaria en F21; dispatch por F22.

**Deep-spec (al átomo, verificado).** `_CHAIN_PATTERNS` = **9 regex** `re.IGNORECASE` con `.search()` parcial: `flexicar, ocasionplus, clicars, carplus, stellantis, mobility.?centro, grupo\s+\w+\s+motor, bmw\s+premium, mercedes.benz\s+\w+` **[VERIFIED `cross_source_dedup.py:163-176`]**; `_is_chain(name)=any(p.search(name)…)` **[VERIFIED `:254-258`]**. `CHAIN_TOKENS` = **12 strings PLANAS** space-free `flexicar…clickautos, hrmotor, csvmotor, domingoalonso, movento…kmcero, km0` **[VERIFIED `build_residual_namemuni_dedup.py:69-72`]**. **Doble divergencia VERIFIED**: (1) **forma** — regex+`.search()` vs substrings crudos; (2) **representación** — las regex de cross-source llevan `\s+` → solo casan **nombre crudo con espacios**; el residual matchea contra `_norm(name)` que **borra espacios** (por eso sus tokens son space-free); operan sobre representaciones **incompatibles**; (3) **contenido** — intersección = {flexicar, ocasionplus, clicars, carplus, stellantis} (**solo 5**); solo-cross-source = 4; solo-residual = 7. Una cadena atrapada por una capa es **invisible** para la otra. El guard es **asimétrico por diseño**: solo bloquea, nunca fuerza → falso-positivo = under-merge (seguro), falso-negativo = over-merge catastrófico de N sucursales.

**Costura.** Promover a `IdentityLocale.chain_tokens(cc)` + autoridad única `is_chain(name, cc)` (F22), consumida por cross-source y residual desde **una sola fuente**. ES porta la **UNIÓN reconciliada** de las dos listas (ninguna capa pierde cobertura). Por país: DE `Auto1/wirkaufendeinauto/Sixt/EmilFrey/AutoArena`; FR `Aramisauto/EliteAuto/Spoticar`; IT/PT sus consolidadores.

**Fix.** (1) Extender `IdentityLocale` con `chain_tokens` por cc + `is_chain(name, cc)` que normaliza UNA vez con el fold compartido + un set pequeño de regex para marcas multi-palabra. (2) ES = unión reconciliada legacy (ningún token perdido). (3) Borrar `_CHAIN_PATTERNS/_is_chain` y `CHAIN_TOKENS`; ambos importan `is_chain`. (4) Golden de paridad. (5) `chain_tokens(cc)` raise ante cc no registrado.

**Adversarial.** DE: sucursales Auto1/Sixt/Emil Frey pasan el guard name-only ES-only → **OVER-MERGE** de sucursales distintas en un punto. Cross-capa: cadena atrapada por cross-source (regex) re-fusionada por el residual (substring) por la divergencia forma+contenido → Layer 4 **deshace** la protección de B6.1. Precisión: substring sin anclas (`km0`, `csvmotor`) casa a mitad de palabra → under-merge de independientes. Cada mercado (PT/no-UE) tiene consolidadores invisibles a una lista ES-only.

**Sellado (multi-vía).** (1) **Parity golden ES**: `is_chain('ES')` == (`_is_chain` legacy OR substring-residual legacy) sobre corpus fijo → cero regresión, ambas coberturas en una fuente. (2) **Single-source grep**: cero segundo literal de cadena. (3) **Over-merge DE**: fixture sucursales Auto1 con teléfonos distintos → NO name-only merge bajo `cc='DE'`. (4) **Country gate**: falla ruidoso sin fallback ES. (5) **Red anti-over-merge (F19)** re-corrida sin colapso de sucursales.

**Herramienta NEXT-LEVEL (€0).** **PRIMARIA — Snorkel** (Apache-2.0) https://github.com/snorkel-team/snorkel **[VERIFIED NEXT-LEVEL.md:511-517]** — eleva "denylist a mano" a "el motor **descubre** los consolidadores de cada mercado desde el dato": labeling functions (mismo brand-token + teléfonos/direcciones distintas ⇒ "sucursal distinta") auto-generan el roster por país, self-improving. **COMPLEMENTARIA — libpostal** (MIT) **[VERIFIED `:471-477`]** — señal de dirección brand-agnóstica que separa sucursales same-name-same-muni (solo TIGHTENS, nunca fuerza). Ambas CPU/offline/€0.

---

#### F20 Esquema registral y tax-id cif a id nacional generico

> **Una línea:** `entity.cif` es la única columna registral, ES-nombrada y **sin validar** — un CIF basura siembra un strong-key IRREVERSIBLE.
> **↳ Veredicto:** B19·MP3. **Familia:** B. **Cross-ref:** alimenta la rama id de F7/F16; inmutabilidad en F7.

**Deep-spec (al átomo, verificado).** `cif TEXT` única columna registral ES-nombrada **[VERIFIED `0002_entities.sql:11`]**; `alias_kind CHECK IN ('name','domain','cif','phone')` **enum cerrado** **[VERIFIED `:56-57`]**; rama `if cif: return f"cif:{cif.upper().strip()}"` **SIN validación** — cualquier string no-nulo se confía **[VERIFIED `codes.py:88-89`]**. La escalera de prioridad de `canonical_key` es `particular > domain(bare-host) > cif > name+muni > name+prov`; el `cif:` es la **identidad registral FUERTE**: si está, gana sobre name+muni → entra al pre-imagen del `cdp_code` **inmutable**. Un CIF basura/vacío/longitud-rara siembra un merge por strong-key irreversible. El enum cerrado no puede portar un **segundo** id (un país con registral **Y** VAT).

**Costura.** Una columna ES-nombrada + enum cerrado + rama `cif:` sin validar. Genérico = migración **ADITIVA**: conservar `cif` (back-compat) + añadir `registral_id TEXT`, `id_scheme TEXT` (`es.cif`, `de.handelsregister`/`de.vatid`, `fr.siren`/`siret`, `it.iva`, `pt.nif`/`nipc`, `mx.rfc`, `eu.vat`); ensanchar el CHECK (aditivo); rama id → `{scheme}:{validated_value}` con validación de dígito de control.

**Fix.** (1) Migración aditiva (p.ej. `0054`): `ADD COLUMN registral_id, id_scheme`; backfill `id_scheme='es.cif', registral_id=cif WHERE cif IS NOT NULL`; **conservar `cif`** (reversible). Ensanchar `alias_kind` (drop+recreate aditivo). (2) `codes.canonical_key`: rama cif → par `(scheme,id)`; ES emite **BYTE-idéntico** `cif:{CIF}` (cero re-key de 2.2M+); país nuevo `f'{scheme}:{validated}'` con validación (python-stdnum) → basura → fallthrough, no strong-key. (3) Guarda de inmutabilidad (F7): el scheme/id **no filtra** `country_code` al pre-imagen.

**Adversarial.** DE/FR/IT/PT/MX/JP: formato distinto y a menudo **2 ids** (DE HRB+USt-IdNr, FR SIREN/SIRET, IT Partita IVA, PT NIF/NIPC, MX RFC) → columna única + enum cerrado no los representan → se pierde el id fuerte → degrada a name+muni. **Sin validación hoy**: un "CIF" scrapeado basura (OCR, `000000000`, un VAT confundido) siembra un `cif:` strong-key falso IRREVERSIBLE. Cross-frontera: CIF ES y NIF PT numéricamente iguales colisionan en `cif:X` si el scheme no se namespacea.

**Sellado (multi-vía).** (1) **python-stdnum per-scheme golden**: valid/invalid por país pineados; basura falla el dígito de control y se **descarta** (no siembra arista). (2) **Preservación ES**: `es.cif` acepta los CIF de hoy, token `cif:` byte-idéntico → goldens cdp + Ferrari verdes. (3) **Aditivo/reversible**: rollback dropea columnas nuevas, `cif` sobrevive. (4) **Namespacing**: `es.cif:X != pt.nif:X`. (5) **Doble id**: fixture DE con HRB Y USt-IdNr produce DOS aliases.

**Herramienta NEXT-LEVEL (€0).** **PRIMARIA (match exacto) — python-stdnum** (LGPL-2.1) https://github.com/arthurdejong/python-stdnum **[VERIFIED NEXT-LEVEL.md:487-493, "closes B19/MP3 — country-proof strong id key"]** — valida+formatea ~50 países company/VAT/tax CON dígito de control; el strong-key se vuelve auto-validante (basura rechazada antes de sembrar false-merge). LGPL OK como import dinámico server-side; portar check-digits si se exige permisivo. **COMPLEMENTARIA — GLEIF LEI Golden Copy** (CC0 1.0) **[VERIFIED `:172-178`]** — espina registral global de dominio público, id ortogonal cross-border día-uno sin adaptador nacional.

---

#### F21 Autoridad de normalizacion de direccion guard de sucursal

> **Una línea:** la desambiguación de sucursal fue **diferida a un alnum-strip naíf** porque ES no la necesitaba; mercados de cadenas densas (DE) la necesitan.
> **↳ Veredicto:** P5 · Mejora 7. **Familia:** B. **Cross-ref:** compone con F6 (cadenas); fold compartido con F5; backfill token-sintético en F16.

**Deep-spec (al átomo, verificado).** La única normalización de dirección es `_normalize` = `NFKD+ascii-ignore + re.sub('[^a-z0-9]+','')` **[VERIFIED `codes.py:29-32`]**, anexada SOLO a las ramas name+muni / name+prov: `addr = f"|{_normalize(address)}" if address else ""` **[VERIFIED `:92-96`]**. **Sin lexema de tipo-de-vía, sin aislar número de portal, sin postcode**: `"Calle Mayor 3"`→`"callemayor3"` y `"C/ Mayor, 3"`→`"cmayor3"` (MISMA dirección → keys distintas = under-merge), mientras dos direcciones distintas pueden colapsar al mismo alnum (over-merge). En ES quedó enmascarado (muni+name cargan la señal; el diseño admite "only a naive alnum-strip exists"). En el path backfill, "address" ni siquiera es dirección: son tokens sintéticos `contract:{sref}`/`wallapop_user:{sref}` **[VERIFIED `canonical_key_backfill.py:62-66`]** corriendo por el MISMO `_normalize`.

**Costura.** Reemplazar `_normalize`-sobre-dirección por un **parser estadístico multilingüe (libpostal)** que parsea/canonicaliza `road/house_number/postcode` en 100+ países → el guard compara **campos estructurados** (mismo name+muni pero distinto house_number/road ⇒ sucursal distinta). **Crítico: la señal de dirección solo APRIETA el guard** (bloquea, nunca fuerza un merge) → no introduce false-merge; la red F19 sigue gateando. Léxico de vía en `IdentityLocale` (F22) solo como fallback. Separar el path token-sintético del path dirección-real.

**Fix.** Parsear con libpostal y comparar estructurado; el lexema de vía per-locale es fallback; el path backfill (token sintético) nunca llega al parser de direcciones reales.

**Adversarial.** Cadenas DE (Auto1/Sixt/Emil Frey) mismo-nombre en una ciudad: el strip **funde sucursales distintas** (over-merge, el fallo que el guard existe para impedir) o **parte una sucursal** entre formatos de vía (under-merge); compone con F6 si la cadena no está en la lista ES. FR/IT/PT: `'Rue'/'R.'`, `'Via'/'V.'` colapsan/divergen sin noción de tipo-de-vía. JP/CJK: NFKD+ascii-ignore pliega la dirección a `''` (F5) → addr inútil. Punto ciego ES: invisible hasta que aterriza un país de cadenas densas.

**Sellado (multi-vía).** (1) **Parser golden** con los casos de dirección etiquetados de libpostal, pineados por país. (2) **Guard A/B** sobre set etiquetado cadena-sucursal: separa sucursales reales (precisión) sin partir dupes (recall), por país. (3) **Ortogonalidad**: la dirección solo BLOQUEA, nunca fuerza → no puede subir el false-merge sobre F19. (4) **No-regresión ES**: keys que descansan en muni+name quedan byte-idénticas (cero re-key).

**Herramienta NEXT-LEVEL (€0).** **libpostal** (MIT) https://github.com/openvenues/libpostal **[VERIFIED NEXT-LEVEL.md:474]** — parser de direcciones estadístico entrenado sobre OpenStreetMap (100+ países); da al guard una señal cross-country real sin lexemas de vía por país. Complementos: `lieu` (harness de dedup sobre libpostal) y `pypostal` (bindings). Modelo ~2GB offline, sin coste por request. Es exactamente el hueco "the design admits only a naive alnum-strip exists".

---

#### F12 Pack de taxonomia de source-keys

> **Una línea:** 5 conjuntos de source-keys ES que **fallan-abierto en silencio** — la precondición oculta de B6.1, backfill y particular L3; si están vacíos, dos-tres capas mueren en cascada muda.
> **↳ Veredicto:** B4·B15·MP1. **Familia:** B. **Cross-ref:** consumida por F11 (ortogonalidad) y F16 (backfill)→F14; gate tipado pareja con F22.

**Deep-spec (al átomo, verificado).** `GEO_SOURCES=frozenset({"osm"})` **[VERIFIED `cross_source_dedup.py:114`]**; `DIGITAL_SOURCES` 12 keys ES **[VERIFIED `:117-130`]**; `PHONE_SOURCES` **[VERIFIED `:133-143`]**; `WEBSITE_SOURCES` **[VERIFIED `:146-153`]**; `_PARTICULAR_PLAT` 3 plataformas ES **[VERIFIED `canonical_key_backfill.py:23-27`]**. **Consumidor #1**: `_is_orthogonal` define ortogonalidad = `(a_geo and b_dig) or (b_geo and a_dig)` **[VERIFIED `:417-430`]** — si `GEO_SOURCES(cc)` o `DIGITAL_SOURCES(cc)` está vacía, el predicado es **siempre False**. **Consumidor #2**: `candidate_kwargs` rama particular hace `plat=_PARTICULAR_PLAT.get(source_key)`; si no está → `return` SIN candidato → `canonical_key` queda NULL **[VERIFIED `:44-51`]**. **Ambos FALLAN-ABIERTO en silencio**: un source_key sin clasificar no lanza ni loguea, simplemente no participa.

**Costura.** Mover los 5 conjuntos a `IdentityLocale.source_taxonomy(cc)` (despacho por `entity.country_code`); ES registra los EXACTOS de hoy → B6.1 y backfill byte-idénticos. **Fix de cobertura (el corazón)**: gate que enumera TODO `source_key` en `entity_source` por país y exige que cada uno esté en ≥1 bucket (o en un bucket `ignored` explícito) → **falla-CERRADO**: source_key sin clasificar = build ROJO, no NO-OP. Guard de disjuntez cross-pack (un source_key no en dos packs).

**Fix.** (1) Taxonomía per-país en el locale. (2) Gate de cobertura fail-closed. (3) Re-anclar `PROB_*` por país (capa-2: aprenderlas con Splink). (4) `_CHAIN_PATTERNS`→`chain_tokens(cc)` (F6). (5) Teléfono ya delegado a `phone_match_key` (F2): asegurar key E.164.

**Adversarial.** DE: `mobile.de/autoscout24.de` ausentes de `DIGITAL_SOURCES` → `_is_orthogonal` jamás True → **B6.1 entero es NO-OP silencioso** (la omisión más load-bearing). MX: MercadoLibre/Kavak/seminuevos desconocidos → B6.1-noop **Y** `_PARTICULAR_PLAT` no los mapea → particulares MX nunca reciben `canonical_key` → **F16 cobertura cero → F14 sin grupos: 2-3 capas mueren en cascada silenciosa**. JP: carsensor/goo-net ídem. Nunca ruidoso: ningún test ES rompe; el daño es cobertura ausente, invisible hasta auditar.

**Sellado (multi-vía).** (1) **Gate de cobertura total**: `DISTINCT source_key` del país ⊆ unión de buckets → uno suelto = rojo. (2) **ES byte-idéntico**: 5 conjuntos == frozensets/dict de hoy. (3) **Ortogonalidad viva**: `GEO_SOURCES(cc)` y `DIGITAL_SOURCES(cc)` ambos no-vacíos por país, o se marca hueco confesado (no se sella "cross-source OK"). (4) **Backfill no-NULL**: % `canonical_key NOT NULL` en `particular` por encima de un piso. (5) **Disjuntez cross-pack**.

**Herramienta NEXT-LEVEL (€0).** **Pydantic** (MIT) https://github.com/pydantic/pydantic **[VERIFIED NEXT-LEVEL.md:587, "Guard de drift de registry/semilla como CONTRATO TIPADO en CI"]** — country-pack tipado + test CI de biyección `source_health↔registry == 0 UNMAPPED / 0 ORPHAN` por país = el test de cobertura exacto, con disjuntez cross-pack (`:590`). **COMPLEMENTO runtime — Great Expectations/Pandera** (Apache-2.0/MIT) **[VERIFIED `:164-170`]** "Contrato de datos PRE-sello", expectativa "NINGÚN source_key cae en silencio". Pydantic valida la forma en CI sin DB; GE/Pandera valida el dato servido. Ambos €0 CPU puro.

---

### Familia C · Minteo de identidad inmutable

---

#### F7 Autoridad de minteo cdp_code y canonical_key

> **Una línea:** la identidad ETERNA; la faceta donde la parametricidad **ya está casi cerrada** — el peligro es de signo NEGATIVO (un refactor "limpio" re-keyaría todo ES).
> **↳ Veredicto:** Riesgo 2 (re-key) + mitad de B16 (empty-guard). **Familia:** C. **Cross-ref:** empty-name guard compartido con F5; rama cif con F20; consumido por F16.

**Deep-spec (al átomo, verificado).** `mint_code(*, province_code, digest, country_code=DEFAULT_COUNTRY)→f"CDP-{country_code}-{province_code}-{_base32(digest)}"` **[VERIFIED `codes.py:44-53`]** — **el ÚNICO hogar del literal de prefijo** (los ~30 mints enrutan aquí). `canonical_key` **acepta `country_code` pero NO lo usa**: comentario explícito "DELIBERATELY NOT used here … mixing the country into it would change every sha256 hash and re-key all entities" **[VERIFIED `:62-65`]**. Escalera de pre-imagen: `particular:{plat}:{sid}` > `domain:{host}` (bare-host, solo si `host and not path`) > `cif:{CIF}` > `name:{norm}|{muni}` > `name:{norm}|p{prov}` > `raise ValueError` **[VERIFIED `:72-97`]**. `cdp_pair`: `sha256(key)→base32 Crockford 8 chars (sin I,L,O,U)` **[VERIFIED `:100-118`, `:26`]**. **El hash se computa SOLO sobre la pre-imagen sin país**; `country_code`/`province_code` son segmentos decorativos del prefijo que no alimentan el hash → threadear país por todo el stack **no re-mintea una sola entity ES**.

**Costura.** Faceta de signo **negativo**: la única vía segura de hacerlo genérico es **prefijo-only**; cualquier filtración de `country_code` al sha256 re-mintea todo ES (rompe FK `entity_completion` y todo índice servido sobre 2.2M+). Fragilidad secundaria: la rama domain (`:86-87`) asume estructura de URL ES/OEM (bare-host como identidad) → un agregador de otro mercado con path-en-host o sin bare-host mis-mintea.

**Fix.** Bloquear la invariante **mecánicamente**: (1) property-test que asserta `canonical_key` byte-invariante bajo cualquier `country_code`; (2) grep-guard de que `'CDP-'` vive solo en `mint_code:53`; (3) **guardia anti-vacío** en `canonical_key` (raise on empty core) — cierra el over-merge mint-time de B16/F5; (4) mover la política de forma-de-dominio (qué hosts son portales agregadores vs dominio propio) al `IdentityLocale` (F22).

**Adversarial.** DE/FR **refactor-leak**: meter país en la pre-imagen re-keya cada `cdp_code` ES — **el único fallo que corrompe la clave INMUTABLE**. Colisión cross-frontera: name+muni idéntico ES↔país#2 comparte el sufijo de 8 chars (solo el prefijo los segrega; un consumidor que keye por `canonical_key`/sufijo puentea tenants). Rama domain: agregador no-ES mis-mintea. Pre-imagen vacía (sin guardia): nombre CJK que pliega a `''` → `name:|{muni}` → over-merge mint-time de todos los dealers sin dominio/cif de un muni a UN `cdp_code`.

**Sellado (multi-vía).** (1) **Goldens cdp + Ferrari** byte-idénticos tras threadear país (cero re-key). (2) **Hypothesis** genera `country_code` arbitrario y asserta `canonical_key` invariante (prueba de que país no entra a la pre-imagen). (3) **Grep estático**: `'CDP-'` en un solo sitio. (4) **Unit**: `canonical_key` lanza ante core vacío (over-merge mint-time estructuralmente inalcanzable).

**Herramienta NEXT-LEVEL (€0).** **Hypothesis** (MPL-2.0) https://github.com/HypothesisWorks/hypothesis **[VERIFIED NEXT-LEVEL.md:320]** — convierte "el país nunca debe filtrarse a la pre-imagen" + "keys ES byte-idénticas" de esperanza documentada a **invariante generado adversarialmente** con minimización de contraejemplo que bloquea el merge. Complementos: **anyascii** (ISC, `:482`) para la guardia anti-vacío del fold; **in-toto** (Apache-2.0, `:312`) para atestiguar la procedencia de la identidad inmutable sobre 2.2M entidades.

---

#### F3 Validador de prefijo cdp_code gate G1 y los 62 literales

> **Una línea:** el mint ya genera `CDP-DE-*` correcto, pero el **VALIDADOR G1** hard-asserta `^CDP-ES-` → toda entity de país #2 falla los 5 gates y **no se sirve** (el 6.º blocker).
> **↳ Veredicto:** costura `complete.py:89` + Riesgo 6 + G1 6º-blocker. **Familia:** C. **Cross-ref:** mint genérico en F7; province-check per-country pareja con F10/F19.

**Deep-spec (al átomo, verificado).** `_CDP_CODE_RE = re.compile(r"^CDP-ES-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$")` — **país hardcodeado en el ancla** **[VERIFIED `complete.py:89`]**. `check_g1` (uno de 5 gates servidos) usa el regex en `:145-146` (`if not match → (False, "cdp_code_format_invalid")`) + 2 chequeos más **también ES-shaped**: exactamente una fila entity (`:123-133`) y `province_code ∈ 01-52` (`_PROVINCE_RE`, `:135-143`) **[VERIFIED `:107-148`]**. `[CORRIGE v1]` **62 archivos** con literal `CDP-ES-` **[VERIFIED `grep -rl 'CDP-ES-' --include=*.py --include=*.sql | wc = 62`]** — más que los 41 del diseño. **El MINT funciona** (`mint_code('DE')→CDP-DE-*`, `canonical_key` country-blind **[VERIFIED `test_country_coexistence.py:13-16`]**); **el VALIDADOR es el blocker**, guardado por xfail en `test_country_coexistence`/`test_country_golden`.

**Costura.** `^CDP-ES-` en el regex + 62 literales dispersos (parse/match a mano: un `LIKE 'CDP-ES-%'`, un fixture, un slice `[4:6]`) + el province-check `:142-143` ES-shaped = el país horneado en la superficie de **VALIDACIÓN y PARSE**, aunque el MINT ya es prefix-only genérico.

**Fix.** (1) Ensanchar `:89` a `^CDP-([A-Z]{2})-([0-9]{2})-[0-9A-HJKMNP-TV-Z]{8}$` y **quitar el xfail**. (2) Validar el segmento cc contra **ISO-3166-1 alpha-2 (pycountry)** en vez de `[A-Z]{2}` flojo. (3) **Centralizar el prefijo** en un único `CDP_PREFIX(cc)=f'CDP-{cc}-'` (o reusar `codes.mint_code`) y enrutar los 62 literales: **62→1**. (4) Volver el province-check per-country (geo_unit desde ISO/F10).

**Adversarial.** País #2: DE/FR mintea `CDP-DE-*` correctamente pero falla el regex de `check_g1` → nunca pasa G1 → nunca completa los 5 gates → **no se sirve** (6.º blocker). Los **62 literales = mina distribuida**: tocar solo el regex deja **61 trampas** vivas. `[A-Z]{2}` flojo acepta `CDP-ZZ-`/`CDP-QQ-` no-ISO como identidad válida.

**Sellado (multi-vía).** (1) **Golden ES**: `check_g1` byte-idéntico para cdp_codes ES (cero re-key, Ferrari verde). (2) **Pilot DE**: entity `CDP-DE-*` pasa `check_g1` (xfail→xpass→assert). (3) **CI grep**: 0 literales `CDP-ES-` fuera del único `CDP_PREFIX` (62→1, forzado como test). (4) **pycountry**: segmento cc ∈ ISO-3166-1; `CDP-ZZ-` rechazado. (5) **5 gates E2E** para país#2 en `test_country_pilot_de`.

**Herramienta NEXT-LEVEL (€0).** **pycountry** (LGPL-2.1) https://github.com/pycountry/pycountry **[VERIFIED NEXT-LEVEL.md:530]** — autoridad ISO 3166-1 alpha-2 para que el segmento cc sea un país real validado, no un `[A-Z]{2}` flojo; uso en build/config-time mantiene LGPL fuera del hot-path (`:532`). Fallback estricto-permisivo: **iso3166** (MIT, `:531`).

---

### Familia D · Clustering B1 + topología

---

#### F9 B1 clusterer scoping de run y dispatch de locale

> **Una línea:** B1 es **SINGLE-GLOBAL en tres ejes** (qué filas, bajo qué run, con qué locale); re-correr para país#2 BORRA y reescribe el run que sirve a ES.
> **↳ Veredicto:** B1·SH1·MP5. **Familia:** D. **Cross-ref:** topología en F10; locale en F22; gate servido en F17; rollback en F24.

**Deep-spec (al átomo, verificado).** `RUN_ID="dealer-identity-det-v1"` literal FIJO sin sufijo **[VERIFIED `cluster_dealers.py:56`]**; `SCOPE_CONDITION="kind <> 'particular' AND status <> 'closed'"` **sin predicado de país** **[VERIFIED `:59`]**; `_load_entities` `SELECT … FROM entity WHERE {SCOPE_CONDITION}` carga TODAS las entities **[VERIFIED `:236-259`]**; `_write_to_pg` delete-then-insert por el RUN_ID **global** **[VERIFIED `:558-578`]**. **Tres ejes single-global**: (i) qué filas (sin filtro país); (ii) bajo qué id (un literal); (iii) con qué locale (normalizadores sin cc). Re-correr B1 para cualquier tenant **borra y reescribe** el run que sirve a ES. La afirmación de diseño "mismo contrato para cualquier país" es **FALSA en código**: es single-global. *(Esta faceta audita el WHERE/tenancy; la topología de aristas es F10 — sin solape.)*

**Costura.** (1) `SCOPE_CONDITION += AND country_code=%s` (parametrizado). (2) `RUN_ID=f"dealer-identity-det-v1-{cc}"` → delete-then-insert idempotente POR TENANT. (3) cargar `get_locale(cc)` una vez y pasarlo a los 3 normalizadores. `v_canonical` ya sirve el run verificado → aditivo **si** el gate servido también se vuelve per-country (F17).

**Fix.** (1) `SCOPE_CONDITION` plantilla + bindear `country_code` en `_load_entities`. (2) `RUN_ID` sufijado → idempotencia/rollback por tenant. (3) Inyectar `get_locale(cc)` en la firma de los normalizadores; ES registrado con las listas EXACTAS → keys byte-idénticas. (4) `entity_cluster_run.scope` registra el country. **CRÍTICO**: el cambio 1+2 va junto al gate per-country de F17; si solo se hace aquí, B1 escribe runs per-country pero la vista sigue sirviendo el último global.

**Adversarial.** Correr identity para DE hoy ejecuta `_load_entities` SIN filtro → carga ES+DE juntos → aristas cross-país y, al escribir, el delete-then-insert del RUN_ID global **SOBREESCRIBE** el run de ES. Rollback de DE arrastra ES (comparten id). Con `municipality_code` opaco sin country (F10), un mismo string de muni-code entre ES y país#2 puede **PUENTEAR** tenants en el run global. Locale equivocado: entity DE normalizada con léxico ES en silencio → keys erróneas.

**Sellado (multi-vía).** (1) **ES byte-identidad**: con `cc='ES'` el run produce `entity_cluster` idéntico fila-a-fila (golden de cardinalidad + clusters). (2) **Aislamiento**: un run DE no toca NI UNA fila del run ES (`count(entity_cluster WHERE run_id LIKE '%-ES')` invariante antes/después de correr DE). (3) **Idempotencia per-tenant**: re-correr DE produce filas idénticas y NO altera ES. (4) `country_code` foráneo no validado FALLA ruidoso (acopla con F22).

**Herramienta NEXT-LEVEL (€0).** **pycountry** (ISO 3166-1/-2 + ISO 4217, LGPL-2.1) https://github.com/pycountry/pycountry **[VERIFIED NEXT-LEVEL.md:530]** — el `cc` que scopea `SCOPE_CONDITION` y sufija `RUN_ID` debe ser un alpha-2 **canónico**; valida en build/config-time, eliminando el drift `UK`↔`GB` y el typo que crearía un run-tenant huérfano (`EN` en vez de `ES` → RUN_ID fantasma que nadie sirve). Eleva la **corrección de la clave de tenant** (un dato), no el plumbing de run-scoping. Alternativa MIT permisiva: **iso3166** (`:531`).

---

#### F10 Topologia de blocking de 4 aristas y guardas fuzzy

> **Una línea:** las 4 aristas bloquean por `(señal, municipality_code)` con muni-code **token opaco sin país** → en DB multipaís un muni-code colisionante **puentea tenants**.
> **↳ Veredicto:** B2·MP8. **Familia:** D. **Cross-ref:** scoping en F9; single-country invariant en F19; muni-code namespacing cross-etapa con Geo-6.

**Deep-spec (al átomo, verificado).** `FUZZY_BLOCK_CAP=500` **[VERIFIED `:67`]**, `FUZZY_MAX_LEVENSHTEIN=2` **[VERIFIED `:72`]**, `FUZZY_MIN_NAME_LEN=8` **[VERIFIED `:79`]**. `_build_deterministic_edges` (aristas 1-3): clave de bloqueo `(<señal>, municipality_code)` — edge-1 `idx_name_muni`, edge-2 `idx_phone_muni`, edge-3 `idx_web_muni`; cada bucket >1 emite pares intra-bucket **[VERIFIED `:400-462`]**. Edge-4 self-join SQL levenshtein dentro de cada bloque-muni, `HAVING COUNT(*) <= 500`, `length >= 8`, `distance <= 2`, excluyendo exact-equal **[VERIFIED `:262-392`]**. `muni = (ent.get('municipality_code') or '').strip()` — **token OPACO sin country embebido** **[VERIFIED `:416`]**. La colisión está **probada**: `INSERT geo_province(code=28,country_code=DE)` falla en `geo_province_pkey(code)` **[VERIFIED `0053:3-5`]**; el fix promueve la PK a `(country_code, code)` pero la clave de bloqueo de cluster_dealers es el **STRING pelado** `'28079'` sin country → puente. Rationale de los caps: O(n²) a n=1507 (Madrid) ~1.1M pares (`:62-66`); min-len 8 porque levenshtein-1 sobre 5 chars fusionaría `'megar'/'vegar'` (`:74-79`).

**Costura.** La clave de bloqueo debe volverse `(key, country_code, municipality_code)` O el run entero country-scopeado (F9: solo carga un país → muni inambiguo). Los caps `500/8/2` deben re-anclarse por país (distribución de tamaño de muni + estadística de longitud de nombre; CJK transliterado infla longitud → otro min-len).

**Fix.** **Minimal**: country-scopear el run (F9). **Defensa-en-profundidad**: añadir country a la clave Python `(nn,country,muni)` (`:416-430`) y al self-join SQL (`a.country_code=b.country_code` en `:366` + temp table `:313-318`). Re-anclar `FUZZY_*` (`:67/79/72`) al locale/manifest per-country (F22/F19), derivados de estadística censal, no de `500/8/2`.

**Adversarial.** Cross-frontera: `'Auto Schmidt'` en muni `'28079'` ES y `'28079'` XX comparten clave edge-1 → **unión falsa cross-frontera** (falta el invariante single-country). Fuzzy: nombre CJK-transliterado de 8 chars con levenshtein-2 es distancia semántica mayor → false-merge (min-len 8 es heurística latina). CPU: muni foránea densa >1507 con cap subido funde CPU PG; con cap 500 se salta en silencio → el recall fuzzy cae justo en los mercados más densos.

**Sellado (multi-vía).** (1) **Byte-identidad ES** con country-scoping: clusters actuales reproducidos + CHECK 1-7 internos verdes (CHECK6 `Megar≠Vegar` `:830-870`, CHECK7 `AUTOMOCION DEL OESTE` merge `:872-922`). (2) **Fixture 2-países** → CERO clusters cross-country (assert single-country-component). (3) **Cap-meaningfulness**: cap > max muni-size del país O munis saltadas documentadas; paridad recall vs levenshtein brute-force en holdout. (4) **Determinismo**: re-run produce edge-set idéntico (goldens).

**Herramienta NEXT-LEVEL (€0).** **datasketch MinHash-LSH + RapidFuzz** (MIT) https://github.com/ekzhu/datasketch **[VERIFIED NEXT-LEVEL.md:535-541]** — retira el O(n²) SQL levenshtein de edge-4 con candidatos sub-cuadráticos y language-neutral (LSH sobre n-gramas de char) + RapidFuzz para el fine-compare in-block; escala a munis foráneas densas sin el cap 500 ni tuning per-locale. Secundarias: **pycountry** (`:527-533`) para re-anclar caps y el sentinel `<52`; **LaBSE** (`:455-461`) para recall semántico multilingüe donde aún no existe el normalizador del país.

---

#### F23 Seleccion de representante canonico consistente entre 4 capas

> **Una línea:** hay **DOS reglas de representante distintas** (B1 attr-richness vs dedup most-available) y el test richer-than-rep **solo cubre las capas dedup**, no las componentes puras-B1.
> **↳ Veredicto:** red anti-over-merge + consistencia de rep. **Familia:** D. **Cross-ref:** rep most-available en F14; red de cobertura en F19; rank ES-shaped pareja con F12.

**Deep-spec (al átomo, verificado).** `SOURCE_GROUP_RANK = {oem_dealer_network:10, association:9, official_registry:8, marketplace_motor:7, directory:6}` **[VERIFIED `:82-88`]**; `_source_group_rank(sg)=…get(sg,1)` — **DEFAULT 1** para grupos desconocidos **[VERIFIED `:470-471`]**. `_richness(ent)=sum(website,phone,address,cif,lat no-nulos)` **[VERIFIED `:474-478`]**. `_select_canonical`: `sort_key=(-rank, -richness, str(first_seen or '9999-99-99'), cdp or 'ZZZZ')`; `min(members,key=sort_key)` **[VERIFIED `:481-500`]**. **DOS reglas distintas**: B1 ordena por escalera lexicográfica (señal dominante = `SOURCE_GROUP_RANK`, proxy de riqueza = conteo de atributos), mientras las capas dedup eligen **MOST-AVAILABLE-VEHICLE** (tie cdp asc) **[VERIFIED `build_particular_dedup.py:104-109`]**. `_RICHER_THAN_REP` (`am.c > ar.c + 50`, `RICHEST_REP_DRIFT_TOLERANCE`) **SOLO valida las capas dedup** (lee `canonical_dedup`), **no** las componentes puras-B1 (`v_canonical`) **[VERIFIED `test_dedup_invariants.py:184-211`]** → inconsistencia latente sin cobertura. Importa al producto: el `cdp_code` servido es el que `/entities` resuelve; si el rep no es el vendedor que realmente tiene los listados, el usuario ve el dealer equivocado.

**Costura.** (1) `SOURCE_GROUP_RANK` es ES-shaped; un source_group DE/FR cae al **DEFAULT 1** (`:471`) → colapsa la señal dominante de B1 → el rep se elige de facto por richness/first_seen/cdp en país#2 (regresión invisible en ES). El rank debe ser locale-aware o keyear sobre una CLASE de fuente country-agnóstica. (2) La divergencia B1 (attr-richness) ↔ dedup (most-available) debe unificarse o probarse monótonamente consistente.

**Fix.** (1) Promover `SOURCE_GROUP_RANK` a mapa per-country (o clase de fuente normalizada). (2) Unificar el criterio: most-available es la verdad-de-producto → la resolución SERVIDA re-representa por most-available a nivel de capa dedup (ya ocurre) y B1 conserva attr-richness solo para cold-start (sin vehículos aún). (3) **Documentar+ASSERT** extendiendo `_RICHER_THAN_REP` a cubrir componentes B1 vía `v_canonical`, country-aware. No se reescribe la lógica; se ALINEAN los dos criterios y se prueba su convergencia.

**Adversarial.** País #2: `…get(sg,1)` devuelve 1 para todo source_group nuevo → prioridad de fuente B1 anulada → rep por richness/first_seen/cdp → divergencia con most-available de las capas dedup; para componentes **puras-B1** no hay test → el rep equivocado surfacea en silencio. `[CORRIGE v1]` el comentario `:204-210` reconoce un drift benigno de pocos coches (max ~13); el umbral `+50` distingue ruido de bug (el bug Case-A MIN-cdp tenía márgenes en cientos).

**Sellado (multi-vía).** (1) **ES byte-identidad**: `_select_canonical` produce el MISMO `canonical_ulid` por cluster ES (golden). (2) **Consistencia cross-capa**: para TODA componente servida (B1 en `v_canonical` Y dedup en `canonical_dedup`), el rep es most-available dentro de `RICHEST_REP_DRIFT_TOLERANCE`; extender `_RICHER_THAN_REP` a B1, country-aware. (3) **No-degradación de rank**: ningún source_group servido cae a default 1 sin estar declarado. (4) **Property-based** que B1 y la regla most-available convergen al mismo nodo dado el mismo input de riqueza.

**Herramienta NEXT-LEVEL (€0).** **Hypothesis** (MPL-2.0) https://github.com/HypothesisWorks/hypothesis **[VERIFIED NEXT-LEVEL.md:320]** — convierte el chequeo por-ejemplo `_RICHER_THAN_REP` en una **propiedad probada**: genera clusters sintéticos con riqueza/disponibilidad conocida y asserta que la escalera de B1 y la regla most-available **convergen** al mismo representante (y que ese rep es el más rico), minimizando al contraejemplo y congelándolo como regression-golden. Ataca la inconsistencia latente que la faceta nombra (hoy solo cubierta a nivel dedup). + **pandera** (MIT) en CI local, CPU puro.

---

### Familia E · Cadena de overlays dedup

---

#### F11 Motor de dedup cross-source B61 ortogonalidad OSM y digital

> **Una línea:** la overlay que cruza el mundo-mapa (OSM) con el mundo-anuncio (marketplaces), cuya precondición `_is_orthogonal` **falla-abierto en silencio** si la taxonomía del país está vacía.
> **↳ Veredicto:** B4·MP1. **Familia:** E. **Cross-ref:** taxonomía en F12; cadenas en F6; teléfono en F2; pesos aprendidos → Splink.

**Deep-spec (al átomo, verificado).** `RUN_ID_FULL="cross-source-dedup-v1"` **[VERIFIED `:104-105`]**; `SCOPE_SQL=kind IN ('compraventa','garaje','concesionario_oficial','desguace')` **[VERIFIED `:111`]**. 3 estrategias de arista decreciente: phone+muni (`PROB_PHONE=0.97`), web-host+muni (`0.98`), exact-name+muni+fuente-distinta (`0.82`); 2+ señales → `0.99` **[VERIFIED `:155-159`]** — las 4 `PROB_*` son constantes **[ASSUMED]** medidas en ES. **`_is_orthogonal` es la precondición LOAD-BEARING**: `(a_geo and b_dig) or (b_geo and a_dig)` donde `a_geo = bool(keys_a & GEO_SOURCES)` **[VERIFIED `:417-430`]** — exige que un lado lleve key GEO y el otro DIGITAL. **El átomo del no-op silencioso**: `GEO_SOURCES` clavado a `{osm}` (`:114`); si un país no tiene filas 'osm' O ninguna de las 12 digital-keys ES, `a_geo`/`b_dig` son siempre False → **CERO aristas → B6.1 es no-op SILENCIOSO** (sin error, sin log). Anti-FP en orden: muni obligatorio, divergencia Jaccard-trigramas ≥4 tokens rechaza salvo phone/web compartido, chain-collapse guard, geo solo BONUS **[VERIFIED `:36-46`]**.

**Costura.** Los 4 frozensets son taxonomía ES (F12 es el pack); `_is_orthogonal` es GENÉRICO en forma — lo que rompe es la **taxonomía vacía**. Parametrizar los 4 source-sets por país, re-anclar `PROB_*` por país (o aprenderlas), lista de cadenas por país (F6), y añadir un **gate de cobertura** fail-closed.

**Fix.** (1) `GEO/DIGITAL/PHONE/WEBSITE_SOURCES` → `IdentityLocale.source_taxonomy(cc)`; ES registra los 4 sets EXACTOS → aristas byte-idénticas. (2) Re-anclar `PROB_*` por país (capa-2 Splink). (3) `_CHAIN_PATTERNS`→`chain_tokens(cc)` (F6). (4) **Gate CI fail-closed**: todo source_key del país mapea a ≥1 set; key sin clasificar FALLA el build. (5) Teléfono key E.164 (F2) para no cruzar fronteras.

**Adversarial.** DE: `mobile.de/autoscout24` ausentes de `DIGITAL_SOURCES` y OSM disperso → `_is_orthogonal` nunca True → **B6.1 ENTERO no-op silencioso**: duplicados OSM↔mobile.de jamás fusionan, el over-count cross-source se sirve intacto. FR/PT/IT ídem (leboncoin/lacentrale/subito.it sin clasificar). Umbrales Jaccard-trigrama afinados a nombres ES: en DE aglutinante o FR acentuado sobre-rechaza o sub-rechaza. `PROB_NAME_EXACT=0.82` asume calidad de nombre ES.

**Sellado (multi-vía).** (1) **GATE de cobertura fail-closed**: cada source_key del país en ≥1 de los 4 sets → uno suelto FALLA. (2) **ASSERT no-noop**: B6.1 produjo >0 aristas O registro **EXPLÍCITO** (no silencioso) de "no existe solape geo×digital". (3) **RECOMPUTE ortogonal**: merges servidos == recompute SQL independiente. (4) **Byte-identidad ES**. (5) **Goldens nombrados**: `das_weltauto`/`mercedes_benz_wholesale`/`milanuncios` verdes.

**Herramienta NEXT-LEVEL (€0).** **Splink** (linkage Fellegi-Sunter aprendido, MIT) https://github.com/moj-analytical-services/splink **[VERIFIED NEXT-LEVEL.md:447-453]** — apunta EXACTO a la deuda: "hand-coded booleans with ASSUMED probabilities (`PROB_PHONE=0.97` etc.)". Entrena los pesos m/u por EM no supervisado **desde el dato**, probabilidad calibrada por par, exporta el modelo como JSON certificable; corre €0 in-process sobre DuckDB. Reemplaza las 4 `PROB_*` por pesos aprendidos per-país y auto-marca clusters inestables para el gate (la red determinista sigue siendo el piso, `:452-453`). Secundarios: **pyJedAI** (`:543`) 2ª vía ER; **LaBSE** (`:455`) candidate-net más allá del exact-name.

---

#### F13 Dedup super-canonico deep-link Layer 2 y asserts de censo

> **Una línea:** la overlay que une canónicos que comparten una URL de listing; su gate de censo **es FATAL pese a documentarse "non-fatal"** → cualquier fila no-ES aborta el sellado.
> **↳ Veredicto:** B18·SH5. **Familia:** E. **Cross-ref:** composición en F18; gate servido en F17; red en F19.

**Deep-spec (al átomo, verificado).** `ANTI_HUB_K=3` (excluye deep_links compartidos por ≥K canónicos) **[VERIFIED `build_canonical_dedup.py:88`]**. **4 enteros ES sellados** (re-blessed 2026-06-23): `EXPECTED_DEDUPED_COUNT=54489`, `EXPECTED_N_SUPER_CANONICALS=3586`, `EXPECTED_TOTAL_MEMBERS=7628`, `EXPECTED_N_MERGED=4042` — globales, sin country **[VERIFIED `:98-101`]**. `[CORRIGE v1]` **LA CONTRADICCIÓN confirmada**: comentario `:95-97` dice "non-fatal DIVERGENCE warning prompting re-verification"; código `:455-463` hace `print("[DIVERGENCE DETECTED]…DO NOT force…"); sys.exit(1)` — **FATAL** **[VERIFIED]**. La query deep_link excluye `kind <> 'particular'` (fix del over-merge 113k) y `COALESCE(vc.canonical_cdp_code, e.cdp_code)` **[VERIFIED `:184-191`]**. `canonical_dedup_run(run_id TEXT PRIMARY KEY)` — **sin columna country_code** **[VERIFIED `0027:43`]**; `vam_verified DEFAULT FALSE` (gate del Director). Axioma: un `deep_link` (URL) = un dealer físico.

**Costura.** Los 4 `EXPECTED_*` son censo ES punto-en-el-tiempo, GLOBALES, y el assert es FATAL. El instante en que existe CUALQUIER fila no-ES (o el censo ES crece) los counts divergen → `sys.exit(1)` → el overlay NUNCA se construye → sellado ABORTA ("trampa FATAL-al-crecer"). `RUN_ID` global, PK sin country.

**Fix.** (1) Reemplazar los 4 enteros + `_assert` FATAL por expectativas **country-keyed NO-fatal**: counts per-cc, comparar a banda/baseline per-cc, **warning + exit 0** (honrar `:96`); fatales SOLO los invariantes country-proof (0 particular por componente, single-country, anti-hub honrado). (2) Country-scopear: `RUN_ID=f'…-{cc}'` + `AND e.country_code=$1` + migración aditiva que añade `country_code` a `canonical_dedup_run` (F17). (3) Assert single-country de cada componente. (4) Re-anclar `ANTI_HUB_K` por estadística de compartición de listados del país.

**Adversarial.** ALL onboarding: cualquier entity no-ES o crecimiento del censo ES → los 4 asserts divergen → `sys.exit(1)` → el deep-link layer no llega a verdict y el seal aborta. `--force` sobre divergencia REAL sellaría un over-merge (`:459` advierte "DO NOT force"). DE/MX: URL-agregador con `ANTI_HUB_K=3` mal-anclado encadena dealers no relacionados. Cross-frontera: deep_link sin country en el JOIN puentea un dealer ES y uno DE.

**Sellado (multi-vía).** (1) **Prueba no-fatal**: fila sintética no-ES → build COMPLETA (exit 0) con warning, NO `sys.exit(1)`; ES baseline intacto. (2) **Invariantes estructurales DUROS** (siguen fatales): 0 `particular` por componente, **toda componente single-country**, anti-hub honrado. (3) **Counts per-country**: ES reproduce 54489/3586/7628/4042 byte-idéntico. (4) **Idempotencia** `delete RUN_ID-{cc}` then insert. (5) **Goldens** `LOUZAO A CORUÑA=22`, `DIMOVIL=17` (mayores legit, `:93`) verdes + red F19.

**Herramienta NEXT-LEVEL (€0).** **PRIMARIA — Great Expectations / Pandera** (Apache-2.0) https://github.com/great-expectations/great_expectations **[VERIFIED NEXT-LEVEL.md:164-170, "Contrato de datos PRE-sello … falla CERRADO, no abierto"]** — convierte los 4 enteros hand-blessed + `sys.exit(1)` en una Expectation Suite VERSIONADA y country-keyed que falla CERRADO sobre la precondición **estructural**, no un FATAL global sobre un entero exacto; ES suite byte-idéntica, país nuevo aditivo. **COMPLEMENTARIA — ER-Evaluation** (AGPL-3.0; CLI offline o portar a scipy) **[VERIFIED `:519-525`]** — sustituye el frágil `EXPECTED_DEDUPED_COUNT` por cardinalidad CERTIFICADA + intervalo por país: el censo creciente **encoge el margen** en vez de detonar `sys.exit(1)`.

---

#### F14 Dedup particular province-split Layer 3 y modelo de identidad del particular

> **Una línea:** funde los N `cdp_code` provinciales de un mismo vendedor privado; su DSN está **hardcodeado sin override** y su etiqueta `rep=MIN(cdp)` está **obsoleta** vs el most-available vivo.
> **↳ Veredicto:** B15(particular) + costura DSN `build_particular:38`. **Familia:** E. **Cross-ref:** modelo sellerId en F16; taxonomía en F12; rep en F23; rollback en F24.

**Deep-spec (al átomo, verificado).** `DSN="postgresql://…127.0.0.1:5433/cardeep"` **hardcodeado, SIN `os.environ`** **[VERIFIED `build_particular_dedup.py:38`]** (`[CORRIGE v1]` el literal real es `:5433`, no `:5434`, y **no existe ninguna vía de override**). Grupos: `WHERE kind='particular' AND canonical_key IS NOT NULL GROUP BY canonical_key HAVING count(*)>1` **[VERIFIED `:64-71`]**. Casos: **C** `len(existing)>1 or super_kinds!={"particular"}` → SKIP (preserva cross-kind) **[VERIFIED `:94-98`]**; **B** reusa el único super particular **[VERIFIED `:99-102`]**; **A** `rep=min(members, key=(-avail, cdp))` = **MOST-AVAILABLE, tie cdp asc** **[VERIFIED `:109`]**; nunca pisa mapping existente **[VERIFIED `:112-113`]**. INERTE: `vam_verified=FALSE` **[VERIFIED `:132`]**. `[CORRIGE v1]` **DRIFT REAL**: docstring `:14-18` y label dry-run `:118` dicen `rep=MIN(cdp_code)`, pero el código vivo `:109` hace **most-available** (fix FASE 3, `:104-107`) — **etiqueta obsoleta = trampa** para quien onboardea. Modelo: un particular en N provincias recibe N `cdp_code` con mismo sufijo-hash (el hash excluye provincia) pero distinto prefijo; la clave definitiva es `particular:{platform}:{sellerId}` (`codes.py:72-75`).

**Costura.** (1) **DSN hardcodeado** → no puedes apuntar a otra DB/tenant ni al dry-run. (2) **Modelo de identidad ES-only**: `_PARTICULAR_PLAT` 3 source_keys ES + regla sellerId `coches.net→bucket-provincia` (`:47`); plataformas de otro mercado ausentes → `canonical_key` nunca computa `particular:{plat}:{sid}` → group query vacío → **L3 no-op silencioso**.

**Fix.** (1) `DSN=os.environ.get('CARDEEP_DSN', default)`. (2) Promover `_PARTICULAR_PLAT` y la regla de anonimización/bucket al `IdentityLocale` por país (F22). (3) Sufijar `run_id` por país (F24). (4) **Sincronizar la etiqueta dry-run `:118` y el docstring `:14-18` con el most-available real `:109`** (cerrar el drift de doc).

**Adversarial.** MX/JP: plataformas de particular desconocidas → `canonical_key` nunca minteada → province-splits jamás fusionados (cobertura cero silenciosa; hambre encadenada F16→F12). DSN `:5433` hardcodeado bloquea onboarding contra otra DB. `'S.A. DE C.V.'` mal-stripeado (F4) contamina el nombre. Etiqueta `rep=min(cdp)` obsoleta engaña al onboarder y rompe la consistencia de rep (F23). Caso C: si `entity.kind` de un país diverge, un particular mal-tipado podría fundirse con un dealer.

**Sellado (multi-vía).** (1) **INERTE por construcción** (`vam_verified=FALSE`; vista intacta hasta gate tras E2E) — sello de seguridad primario. (2) **Reversibilidad** por DELETE del run (F24). (3) **Invariante**: cada par comparte exactamente un `canonical_key`; dealers intactos; cross-kind (Caso C) preservado — vía red F19 country-aware. (4) **2ª vía Splink** re-deriva clusters mismo-vendedor y debe concordar/refinar el agrupamiento por `canonical_key` dentro del intervalo; divergencia → gate. (5) **Consistencia rep** most-available == richer-than-rep (F23).

**Herramienta NEXT-LEVEL (€0).** **Splink** (Fellegi-Sunter probabilístico aprendido, MIT) https://github.com/moj-analytical-services/splink **[VERIFIED NEXT-LEVEL.md:450]** — €0 in-process sobre DuckDB; EM-entrena pesos m/u desde el dato, probabilidad calibrada + waterfall por merge, `model.json` reproducible por país; alimenta el gate VAM (el determinista por `canonical_key` sigue siendo el piso). Convierte el heurístico ASUMIDO del province-split en una 2ª vía certificable y auto-recalibrante. 3ª vía: **pyJedAI** (Apache-2.0, `:546`) para tri-acuerdo.

---

#### F15 Dedup residual name muni Layer 4 y fix bystander-drag

> **Una línea:** la 4.ª capa coarsen-only que funde stragglers `(norm_name,muni)`; su clave de grupo **YA diverge** de B1 (sin strip de sufijo + 4.ª normalización en SQL).
> **↳ Veredicto:** costura residual + bystander-drag. **Familia:** E. **Cross-ref:** léxico/fold con F4/F5; cadenas con F6; dirección con F21; composición con F18.

**Deep-spec (al átomo, verificado).** `DSN=os.environ.get("CARDEEP_DSN",…)` — `[CORRIGE v1]` **TIENE override** (limpio, a diferencia de F14) **[VERIFIED `:60`]**; `BASE_RUN="particular-canonkey-v1"` (encadena sobre L3) **[VERIFIED `:62`]**; `CHAIN_TOKENS` 12 strings ES-only **[VERIFIED `:69-72`]**; `_norm` 3.ª copia del fold **sin strip de sufijo** **[VERIFIED `:75-79`]**; UnionFind two-pass `_p`/`_r` (copia de F1) **[VERIFIED `:82-116`]**; SQL de grupos `lower(regexp_replace(coalesce(trade_name,legal_name),'[^a-zA-Z0-9]','','g')) AS nm` — **4.ª normalización** (sin NFKD, sin strip de sufijo) **sin filtro country_code** **[VERIFIED `:145-160`]**. **El corazón — `_is_eligible` (bystander-drag)**: `own_codes={cdp_code}∪rcodes`; si algún `base_members[sup] − own_codes` no-vacío → ineligible **[VERIFIED `:209-218`]** (ROOT FIX del over-merge clase-aragncar: bystander "VenderMiCoche.es Zaragoza" + "Cars Zaragoza"). Clasificación `excl_chain`/`excl_addr`/`excl_ambiguous`; `rep=min(rcodes, key=(-avail,cdp))` **[VERIFIED `:223-245`]**. Asserts coarsen-only Inv-1/Inv-2 + `sys.exit(1)` **[VERIFIED `:279-341`]**; snapshot `canonical_dedup_backup_20260620` pre-write **[VERIFIED `:360-366`]**.

**Costura.** `CHAIN_TOKENS` ES-only; `_norm` (3.ª copia) + el fold SQL `:148` (4.ª, aún más débil) divergen de `_normalize_name` de B1; SQL de grupos sin `country_code`; snapshot congelado por fecha (ni run ni country scopeado).

**Fix.** (1) `CHAIN_TOKENS` desde `IdentityLocale.chain_tokens(cc)` (F6). (2) Reemplazar `_norm` y el fold SQL `:148` por la autoridad de nombre compartida + anyascii (F5) → clave de grupo **== clave de B1** (cero drift). (3) `AND e.country_code=%s` en el SQL de grupos `:153` y en avail; scopear `BASE_RUN/RUN_ID` por país. (4) Snapshot run+country scopeado. (5) **Mantener `_is_eligible` bystander verbatim** (country-agnóstico y correcto).

**Adversarial.** `CHAIN_TOKENS` ES-only → cadena DE (Auto1/Sixt) con name+muni pasa el chain-guard → **over-merge** de sucursales. `_norm` ASCII-fold: kanji→`''` (agrupación espuria JP/CN), pierde eszett DE. **Fold SQL `:148` sin strip**: `'Mueller GmbH'` vs `'Mueller'` agrupan distinto que `_normalize_name` de B1 → drift silencioso clave-grupo↔arista-B1. Sin filtro de país: ES+DE co-agrupan por `(nm,mc)`; muni-code opaco colisionante cross-frontera (F10) puentea tenants. Aflojar bystander → vuelve el over-merge clase-aragncar.

**Sellado (multi-vía).** (1) **Golden ES**: `SAFE=19 / excl_ambiguous=4 / excl_addr=36 / excl_chain=4` byte-idéntico (counts verificados 2026-06-23 `:201-204`). (2) **Bystander unit**: grupo cuyo base super tocado lleva un miembro externo → `excluded_ambiguous`, 0 aristas. (3) **Scope per-country**: run DE escribe `residual-namemuni-v1-DE`, 0 filas ES tocadas; rollback restaura ES byte-exacto. (4) **Coarsen-only** verde (Inv-1/2). (5) **Paridad de clave de grupo**: `nm` residual == `_normalize_name` B1 en fixture (mata el drift de la 4.ª fold). (6) **libpostal A/B** sobre el address-guard.

**Herramienta NEXT-LEVEL (€0).** **libpostal** (MIT) https://github.com/openvenues/libpostal **[VERIFIED NEXT-LEVEL.md:474]** — reemplaza el `_norm(address)` alnum-strip por parser estadístico de direcciones de 100+ países → el address-guard (`excl_addr`) correcto cross-mercado; `lieu`/`pypostal` (`:475`). + **anyascii** (ISC, `:482`) cierra el drift de la 3.ª copia ASCII-fold de `_norm`.

---

#### F16 Backfill forward-coverage de canonical_key

> **Una línea:** rellena `canonical_key` lazy con corrección matemáticamente cerrada (el hash es testigo) — pero los **feeders de candidatos** son ES-only y su ausencia mata L3 en silencio.
> **↳ Veredicto:** B15(backfill)·MP1 (cascada). **Familia:** E. **Cross-ref:** taxonomía en F12; rama cif en F20; alimenta F14.

**Deep-spec (al átomo, verificado).** `_PARTICULAR_PLAT` mapa source_key→token de plataforma **[VERIFIED `:23-27`]**; `_SELECT` filas `WHERE canonical_key IS NULL AND province_code IS NOT NULL` con `LEFT JOIN LATERAL` al primer `entity_source` **[VERIFIED `:29-38`]**; `candidate_kwargs` por prioridad: particular `_PARTICULAR_PLAT.get(source_key)` (`sid=prov if plat=='coches.net' else source_ref`) / dealer `domain`/`cif`/`name+muni` **[VERIFIED `:41-68`]**. **El GATE de re-hash (`:88`)**: por cada fila NULL recomputa `cdp_pair(**kw)` y **SOLO escribe `canonical_key` cuando el `code` recomputado IGUALA el `cdp_code` guardado** → **una key errónea es IMPOSIBLE de escribir** (el hash es el testigo absoluto) **[VERIFIED `:71-98`]**. Idempotencia estructural (2.º run solo ve filas aún NULL). El pre-imagen de `canonical_key` ya es country-agnóstico → el backfill está **listo-para-genérico EXCEPTO por los feeders de candidatos**.

**Costura.** Dos feeders ES-hard-codeados: (1) `_PARTICULAR_PLAT` → mapa por país (alimentado por F12). (2) regla de anonimización `coches.net→sid=prov` (`:47`) → parametrizar por (plataforma, país). (3) la rama `cif` (`:58-59`) → id nacional VALIDADO por forma (F20). **El gate `:88` y `cdp_pair` no se tocan: ya son genéricos.**

**Fix.** (1) `_PARTICULAR_PLAT`→`IdentityLocale.particular_platforms(cc)`; ES conserva el dict EXACTO. (2) Parametrizar la regla seller-id anónimo por (plataforma, país). (3) En la rama `cif`, validar por **python-stdnum** antes de emitir candidato (es.cif/de.vatid/fr.siren/it.iva/pt.nif/mx.rfc). (4) Métrica de cadencia `matched/scanned by_kind by_country` para que la cobertura-cero sea **VISIBLE**. **Nada relaja el gate** — solo ENRIQUECE el set de candidatos.

**Adversarial.** MX/JP (**cobertura-cero silenciosa**): sin las plataformas de particular del país, `candidate_kwargs` no emite candidato (`return` temprano `:51`) → el gate nunca matchea → `canonical_key` NULL → **F14 sin grupos que fusionar**. No falla ruidoso: `matched=0`, invisible hasta auditar. DE/FR/IT/PT: la rama `cif` asume formato ES; un id de otro país degrada a `name+muni` (más débil).

**Sellado (multi-vía).** (1) **ES byte-identidad**: rellena la MISMA `canonical_key` que hoy (golden de `by_kind`). (2) **Auto-verificación intrínseca**: el gate `:88` es la prueba viva (ninguna key escrita puede no reproducir su `cdp_code`; corrección absoluta, no muestreada). (3) **Cobertura per-país con piso**: `matched/scanned` por kind por country supera un floor, o el país se marca "particular-uncovered" (cierra el cobertura-cero invisible). (4) **Idempotencia**: 2.º run `matched=0` nuevos.

**Herramienta NEXT-LEVEL (€0).** **python-stdnum** (validación registral/VAT con dígitos de control, LGPL-2.1) https://github.com/arthurdejong/python-stdnum **[VERIFIED NEXT-LEVEL.md:490]** — la rama `cif` emite hoy `row['cif']` crudo; python-stdnum conoce ~50 esquemas nacionales y los valida CON check-digit → la rama registral generaliza per-país y un id-basura se rechaza ANTES de gastar un candidato. El id-fuerte pasa de "cif ES crudo" a `{scheme}:{validated_value}` country-proof. Pure-Python offline; el gate de re-hash ya garantiza corrección — esto eleva la COMPLETITUD+VALIDEZ del set de candidatos.

---

#### F18 Arquitectura de composicion de la cadena de overlays coarsen-only

> **Una línea:** las 4 capas componen por **carry-forward + append-only never-override**; la cadena está acoplada por **run-ids STRING literales sin dimensión de país** y un peligroso `ORDER BY run_id DESC` léxico.
> **↳ Veredicto:** composición coarsen-only (orden + enchufe de capa). **Familia:** E. **Cross-ref:** qué-run-sirve en F17; capas en F11/F13/F14/F15; rollback en F24.

**Deep-spec (al átomo, verificado).** `v_dealer_resolved` compone B1 ∘ dedup: CTE `b1` `COALESCE(vc.canonical_cdp_code, e.cdp_code)` **[VERIFIED `0028:46-56`]**; CTE `deduped` `COALESCE(cd.super_canonical_cdp_code, b1_cdp)` **[VERIFIED `:57-68`]**; lee UN solo run `latest_run = WHERE vam_verified=TRUE ORDER BY run_id DESC LIMIT 1` **[VERIFIED `:36-45`]**. **Encadenado por STRING de run-id**: residual declara `BASE_RUN="particular-canonkey-v1"` literal **[VERIFIED `build_residual:62`]**; particular `DEFAULT_NEW_RUN="particular-canonkey-v1"` **[VERIFIED `build_particular:39`]**. **CARRY-FORWARD**: el particular COPIA todas las filas del served_run al new_run (`INSERT…SELECT…WHERE run_id=served_run`) **[VERIFIED `:138-145`]** + AÑADE merges con `ON CONFLICT DO NOTHING` **[VERIFIED `:147-154`]** (nunca pisa: `if c in mapped: continue`). Test coarsen-only `test_dedup_chain_only_coarsens_no_merge_undone` (cada par co-clusterizado resuelve al MISMO super; reps PUEDEN moverse, PARTIR un merge NO) **[VERIFIED `:406-434`]**. **La invariante**: partición servida ⊒ deep-link ⊒ B1 (cada una solo coarsens); el orden vive en STRINGS literales + "último vam_verified por `run_id DESC`".

**Costura.** Genérica EN FORMA, pero acoplada por run-ids STRING literales SIN país: `BASE_RUN`, `RUN_ID`, el run deep-link, todos GLOBALES. Para un 2.º país, suffixar los run-ids por país (`…-{cc}`) para que cada país tenga su PROPIO head, o filtrar carry-forward/`BASE_RUN` por country. Distinta de F17 (qué-run-sirve): aquí se audita la **COMPOSABILIDAD** (orden + coarsen-only + enchufar capa nueva).

**Fix.** (1) Parametrizar `BASE_RUN`/`NEW_RUN` por país (suffix `-{cc}`); la PK `(run_id, canonical_cdp_code)` ya aísla → cadenas limpias. (2) Sustituir "latest vam_verified `ORDER BY run_id DESC`" por seleccción del head declarado en un **MANIFEST de cadena ordenado por país** (NO confiar en el orden léxico del string). (3) El build asevera que `BASE_RUN == el run inmediatamente previo del manifest`. (4) Insertar/reordenar una capa actualiza el manifest, no un literal disperso.

**Adversarial.** **REORDER**: si `build_particular` corre antes de gatear deep-link, `served_run` resuelve a B1-only → particular arrastra la base EQUIVOCADA. **LANDMINE LÉXICO**: `ORDER BY run_id DESC LIMIT 1` **[VERIFIED `0028:42-44`]** elige el head por MAX LÉXICO del string — coincide con la cadena solo por convención de nombres (`'r'>'p'>'d'`); un país cuyo head ordene antes que un run intermedio (o >1 `vam_verified=TRUE` durante un rebuild) hace que la vista sirva un run **NON-HEAD**. **CROSS-TENANT**: con run-ids globales, particular de DE carry-forwardea filas ES al mismo string → revertir DE borra aristas ES. **CAPA NUEVA**: insertar "photo-dedup" exige re-apuntar `BASE_RUN`; si se olvida, la capa nueva se cae del head en silencio.

**Sellado (multi-vía).** (1) **Property coarsen-only** (test `:406` generalizado country-aware): ningún merge deshecho, por país; reps pueden moverse. (2) **Completitud carry-forward**: el head tiene row-count ≥ suma de aristas propias de cada capa. (3) **Manifest de orden**: cadena declarada por país; el build asevera `BASE_RUN == previo` y `served == head del manifest` (no el max léxico). (4) **Recompute de cardinalidad** componiendo las capas en orden (served==recompute de F19). (5) **Idempotencia**: re-correr una capa reproduce el head byte-idéntico.

**Herramienta NEXT-LEVEL (€0).** **Hypothesis** (property-based, MPL-2.0) https://github.com/HypothesisWorks/hypothesis **[VERIFIED NEXT-LEVEL.md:320]** — el coarsen-only es una propiedad de retículo (∀ cadena, la partición servida es coarsening de B1; ∀ reordenamiento/inserción, ningún merge deshecho). Hypothesis GENERA cadenas adversariales (sets de aristas aleatorios, órdenes de run, inserciones) y MINIMIZA al contraejemplo, cazando los landmines de reorder/stale-base/sort-léxico que el golden por-ejemplo (`:406`) no enumera. *(Caveat honesto: NEXT-LEVEL documenta Hypothesis para el contrato de extracción, no para esta invariante de composición — misma herramienta/licencia aplicada a un target adyacente.)* Secundario: **pyJedAI** (`:543`) como vía ER independiente que recomputa el set canónico compuesto (2-vía).

---

### Familia F · Capa beta (no servida)

---

#### F8 Capa beta resolve_entities desacople ES y seguridad de activacion

> **Una línea:** la clausura transitiva fingerprint (NO servida hoy, `vam_verified=FALSE`) porta **DOS copias frágiles ES** — un teléfono last-9 y un city-guard global ASCII-ciego — que false-mergean en cuanto se sirva.
> **↳ Veredicto:** SH8 + Riesgo 5 (activación) + Mejora 2. **Familia:** F. **Cross-ref:** teléfono en F2; transliteración/city en F5; UnionFind en F1.

**Deep-spec (al átomo, verificado).** `_normalize_phone`: `digits[-9:]` con guard `len<7→None` — **SEGUNDA copia del normalizador frágil**, SIN validación de forma ES ni strip namespaced de `+34` **[VERIFIED `resolve_entities.py:135-146`]**; alimenta `phone_buckets→ph_candidates→` arista 'phone' **[VERIFIED `:568-571`]**. `_load_ine_municipalities`: `SELECT name FROM geo_municipality` **sin filtro de país** **[VERIFIED `:245`]**, folded con `_nfkd_lower` (`[CORRIGE v1]` definido en `:168-173`, no `:247` como decía el hint; la llamada está en `:247`) — ASCII-fold parcial, ciego a CJK. `UnionFind` copia (F1) **[VERIFIED `:257-291`]** + `ConstrainedUnionFind` con `city_set`/`org_set` **[VERIFIED `:299-380`]**. Estado NO servido: `vam_verified=FALSE` **[VERIFIED `:1051`]**. DSN env-override SÍ existe (`:119-123`). El city-guard §B Guard 2 bloquea un merge fingerprint si ambos trade_names contienen tokens de municipio INE DISTINTOS — pero carga el set GLOBAL (sin país) y folda ASCII-ciego.

**Costura.** Tres costuras: (i) **teléfono** — borrar `digits[-9:]` y delegar a `phone_match_key(raw, cc)` (F2, key E.164 completa `+34xxx≠+49xxx`); (ii) **city-guard** — `_load_ine_municipalities` recibe `country_code` y filtra `WHERE country_code=%s` (la columna existe `0052/0053`), y el fold pasa a transliteración script-aware (anyascii) no ASCII-ciego; (iii) **union-find ×2** — consolidar bajo el primitivo de F1.

**Fix.** (teléfono) borrar cuerpo de `_normalize_phone` y delegar; añadir `e.country_code` al SELECT/GROUP BY de `_load_p_entities` (`:392-412`). (city-guard) `WHERE country_code=%s` + reemplazar `_nfkd_lower` por anyascii en `_city_tokens`. (union-find) importar F1. (activación) **NO flipear `vam_verified=TRUE` hasta que ambos goldens pasen.**

**Adversarial.** JP/CJK: set global + ASCII-fold → city-guard ciego, dos branches JP en pueblos distintos con Jaccard 1.0 (pool de stock virtual) se fusionan (**over-merge A—C—B**, el fallo exacto que el `ConstrainedUnionFind` existe para impedir, pero su `city_set` queda vacío para JP). FR/PT: móvil que comparte últimos 9 dígitos con uno ES → par candidato 'phone'; con fingerprint ≥0.30 → **falso-merge cross-frontera** de dos dealers reales. Activación peligrosa: si se gatea con el last-9 vivo, un teléfono con extensión produce token erróneo → arista falsa horneada en el cierre transitivo → colapso IRREVERSIBLE de dos dealers en la vista servida.

**Sellado (multi-vía).** (1) **Paridad ES** del teléfono + assert estructural: dos calling-codes distintos nunca comparten key. (2) **Fixture ES+JP**: city-guard carga solo el país del run y detecta token JP vía anyascii. (3) **Seguridad de activación**: el run permanece `vam_verified=FALSE` en CI; test sobre fixture 2-países asserta **CERO aristas cross-país** (single-country-component) ANTES de cualquier gate. (4) **Idempotencia** delete-then-insert (`:1040-1045`).

**Herramienta NEXT-LEVEL (€0).** **python-phonenumbers** (Apache-2.0) https://github.com/daviddrysdale/python-phonenumbers **[VERIFIED NEXT-LEVEL.md:463-469]** — autoridad E.164 ~250 regiones; key completa hace imposible la colisión `+33/+34` y `is_valid_number` da el gate de basura que el last-9 nunca tuvo. Secundaria: **anyascii** (ISC, `:479-485`) para el fold del city-guard (tokens JP/CJK no se pierden).

---

### Familia G · Espina servida + sellado + red

---

#### F17 Vistas de resolucion servida y gate por pais LA ESPINA

> **Una línea:** **LA ESPINA** — las dos vistas servidas eligen "el run a servir" por `vam_verified=TRUE ORDER BY ts DESC LIMIT 1` **GLOBAL**; sellar país#2 voltea el mismo switch que gobierna ES.
> **↳ Veredicto:** B1·SH1·MP5. **Familia:** G. **Cross-ref:** run scoping en F9; rollback en F24; red en F19; composición en F18.

**Deep-spec (al átomo, verificado).** `v_canonical` selecciona `WHERE ec.cluster_run_id = (SELECT … FROM entity_cluster_run WHERE vam_verified=TRUE ORDER BY run_at DESC LIMIT 1)` — **un único run latest-verified GLOBAL, sin filtro de país** **[VERIFIED `0020:51-67` (`:62-67`)]**. `v_dealer_resolved`: el CTE `latest_run` toma `WHERE vam_verified=TRUE ORDER BY run_id DESC LIMIT 1` de `canonical_dedup_run` — **single global** **[VERIFIED `0028:35-76` (`:40-44`)]**. El flag vive en las tablas `*_run` (`entity_cluster_run.vam_verified` `0020:27`; `canonical_dedup_run.vam_verified` `0027:58`) **sin columna de país** **[VERIFIED]**. **Consecuencia**: hay UN run autoritativo para toda la tabla; si corres identity para país#2 y lo sellas, el `LIMIT 1` global ahora selecciona ESE run para TODO país → las filas ES resuelven a través del run del país#2. Sellar DE re-gatea ES; revertir DE desplaza la identidad servida de ES.

**Costura.** Romper SINGLE-GLOBAL en PER-COUNTRY: la tabla de run debe portar `country_code` (o `run_scope`) y las vistas deben seleccionar "el último run vam_verified DE ESTE país" por `country_code` de la entidad — una selección correlacionada/lateral keyed por país, no un `LIMIT 1` escalar global.

**Fix.** (1) Añadir `country_code CHAR(2)` a `entity_cluster_run` y `canonical_dedup_run` (aditivo, `DEFAULT 'ES'` backfillea byte-idéntico, espejo de 0052/0053). (2) Reescribir `v_canonical` (`0020:62-67`) y el CTE `latest_run` de `v_dealer_resolved` (`0028:36-45`) para elegir el latest vam_verified DE ESE país (LATERAL/CTE per-country, **`ORDER BY timestamp dentro del país`**, no por el string `run_id`). (3) Sufijar `RUN_ID` por país (`cluster_dealers:56`). (4) **Degradación**: entidad de un país SIN run verificado debe **COALESCE-to-self** (su `cdp_code` crudo), nunca el run de otro país.

**Adversarial.** Multi-tenant: sellar DE → ES re-resuelve en silencio a través del run DE (mezcla tenants en la identidad servida); rollback DE → la identidad servida ES se desplaza; imposible certificar DE a su intervalo sin re-certificar ES. Sin-run: un país no sellado resolvería contra el run global de otro país (asignaciones cross-tenant) en vez de degradar a self. **Hazard de orden**: `ORDER BY run_id DESC` (`0028:43`) es léxico sobre el string; suffixar por país exige ordenar por timestamp dentro del país.

**Sellado (multi-vía).** (1) **Byte-identidad ES**: con solo el run ES sellado, ambas vistas devuelven filas byte-idénticas a hoy (`/health` dealer count sigue 40,016). (2) **Aislamiento de tenant**: sella un run DE sintético; asserta filas servidas ES SIN CAMBIO y DE resuelve solo por su run. (3) **Rollback**: flip DE `vam_verified=FALSE` → ES intacto, DE degrada a self. (4) **Degradación sin-run**: entidad de país no sellado resuelve a su propio `cdp_code` (COALESCE-to-self), por fixture.

**Herramienta NEXT-LEVEL (€0).** El fix estructural (country en la tabla de run + reescritura de vista) es **ingeniería SQL/esquema pura — sin librería**. La ELEVACIÓN: **in-toto + Sigstore/cosign + rekor** (Apache-2.0) https://github.com/in-toto/in-toto **[VERIFIED NEXT-LEVEL.md:140-147]** — una vez el gate es per-country, cada flip de sello emite una atestación firmada que liga `{git SHA, content-hashes de inputs, run_id, conteos servidos}` a un transparency log tamper-evident → "DE sellado en el intervalo X" = certificado per-country **no-repudiable** verificable por un tercero, y la atestación previa de ES es probadamente intacta ante el sello de DE.

---

#### F24 Disciplina no-destructiva idempotente y rollback por pais

> **Una línea:** identidad es SIEMPRE overlay, NUNCA mutación; pero los `run_id` son constantes **GLOBALES** → revertir país#2 golpea el run/flag que gobierna ES.
> **↳ Veredicto:** SH1-adjacente (rollback) + MP5. **Familia:** G. **Cross-ref:** gate servido en F17; composición en F18; capas en F13/F14/F15.

**Deep-spec (al átomo, verificado).** Headers "Additive + reversible … NON-DESTRUCTIVE overlay … Every original cdp_code survives untouched" **[VERIFIED `0020:1-7`, `0027:34-36`]**; rollbacks por `DROP VIEW/TABLE … CASCADE` **[VERIFIED `0020:69-72`, `0027:122-125`, `0028:78-79`]**. Idempotencia REAL = **delete-then-insert por `run_id` en una transacción**: `DELETE FROM entity_cluster WHERE cluster_run_id=%s` + `DELETE … entity_cluster_run` + INSERT, dentro de `with conn:` **[VERIFIED `cluster_dealers.py:581-633`]** (`[CORRIGE v1]` el hint `:28` es la línea de docstring; el mecanismo vive en `:581-633`). Snapshot físico pre-write del residual `canonical_dedup_backup_20260620` (CREATE/TRUNCATE/INSERT) ANTES del DELETE **[VERIFIED `build_residual:360-366`]**. La cadena COALESCE-to-self (`0028:52-53,63`) hace el rollback **graceful**: quitar un run → LEFT JOIN NULL → COALESCE cae a la capa inferior o al `cdp_code` crudo; la identidad **degrada, no se rompe**. Inmutabilidad de `entity` impuesta solo por disciplina + ausencia de UPDATE **[VERIFIED: ninguna capa hace UPDATE sobre entity]**.

**Costura.** El `run_id` es la unidad de sello/rollback pero hoy es constante GLOBAL (`'dealer-identity-det-v1'`, `'entity-resolution-fingerprint-v1'`, `BASE_RUN/RUN_ID` de los `build_*`). La snapshot table del residual (`:362`) y su `TRUNCATE` (`:364`) son globales. Sin suffix de país, revertir país#2 (DELETE run / flip flag) golpea el MISMO run_id/flag que gobierna ES.

**Fix.** (1) Suffixar cada `run_id` de capa con el país (`…-{cc}`); el delete-then-insert ya escopea por `run_id` automáticamente. (2) Nombre de snapshot residual (`:362`) + `TRUNCATE` (`:364`) → **per-country/per-run** (si no, en run multipaís el snapshot de B sobreescribe el de A). (3) Writes siguen dentro de las transacciones únicas existentes (atomicidad sin cambio).

**Adversarial.** Sin suffix, rollback de país#2 arrastra el run ES sellado (mismo id/flag) → identidad servida ES perturbada (hazard single-global de F17 visto desde la reversibilidad). Write no-idempotente que salte el delete → duplica filas, infla `cluster_size`. **UPDATE accidental de `entity` es IRREVERSIBLE** (reescribe el pre-imagen del `cdp_code` inmutable); el snapshot residual solo cubre `canonical_dedup`, no `entity`. `TRUNCATE` del snapshot (`:364`) global: en run multipaís el snapshot de B sobreescribe el de A.

**Sellado (multi-vía).** (1) **Idempotencia golden**: correr una capa dos veces → filas de run byte-idénticas (row-count + checksum) + `entity` intacto (hash before/after). (2) **Aislamiento de rollback**: con run_ids per-country, borrar/flipear el run de país#2 → filas del run ES + vistas servidas byte-idénticas. (3) **Inmutabilidad**: test que asserta que ningún `cdp_code` de entity cambió (golden cdp / Ferrari). (4) **Recuperabilidad del snapshot**: simular write malo del residual, restaurar desde snapshot per-run.

**Herramienta NEXT-LEVEL (€0).** **DVC (Data Version Control)** (Apache-2.0) https://github.com/iterative/dvc **[VERIFIED NEXT-LEVEL.md:148-154]** — pone los INPUTS de cada run per-country (snapshot de entity, aristas, locale pack, manifest de caps) bajo almacenamiento content-addressed; `dvc repro` de un build pasado reproduce filas de overlay idénticas, y un mismatch de checksum ABORTA. Eleva la idempotencia de "delete-then-insert da las mismas filas SI los inputs no cambian" a "los inputs están hash-pineados → un re-run/rebuild post-rollback es probadamente byte-idéntico". Secundaria: **in-toto + cosign** (Apache-2.0, `:140-147`) para atestiguar cada run per-country tamper-evident.

---

#### F19 Red de regresion anti-over-merge country-aware

> **Una línea:** la vía de verificación independiente (recomputa el over-merge en SQL crudo) es **country-BLIND total** (0 matches de `country_code`) y le falta el invariante **single-country-component**.
> **↳ Veredicto:** MP6·MP10·SH2·SH3·SH4·SH6. **Familia:** G. **Cross-ref:** gate servido en F17; caps con F10; single-country con F13; rep con F23.

**Deep-spec (al átomo, verificado).** `MAX_COMPONENT_SIZE_CAP=30`, `MAX_DISTINCT_NAMES_CAP=12` **[VERIFIED `:75-76`]**; `KNOWN_REAL_MAX_COMPONENT_SIZE=22` (LOUZAO A CORUÑA), `KNOWN_REAL_MAX_DISTINCT_NAMES=8` **[VERIFIED `:79-80`]**. `_served_run()=SELECT … WHERE vam_verified=TRUE ORDER BY run_id DESC LIMIT 1` — **single-global, SIN country_code** **[VERIFIED `:117-126`]** (la espina de F17). Los 5 guards: `_CROSS_KIND_COMPONENTS` (`bool_or(particular) AND bool_or(<>particular)`, firma del over-merge 113k) **[VERIFIED `:142-152`]**, `_MAX_COMPONENT_SIZE` **[VERIFIED `:154-157`]**, `_MAX_DISTINCT_NAMES` **[VERIFIED `:163-176`]**, `_RICHER_THAN_REP` (`am.c > ar.c + 50`) **[VERIFIED `:184-211`]**, `_SERVED_DEALER_COUNT` **[VERIFIED `:216-221`]**. Cap-meaningfulness: `assert MAX_COMPONENT_SIZE_CAP < 52` y `< 52` — **el `52` = provincias de España** (sentinel ES-shaped) **[VERIFIED `:244,:255`]**. `test_served_dealer_count_matches_live_recompute`: `served==recomputed` (recompute SQL independiente bypaseando la vista) — **un entero global, sin split de país** **[VERIFIED `:356-394`]**. **`country_code` en el fichero: 0 matches [VERIFIED grep]**. Goldens vivos: `test_das_weltauto`/`test_mercedes_benz_wholesale`/`test_milanuncios_dealer_identity` **[VERIFIED existen]**.

**Costura.** Tres fixes acoplados por la misma raíz "los guards agregan ES+país#2 sin separar tenant": (Fix-1) `WHERE e.country_code=$cc` en cada guard y en `_served_run` (último run verificado DE ESE país, depende de F17); (Fix-2) re-anclar caps/real-max/sentinel desde un **manifest por país** (subdivisiones: ES 52, FR 101, IT 107, DE 16, MX 32, JP 47); (Fix-3) **AÑADIR la invariante FALTANTE single-country-component**; (Fix-4) `served==recompute` por país.

**Fix.** Idéntico a la costura: country-aware en los 5 guards + `_served_run`; caps desde seal manifest; **`SELECT … GROUP BY super HAVING count(DISTINCT e.country_code) > 1` == 0**; partir el entero global por country.

**Adversarial.** DE/FR (false-fail por agregación): un grupo legítimo grande DE supera el cap 30 calibrado para ES → el guard falla en VERDE sobre dato bueno (flaky), o un cap subido a ciegas deja pasar un over-merge real. **Cross-frontera (el agujero crítico)**: sin la invariante single-country, un dealer del mismo nombre en un muni-code colisionante (`0053` prueba colisión de provincias en 2 dígitos) se fusiona a través de la frontera y pasa cross-kind (ambos dealer), tamaño (2), nombres (1), richer-than-rep — **TODOS los guards verdes**. El over-merge más peligroso es justo el invisible a la red actual. Sentinel `<52` erróneo para FR(101)/IT(107) y DE(16)/MX(32)/JP(47). `served==recompute` global enmascara una regresión de cardinalidad de un solo país.

**Sellado (multi-vía).** (1) **Por-país, no-mezcla**: cada uno de los 5 invariantes con `WHERE country_code=$cc`, verde para CADA país independientemente. (2) **Invariante single-country (nueva, bloqueante)**: cero componentes super-canónicas multi-country en el run servido de cada país. (3) **Caps desde manifest (golden)**: ES reproduce 30/12, real-max 22/8, `<52` (cero regresión); DE/FR/IT/MX/JP pineados a su estadística. (4) **served==recompute por país** a la fila. (5) **2ª vía independiente real**: **pyJedAI** sobre el mismo input concuerda dentro del intervalo certificado; divergencia bloquea el sello. (6) **Goldens vivos** Das WeltAuto/Mercedes wholesale/Milanuncios sin regresión.

**Herramienta NEXT-LEVEL (€0).** Tríada, cada una cubre una mitad: **pycountry** (LGPL-2.1) **[VERIFIED NEXT-LEVEL.md:527-533, nombra literalmente "`<52`=Spain's provinces; FR 101, IT 107, DE 16, MX 32, JP 47" + "single-country invariants asserted per country"]** — autoridad ISO 3166-2 para el seal-manifest de caps (Fix-2/Fix-3), config-time. **pyJedAI** (Apache-2.0, `:543-549`) — 2.ª vía ER arquitectónicamente independiente (hoy build script y SQL audit son ambos home-grown) → Fix-5. **ER-Evaluation** (AGPL-3.0; CLI offline o portar a scipy/BSD) `:519-525` — convierte `served==recompute` (entero global 0.09% home-grown) en **cardinalidad CERTIFICADA con intervalos de confianza POR PAÍS**. Refuerzo: **Hypothesis** (`:320`) para fuzzear los invariantes y minimizar al contraejemplo.

---

#### F22 Registro IdentityLocale y gate CI fail-fast

> **Una línea:** **la espina de dispatch ausente** — `pipeline/identity` tiene **0 referencias `country_code`**; las 5 autoridades son funciones de módulo ES-shaped llamadas sin país → filas extranjeras se normalizan en silencio por reglas ES.
> **↳ Veredicto:** Mejora 5 (extraer pack) + Mejora 3 (CI fail-fast) + Riesgo 3 (silent fallback). **Familia:** G. **Cross-ref:** porta F2/F4/F5/F6/F21/F20/F12; dispatch consumido por F9; gate pareja con F12.

**Deep-spec (al átomo, verificado).** `pipeline/identity` tiene **CERO referencias `country_code`** **[VERIFIED Grep count = 0 en todo el directorio]** — el motor entero es country-unaware en código. `cluster_dealers._normalize_name(name)` sin cc **[VERIFIED `:138`]**, `_normalize_phone(phone)` sin cc **[VERIFIED `:170`]** (`[CORRIGE v1]` `cluster_dealers` **no tiene `_is_chain`**; el hint "254-258" es el cursor SQL de `_load_entities`). `cross_source._normalize_name` sin cc **[VERIFIED `:214`]**, `_normalize_phone→phone_match_key(phone)` **sin cc en el call-site** **[VERIFIED `:231-240`]**, `_is_chain(name)` sin cc **[VERIFIED `:254`]**. `entity.country_code` existe (`0052:54`, idx `:80`) **pero ningún código lo lee**. **NO existe abstracción de locale**: las 5 autoridades (teléfono F2, nombre+sufijo F4, charset F5, cadenas F6, dirección F21) viven como funciones/constantes ES-shaped llamadas SIN país. `IdentityLocale` es el value-object congelado ausente que portaría `{PhonePlan, legal_suffixes, chain_tokens, tax_id_scheme, address_lexicon}`, un `REGISTRY[cc]`, y `get_locale(cc)` que **FALLA RUIDOSO** ante país no registrado.

**Costura.** identity es 100% country-blind en código mientras el DB ya tiene `entity.country_code`. La costura es **la capa de dispatch ausente**: filas extranjeras se normalizan en silencio por reglas ES.

**Fix.** (1) `pipeline/identity/locale.py`: `@dataclass(frozen=True) IdentityLocale` con las 5 costuras; `REGISTRY = {"ES": IdentityLocale(…listas EXACTAS de hoy…)}`; `get_locale(cc)` que **lanza `LocaleNotRegistered`** (jamás ES) para cc desconocido. (2) Threadear `country_code='ES'` por `_normalize_name`/`_normalize_phone`/`_is_chain` en cluster_dealers Y cross_source, despachando a `get_locale(cc).<costura>`; el default mantiene ES byte-idéntico. (3) **Gate CI**: `SELECT DISTINCT country_code FROM entity ⊆ REGISTRY.keys()` (fail-fast) + unit `get_locale('XX')` lanza. (4) Elevar el PhonePlan a python-phonenumbers y las claves del registry a pycountry.

**Adversarial.** **Locale silent-fallback = el fallo load-bearing**: una entity DE normalizada por reglas ES (los `legal_suffixes` ES recortan `'sa'` de palabras FR/DE; la chain-list ES no tiene Auto1/Sixt; `phone_es` false-acepta un móvil FR de 9 dígitos) produce keys ERRÓNEAS en **SILENCIO**, invisible hasta que el over/under-merge aflora aguas abajo; el motor (0 conciencia de país) nunca detecta la fila extranjera. Sin el gate CI, un DB single-tenant ES hace la aserción "cada país tiene locale" **vacuamente cierta** → indetectable hasta el 2.º país, con keys ya minteadas/servidas. `get_locale` cayendo a ES en vez de lanzar convertiría un onboarding-blocker ruidoso en **corrupción de dato silenciosa**.

**Sellado (multi-vía).** (1) **Byte-identidad ES**: country default 'ES' + registry replicando las listas de hoy → todas las keys B1/cross-source + cdp goldens + Ferrari verdes (cero re-key). (2) **Fail-loud unit**: `get_locale('XX')` lanza; ningún path devuelve ES para cc no registrado. (3) **Gate CI**: `DISTINCT entity.country_code ⊆ REGISTRY` (una fila DE sembrada sin locale DE **FALLA CI** — invariante country-proof, espejo de la doctrina fail-closed de Great Expectations). (4) **Dispatch test**: un fixture DE ruteado por `get_locale('DE')` usa sufijos/cadenas/teléfono DE, NO ES. (5) **pycountry**: cada clave del REGISTRY ∈ ISO-3166-1 alpha-2.

**Herramienta NEXT-LEVEL (€0).** **python-phonenumbers** (Apache-2.0) https://github.com/daviddrysdale/python-phonenumbers **[VERIFIED NEXT-LEVEL.md:466]** — la costura PhonePlan del locale pasa a ser metadata Google validada de ~250 regiones en vez de un plan hand-authored; mata el false-accept FR/PT y los rechazos DE/IT/MX/JP en una dependencia, envuelto tras `phone_match_key(raw, country_code)` para que ES quede byte-idéntico (`:468`). + **pycountry** (LGPL-2.1, `:530`) para validar las claves del registry y alimentar el gate CI contra el set ISO real.

---

### Arsenal NEXT-LEVEL €0 consolidado (24 facetas → herramientas)

> Todas verificadas contra `NEXT-LEVEL.md`. Todas €0 / CPU-puro / offline (las palancas €>0 quedan en OI-2). Una misma herramienta sirve a varias facetas: ese solape es **deliberado** (un stack mínimo cubre las 24).

| Herramienta | Licencia | NEXT-LEVEL.md | Facetas | Qué eleva |
|---|---|---|---|---|
| **Hypothesis** | MPL-2.0 | :320 | F1·F7·F18·F19·F23 | Property-based: invariantes (equivalencia UF, country-no-en-preimagen, coarsen-only, convergencia de rep) con minimización de contraejemplo |
| **pyJedAI** | Apache-2.0 | :543/:546 | F1·F11·F14·F19 | 2.ª/3.ª vía ER independiente para certificación multi-vía del sello |
| **python-phonenumbers** | Apache-2.0 | :466 | F2·F8·F22 | Metadata E.164 ~250 regiones + `is_valid_number`; mata false-accept FR/PT y rechazos DE/IT/MX/JP |
| **pycountry** | LGPL-2.1 (build-time) | :530 | F3·F9·F10·F19·F22 | Autoridad ISO 3166-1/-2; valida cc de tenant/cdp y deriva caps del seal-manifest |
| **anyascii** | ISC | :224/:329/:482 | F4·F5·F7·F15 | Transliteración no-destructiva (cierra el ASCII-fold doble-fallo B7/B16), comercial-limpia vs unidecode/GPL |
| **LaBSE / BGE-M3** | Apache-2.0 | :455-461 | F4·F10 | Blocking semántico multilingüe (recall capa-2 antes del normalizador del país) |
| **Splink** | MIT | :447-453 | F11·F14 | Pesos Fellegi-Sunter aprendidos desde el dato (reemplaza los `PROB_*` ASSUMED) |
| **libpostal** | MIT | :471-477 | F6·F15·F21 | Parser de direcciones 100+ países (guard de sucursal cross-mercado) |
| **python-stdnum** | LGPL-2.1 | :487-493 | F16·F20 | Validación registral/VAT con dígito de control (`{scheme}:{validated}` country-proof) |
| **Great Expectations / Pandera** | Apache-2.0/MIT | :164-170 | F12·F13 | Contrato de datos PRE-sello, falla CERRADO (reemplaza el `sys.exit(1)` de censo) |
| **Pydantic** | MIT | :587-590 | F12 | Country-pack tipado en CI; biyección `source_health↔registry` (0 UNMAPPED/ORPHAN) |
| **ER-Evaluation** | AGPL-3.0 (offline/port) | :519-525 | F13·F19 | Cardinalidad CERTIFICADA con intervalos por país (el censo encoge el margen, no detona) |
| **datasketch + RapidFuzz** | MIT | :535-541 | F10 | LSH sub-cuadrático language-neutral (retira el O(n²) de edge-4, sin cap 500) |
| **Snorkel** | Apache-2.0 | :511-517 | F6 | Descubre el roster de cadenas de cada mercado desde el dato (mata la denylist a mano) |
| **in-toto + cosign + rekor** | Apache-2.0 | :140-147 | F17·F24 | Atestación firmada per-country del sello (transparency log no-repudiable) |
| **DVC** | Apache-2.0 | :148-154 | F24 | Inputs content-addressed; `dvc repro` = rebuild post-rollback byte-idéntico |
| **GLEIF LEI Golden Copy** | CC0 1.0 | :172-178 | F20 | Id registral global de dominio público (ortogonal cross-border día-uno) |

---

## Mejoras a nivel inalcanzable (€0, priorizadas)

> Todas €0. Orden: esfuerzo S → M → L. Cada una endurece sin pedir cartera. La columna F# liga a su sub-proyecto.

| Prioridad | Mejora | Por qué no se hizo (causa) | Esfuerzo | F# |
|---|---|---|---|---|
| 1 (S) | **Unificar las 5 (6) copias de `UnionFind`** en `pipeline/identity/union_find.py`. Quita el drift **real** (halving↔two-pass, `_parent/_rank`↔`_p/_r`) en la primitiva más load-bearing. | Duplicación acretada por campañas incrementales; ningún test forzó consolidar. | S | F1 |
| 2 (S) | **Retirar el normalizador phone legacy** de `resolve_entities.py:135` delegando en la autoridad única, cerrando la costura frágil antes de servir la capa beta. | `resolve_entities` es beta no-servida → su copia frágil nunca estuvo en el camino crítico. | S | F8 |
| 3 (S) | **CI fail-fast**: todo `country_code` en `entity` DEBE tener `IdentityLocale` registrado y todo `source_key` clasificado, si no el job se niega a correr. | DB single-tenant hizo el check vacío; solo importa con >1 país. | S | F22·F12 |
| 4 (S) | **Promover los caps over-merge** a un **seal manifest country-parametrizado** (`KNOWN_REAL_MAX_*` per-país), una fila de config por país. | Caps hardcoded a los máximos medidos de ES; la red single-tenant nunca lo exigió. | S | F19 |
| 5 (M) | **Extraer el pack `IdentityLocale` + registry** y enhebrar `country_code` (default ES) por los 3 normalizadores → país nuevo = un archivo declarativo. | ES era el único tenant; los normalizadores hard-codearon ES inline y se copy-pastearon. | M | F22·F4·F6 |
| 6 (M) | **Autoridad E.164 genérica** vía tabla `PhonePlan` per-país, clave = E.164 completo para hacer la arista phone segura en índice pan-UE. | `phone_es` se escribió €0/sin-dependencia solo para ES; la generalización necesita la abstracción de locale primero + un golden por país. | M | F2 |
| 7 (M) | **Autoridad de dirección per-locale** (libpostal) para que el guard de sucursal funcione cross-país, reemplazando el alnum-strip naíf. | Desambiguar sucursal-vs-dupe por dirección es marginal en ES (muni+nombre carga la señal) → se difirió a un strip de string. | M | F21 |
| 8 (L) | **Adjudicador capa-2 local-LLM** solo para los grupos `excluded_ambiguous` irreducibles, proponiendo merges para gate humano/Claude — **nunca auto-aplicado**. | Hoy capa-2 = 0; el motor deja ambiguos sin fundir a propósito. Necesita caso de uso probado y queda gateado (€0 si corre en hardware existente). | L | F14·F23 |

---

## Riesgos / open items

1. **False-merge cross-country en DB compartida** (B2/F10): si B1 sigue country-unscoped (`cluster_dealers.py:59`) y dos países reusan muni-code-strings solapados, las aristas pueden puentear tenants. **Mitigación:** country-scope de la corrida **Y** claves phone E.164 (CC-prefijadas); los muni-codes también deben diferir por autoridad (MP8/Geo-6). **Estado: abierto hasta aplicar el fix estructural.**
2. **Re-key accidental de ES** (detonación del invariante inmutable, F7): cualquier cambio que deje filtrar `country_code` a la pre-imagen hash de `canonical_key` (`codes.py:56`) re-mintea cada `cdp_code` ES. El país **DEBE** quedar prefix-only. **Mitigación:** golden byte-identity test (Hypothesis). **[VERIFIED `codes.py:62-65` confirma exclusión deliberada hoy]**.
3. **Fallback silencioso de locale** (F22): una entity extranjera normalizada por el locale ES (sin entrada en registry) produce claves erróneas en silencio. Sin el CI fail-fast (mejora 3) es invisible hasta que el over/under-merge aflora aguas abajo.
4. **Asserts censo-sensibles** (B18/F13 + caps de F19): son punto-en-el-tiempo; un país nuevo (o crecimiento ES) los dispara. Diseñados para warn+re-verify, pero un `--force` descuidado pasada una divergencia real sellaría un over-merge. **Ligado a OI-1.** `[CORRIGE v1]` el código de `build_canonical_dedup` es **FATAL** hoy (`sys.exit(1)`), no warn — se corrige a lo que el doc promete.
5. **Peligro de activación de la capa beta** (F8): servir `resolve_entities` con su normalizador frágil last-9 vivo y el city-guard global ASCII-ciego podría inyectar aristas phone falsas y over-merges JP; **arreglar la delegación + el city-guard (mejora 2 / SH8) ANTES** de gatear esa capa.
6. **La costura compartida cdp-code/stage-04** (F3): el literal `CDP-ES-` (**62 archivos [VERIFIED grep=62]**) + la regex `complete.py:89` — ensanchar solo la regex sin enrutar los literales por `mint_code` deja entities de país #2 fallando la completion 5-gate en otro sitio (61 trampas vivas).
7. **Stack CAÍDO al auditar** (PG `:5433` cerrado) → todos los conteos vivos son punto-en-el-tiempo; el sello per-país debe re-verificarse contra DB corriendo, no confiarse de números de recon. **= OI-1.**
8. **OPEN: capa-2 LLM gateada** (OI-2) — GASTO/GPU + caso probado + firma. No bloquea el loop; espera en PENDING-OWNER.
9. **OPEN: MP8 contrato geo** (OI-3) — dependencia cross-etapa con Geo (6); se cierra en conjunto.

> **Cierre honesto.** Veredicto del inquisidor: **NEEDS_REWORK**. Las **37 roturas** (B1–B19 + MP1–MP10 + SH1–SH8), ahora bajadas al átomo en **24 sub-proyectos-360**, tienen **resolución de diseño €0** —fixes estructurales one-time + pack `IdentityLocale` per-país + invariante single-country— **sin re-key de ES ni reescritura del motor**. Tres acarrean gating/dependencia declarada y **no se cierran solo en aislamiento de identidad**: **MP8/OI-3** (contrato geo del muni-code, cierra junto con Geo-6), **OI-1** (re-verificar contra DB viva — stack caído al auditar) y **OI-2** (adjudicador capa-2 LLM — €>0, PENDING-OWNER). Ninguna rotura se transcribe como sana: la contradicción doc↔código de `build_canonical_dedup` (B18/F13, `:96` "non-fatal" vs `:463` `sys.exit(1)` FATAL), el drift `rep=MIN(cdp)` (F14), la divergencia ya-viva de la clave residual (F15) y las 5-6 copias divergentes de UnionFind (F1) se integran como **defectos reales** y se resuelven corrigiendo el código a la verdad. El motor de identidad **es** genérico; lo que falta es **desincrustar el pack y enhebrar el país por debajo del esquema** — exactamente el hallazgo transversal de la espina dorsal.
