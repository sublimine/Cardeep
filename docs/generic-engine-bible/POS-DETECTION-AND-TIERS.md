# Detección de Punto de Venta + Taxonomía de Tiers/Grupos
> Capítulo transversal · Ola 2.5 · 2026-06-27 · El **hogar canónico** de "¿qué es un punto de venta?" y de cómo se clasifica todo lo descubierto. Las etapas lo consumen; aquí se define. Mandato owner: **separar Tier-1 de los demás grupos y organizar TODO con lógica total.**
>
> **Honestidad de ejecución (BLINDAJE).** Stack vivo CAÍDO → ninguna cifra es verificable en vivo ahora; **todo conteo de DB es punto-en-el-tiempo** (fechado donde se cita). Cada afirmación de estructura es `[VERIFIED path:línea]` (leída en la fuente) o `[ASSUMED]`. Si memoria y código discrepan, gana el código.
>
> **Dónde encaja en el funnel.** Esta es la columna que las etapas 1 (descubrir), 2 (scrapear), 4 (identidad), 7 (sello) y 8 (servir) referencian para no re-inventar el predicado de punto-venta ni la taxonomía. Cruces: el numerador del sello vive en [`stages/07-quality-seal.md`](stages/07-quality-seal.md); la escalera de fetch por tier en [`stages/02-scrape.md`](stages/02-scrape.md); el des-cegado de país en [`SPINE-COUNTRY-THREADING.md`](SPINE-COUNTRY-THREADING.md) y el invariante anti-false-merge en [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md).

---

## Por qué es de primera clase (no distribuido)

"¿Qué es un punto de venta?" es la pregunta de la que cuelga **toda** cifra pública del censo: el headline "Puntos de venta", lo que pagina el explorador, el numerador del sello, la cobertura por provincia. Si la respuesta vive **distribuida** —re-derivada con un predicado distinto en cada superficie— el sistema miente sin querer: el titular nunca cuadra con lo paginado, y el sello certifica un universo que el usuario no ve.

Eso es exactamente lo que pasó y lo que el owner cazó: **el público "Puntos de venta" estaba inflado ~2,9x** y la auditoría de calidad encontró **tres superficies con tres scopes distintos** `[VERIFIED migrations/0056_v_servable_dealer.sql:5-10]`. Hoy conviven **seis** respuestas a la misma pregunta (ver [§El gate canónico](#el-gate-canónico-qué-es-un-pdv) y [§Costuras](#costuras-es→fix-tabla-consolidada)).

La doctrina de este capítulo: **el punto de venta es un concepto de primera clase — UNA vista canónica que todas las superficies leen— no una propiedad que cada router recalcula.** Es la misma genialidad del VAM-por-triggers y del [`COUNTRY-PROOF-INVARIANT`](COUNTRY-PROOF-INVARIANT.md): *no documentar la regla — hacer que la máquina la imponga.* Cuando el gate es de primera clase, `numerador == paginado == scope-certificado` se cumple **por construcción**, no por coincidencia ni por disciplina del que toca el código.

El motor genérico ya tiene esa vista de primera clase escrita —`v_servable_dealer` (0056)— pero **NO CABLEADA**: existe y nadie la lee. `grep v_servable_dealer` en `services/api/` = **0 hits** `[VERIFIED migrations/0056_v_servable_dealer.sql:26-37; stages/08-serve.md:39 ("ningún router la referencia ... grep ... = 0")]`. Es una definición huérfana mientras el número de cara al usuario lo sigue produciendo un predicado inline distinto. Cerrar esa brecha —cablear la canónica como ÚNICO numerador— es el eje de este capítulo y el OPEN ITEM central compartido con el sello (B8 en [`07-quality-seal.md`](stages/07-quality-seal.md)).

---

## El gate canónico (qué ES un PdV)

El punto de venta canónico se construye con **cuatro gates apilados**, cada uno invariante (mecánico) y reutilizable por país. La vista canónica `v_servable_dealer` los compone:

```sql
-- [VERIFIED migrations/0056_v_servable_dealer.sql:26-37]
CREATE OR REPLACE VIEW v_servable_dealer AS
SELECT se.entity_ulid, se.cdp_code, se.kind, vdr.resolved_cdp_code,
       EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid) AS has_inventory
  FROM servable_entity se
  JOIN v_dealer_resolved vdr ON vdr.entity_ulid = se.entity_ulid
 WHERE se.status = 'active'
   AND se.kind::text NOT IN ('particular', 'desguace')
   AND (se.kind::text <> 'garaje'
        OR EXISTS (SELECT 1 FROM servable_vehicle sv WHERE sv.entity_ulid = se.entity_ulid));
```

| Gate | Qué impone | Dónde vive (verdad del código) |
|---|---|---|
| **G1 · Publicación de entidad** | La entidad es servible: NO tombstoned/cerrada y SIN cuarentena abierta. Deja pasar `active` **y** `unverified`. | `servable_entity`: `status NOT IN ('evicted','closed') AND NOT EXISTS(open quarantine)`; hoy 380.622 active + 11.322 unverified = 391.944 `[VERIFIED migrations/0046_servable_entity_status_filter.sql:17-29]` |
| **G2 · Membresía de kind** | Vende coches: `kind ∉ {particular, desguace}` y `garaje` solo condicional. En la canónica además exige `status='active'` (excluye `unverified`). | `[VERIFIED 0056:34-37]` |
| **G3 · Existencia de inventario** | Punto de venta **ACTIVO con stock**: `EXISTS servable_vehicle`. Obligatorio para `garaje`; marcado por `has_inventory` para todos. | `servable_vehicle`: `status='available' AND (price>0 OR NULL) AND NOT cuarentena` `[VERIFIED migrations/0045_servable_status_filter.sql:23-33]` |
| **G4 · Dedup de identidad** | Un dealer real = un registro: `count(DISTINCT resolved_cdp_code)`. Sin él, el numerador se infla ~2x. | `v_dealer_resolved` = B1 (`v_canonical`) ∘ super-canónico (`canonical_dedup`) `[VERIFIED migrations/0028_dealer_resolved.sql:35-76]`; el ~2x en `[VERIFIED migrations/0042_province_seal_view.sql:10-12 (164,9% vs 79,4%)]` |

**`has_inventory` es la bisagra honesta:** separa "entidad descubierta" (cascarón vacío) de "punto de venta activo con stock". Conteos honestos declarados en la propia vista (live 2026-06-23, **punto-en-el-tiempo**): directorio `count(DISTINCT resolved_cdp_code) ≈ 36,3k`; con inventario `WHERE has_inventory ≈ 18,3k`. El viejo 54.587 mezclaba ~35k cascarones vacíos + ~2,3k desguaces; los particulares (352k listados de plataforma) **nunca** fueron puntos de venta `[VERIFIED 0056:17-20]`.

> **Por qué riesgo-cero:** una VIEW es una query guardada — no toca fila, FK ni `cdp_code` servido. `CREATE OR REPLACE` es idempotente; rollback = `DROP VIEW` `[VERIFIED 0056:22-24,45-46]`. Cablearla al serving público sí cambia una cifra de cara al usuario ⇒ pasa por **dry-run(:5434)→golden→Ferrari→CI** (gate ESCRITURA-EN-SERVING, §00-MASTER).

---

## Ontología de kind

`entity_kind` es un **enum cerrado de 12 valores** (no string libre): 11 en `[VERIFIED migrations/0005_types_and_guards.sql:13-18]` + `particular` añadido en `[VERIFIED migrations/0017_particular_kind.sql:21]`. El enum cerrado es el primer anti-alucinación: el clasificador es físicamente incapaz de emitir un kind fuera de vocabulario.

| Clase respecto al gate | kinds | Trato en el gate canónico |
|---|---|---|
| **(a) Núcleo-PdV — siempre cuenta** | `concesionario_oficial`, `agente_oficial`, `compraventa` | Pasa G2; cuenta si tiene inventario |
| **(b) Condicional por inventario** | `garaje` (taller) | Solo es PdV si `EXISTS servable_vehicle` `[VERIFIED 0056:36-37]` |
| **(c) Canales / otros** — no excluidos hoy, pero no son PdV-coche-retail puro | `plataforma`, `subasta`, `importador`, `oem_vo_portal`, `rent_a_car_vo`, `cadena`[DEPRECATED] | Pasan G2 (no están en la exclusión dura); su semántica de PdV es ambigua → ver [Rechazo de ruido](#rechazo-de-ruido-precisión) |
| **(d) Excluidos duros** | `particular` (listado C2C de plataforma, no punto de venta físico/digital), `desguace` (vende piezas, no coches) | `kind NOT IN ('particular','desguace')` `[VERIFIED 0056:35]` |

**Precedencia de kind (`kind_source`, autoridad de la clasificación):** `registral / oem_locator / legal_census / curated_brandlist` > `classifier` > `platform_label` (+ `manual`) `[VERIFIED 0005:34-39]`. Una etiqueta de plataforma jamás pisa a un dato registral; el desacuerdo escala, no improvisa (BLINDAJE §2.3).

**`sells_cars` — diseño vs implementación (incoherencia real).** La columna nació como gate de negocio: `NULL`=desconocido, `FALSE`=taller puro filtrado del numerador (D-4) `[VERIFIED migrations/0006_entity_evolve.sql:34]`, con índice `idx_entity_sells WHERE sells_cars IS NOT FALSE` `[VERIFIED 0006:59]`. **Pero el gate canónico NO la usa** — usa `kind` + `EXISTS inventario`. Y el dato está incoherente: 596 desguaces con `sells_cars=true` y 0 inventario `[VERIFIED docs/recon/AUDIT_2026-06-15.md:64]`; 7.201 garajes con `sells_cars=NULL` `[VERIFIED :82]`. Es un eje muerto que confunde: o se cablea con datos saneados, o se retira (ver [Open items](#open-items)).

---

## Rechazo de ruido (precisión)

La precisión del censo es **qué SALE** tanto como qué entra. Reglas de rechazo, todas verificadas en el gate:

- **`particular` (C2C):** un anuncio de particular es inventario real (un coche que un comprador puede comprar) y se sirve con delta/historial completo `[VERIFIED migrations/0017_particular_kind.sql:1-19]`, **pero no es un punto de venta**: es un listado sobre un canal (la plataforma). 326.443 entidades `particular` vivas (2026-06-13, punto-en-el-tiempo) `[VERIFIED docs/research/SEGMENT_TAXONOMY.md:32-34]` quedan fuera del PdV por `kind NOT IN ('particular',...)`.
- **`desguace` (piezas):** vende despiece, no coches enteros; excluido del PdV. Su cobertura se mide aparte como **descubrimiento** (¿encontramos al menos el censo oficial?), no como venta servida — ver [Taxonomía de grupos](#taxonomía-de-grupossegmentos) y el segmento `desguace` del sello `[VERIFIED migrations/0043_province_seal_desguace.sql:1-11]`.
- **Cascarón vacío:** cualquier kind sin `servable_vehicle` es "entidad descubierta", no "PdV activo". G3 lo degrada (no aparece en `has_inventory`).
- **Tombstoned / cerrada / en cuarentena:** `evicted`, `closed` y cuarentena abierta desaparecen de toda superficie servida **mecánicamente, no por promesa** `[VERIFIED 0046:17-29]`.
- **`garaje` sin inventario:** taller sin coches en venta — rechazado por G2/G3 combinados `[VERIFIED 0056:36-37]`.

Dos principios de precisión que evitan **inflar** el censo con falsos operadores:

1. **El estado-de-vehículo es un FILTRO, no un canal.** La mayoría de keywords de coche usado (`km0`, `seminuevos`, `coche de gerencia`, `demo`, `outlet`) son **estados/atributos** del vehículo vendidos por los **mismos** canales ya censados (concesionario, compraventa, portal OEM-VO); conectarlos suma **cero** operadores netos `[VERIFIED docs/research/SEGMENT_TAXONOMY.md:63-84]`. Fabricar un PdV a partir de un estado sería ruido.
2. **La plataforma es UN canal, no N puntos de venta.** Un marketplace es una superficie de distribución; los puntos de venta son los dealers que publican en ella (de-duplicados cross-plataforma por G4), no la plataforma multiplicada por sus anuncios.

---

## Taxonomía de Tiers

> Mandato owner explícito: **"separar Tier-1 de los demás grupos."** El eje "Tier" **NO** es tamaño ni importancia comercial — es **postura de defensa anti-bot** (dificultad de scrapeo). Es ortogonal a `kind` (qué vende) y a `source_group` (qué familia).

**Definición canónica de Tier-1 `[VERIFIED docs/architecture/00-TIER1-REGISTRY.md:42-48]`:** una plataforma es **TIER-1 sii pone un muro de bot real** entre nosotros y sus datos (sensor Akamai, Cloudflare managed-challenge, GeeTest, Imperva activo, DataDome). Un gigante de 700k anuncios que sirve HTML a un `curl` Chrome-UA es **OPEN** y se ataca en el motor long-tail; un portal OEM de 50k tras Akamai es **TIER-1** y vive en su propio frente `countries/ES/_tier1/`. Esa es exactamente la separación que el owner pidió "antes de cualquier ataque".

**Historia del eje (de binario a granular):**
- `entity.is_tier1 BOOLEAN NOT NULL DEFAULT FALSE` — el flag original, "hard separation of hard-defense platforms" `[VERIFIED migrations/0002_entities.sql:26]`, con índice parcial `WHERE is_tier1=TRUE` `[VERIFIED 0002:39]`.
- `defense_tier` ENUM granular **reemplaza el booleano plano** (is_tier1 queda como flag derivado de conveniencia) `[VERIFIED migrations/0016_tiering_groups.sql:4-13]`:

| `defense_tier` | Muro | Motor de fetch que lo vence |
|---|---|---|
| `t0_open` | Sin muro real: JSON API abierta, sitemap, registro, OEM API | Tier-0 `curl_cffi` (impersonación coherente) |
| `t1_soft` | WAF presente pero sirve a `curl_cffi` (Cloudflare permisivo, Imperva-serving) | Tier-0 con perfil/fingerprint |
| `t2_js_challenge` | Necesita navegador stealth para minar cookie / pasar JS (DataDome, Imperva reese84) | Tier-1 navegador (cookie-reuse) |
| `t3_hard_sensor` | Sensor activo (Akamai/Kasada/PerimeterX) — stealth-Chromium gratis aún lo crackea | Tier-1 navegador + humanización |
| `t4_spend_gated` | Solo residencial/sensor de pago tras agotar TODOS los vectores libres | **Gate GASTO** (firma owner) |

**Cómo lo consume el motor (cross-ref [`stages/02-scrape.md`](stages/02-scrape.md)):** la escalera de fetch arranca Tier-0 `curl_cffi` → rota fingerprint en ban → escala a Tier-1 navegador que resuelve el challenge **una** vez y mina cookie de clearance reutilizable `[VERIFIED stages/02-scrape.md:18,23; pipeline/engine/fetch.py]`. Hay 14 recetas Tier-1 en `countries/ES/_tier1/` `[VERIFIED stages/02-scrape.md:32]`. El `t4_spend_gated` es la frontera €0: por debajo, todo se cubre con vectores libres; en él, se parquea en el gate GASTO sin parar el loop.

**Por qué la separación importa al censo (no solo al scrapeo):** Tier-1 concentra el inventario de mayor volumen (los marketplaces, los portales OEM) detrás de los muros más caros; tratarlo como "un grupo aparte" permite (a) asignarle el motor caro solo a él, (b) que Claude cace sus recetas en ráfaga (capa-3, §00-MASTER), y (c) no quemar latencia probando Tier-0 inútil en hosts `t2+`. El long-tail OPEN (la web del taller de montaña, `t0_open`) se cubre con el motor barato masivo.

---

## Taxonomía de grupos/segmentos

`source_group` es el eje **"grupos"**: qué CLASE de fuente/operador es la entidad, **por encima** de su `kind`. Enum de 11 valores `[VERIFIED migrations/0016_tiering_groups.sql:16-30]`:

| `source_group` | Qué agrupa | Conteo live 2026-06-13 (punto-en-el-tiempo) |
|---|---|---|
| `marketplace_generalist` | C2C+pro generalista (wallapop, milanuncios) | 2 |
| `marketplace_motor` | Marketplaces de coche (coches.net, AutoScout24, autocasion, coches.com, motor.es) | 1.323 |
| `oem_vo_portal` | Portales OEM certificado-usado (renew, DasWeltAuto, Spoticar, MB Certified) | 5.769 |
| `oem_dealer_network` | Localizadores de red OEM (Kia/MG/BYD/Škoda/Dacia/Hyundai/Mercedes/SEAT APIs) | 1.526 |
| `chain` | Retailers multi-sucursal (Flexicar, OcasiónPlus, Clicars, Autohero) | 189 |
| `rentacar_vo` | Rent-a-car vendiendo ex-flota (OK Mobility, Centauro, Record) | 6 |
| `official_registry` | DGT, BORME, INE, datos.gob, registros CCAA (+ subastas) | 99 |
| `association` | FACONAUTO, GANVAM, AEDRA, AMDA, Gremi… | 409 |
| `directory` | Páginas Amarillas, OSM, FSQ, Overture, directorios genéricos | 9.953 |
| `desguace_network` | AEDRA / DesguacesDirecto / redes de desguace | 1.292 |
| `long_tail_web` | La web propia de la entidad (el taller de montaña) | (NULL en long-tail/particular) |

`[VERIFIED conteos docs/research/SEGMENT_TAXONOMY.md:36-39]`

**Ejes ortogonales (la "lógica total" que el owner pidió).** Una entidad se clasifica en **cuatro ejes independientes** — confundirlos es la raíz de los scopes divergentes:

| Eje | Pregunta que responde | Tipo | Fuente |
|---|---|---|---|
| `kind` | ¿Qué vende / qué es? | enum 12 | `[VERIFIED 0005:13-18 + 0017:21]` |
| `source_group` | ¿De qué familia de fuente viene? | enum 11 | `[VERIFIED 0016:16-30]` |
| `defense_tier` (+`is_tier1`) | ¿Cómo está defendida? (scrapeo) | enum 5 | `[VERIFIED 0016:5-13; 0002:26]` |
| `role` | ¿Qué posición ocupa en el grafo de mercado? | enum 6: `platform, dealer_network, chain, standalone_pos, registry, directory` | `[VERIFIED 0016:33-35]` |

A nivel de organización (cadenas/grupos/marcas/operadores) hay un quinto eje, `org_type` (6 valores: `chain_compraventa, dealer_group, rentacar_brand, oem, auction_operator, platform_operator`) `[VERIFIED 0005:21-26]`.

**Segmento de inventario (sobre la arista, no la entidad):** `platform_listing.segment` distingue el estado del stock — `used` 1.432.777 · `new` 8.380 · `km0` 3.107 · `renting` 1.212 (2026-06-13, punto-en-el-tiempo) `[VERIFIED docs/research/SEGMENT_TAXONOMY.md:41]`. Esto materializa el principio "estado = filtro, no canal": el segmento vive en la arista de listado, no crea un kind nuevo.

---

## Pipeline detección→clasificación→sello

El recorrido de un átomo, de descubrimiento a cifra certificada, y dónde se asigna cada eje:

```
DESCUBRIR ─► CLASIFICAR ─────► PUBLICAR ─► INVENTARIO ─► DEDUP ─► PdV CANÓNICO ─► SELLO
(stage 1)    (4 ejes)          (G1)        (G3)          (G4)     (v_servable_     (numerador /
                                                                   dealer)          denominador)
  │            │                 │            │             │          │               │
  │            │                 │            │             │          │               └─ v_province_seal:
  │            │                 │            │             │          │                  venta = compraventa+
  │            │                 │            │             │          │                  concesionario_oficial
  │            │                 │            │             │          │                  ∧ available / DIRCE-451
  │            │                 │            │             │          │                  desguace = hallados /
  │            │                 │            │             │          │                  censo DGT-CAT
  │            │                 │            │             │          └─ has_inventory parte
  │            │                 │            │             │             PdV-con-stock de cascarón
  │            │                 │            │             └─ resolved_cdp_code (B1∘super-canónico)
  │            │                 │            └─ EXISTS servable_vehicle (available∧price∧no-cuarentena)
  │            │                 └─ status∉{evicted,closed} ∧ no-cuarentena (deja unverified)
  │            └─ kind (precedencia kind_source) · source_group · defense_tier/is_tier1 · role
  └─ adaptadores por fuente (registro, mapas, dorks) → DiscoveredEntity → mint cdp_code + cuórum VAM
```

- **Clasificar** asigna los 4 ejes con su precedencia; el `kind` con autoridad `kind_source`, el `defense_tier`/`source_group`/`role` por el conector de plataforma o el clasificador (cross-ref [`stages/01-discover.md`](stages/01-discover.md), [`stages/02-scrape.md`](stages/02-scrape.md)).
- **Publicar→Inventario→Dedup** son los gates G1/G3/G4; los aplica la vista canónica.
- **Sello** consume el PdV canónico como **numerador**; el detalle de denominadores (registral DIRCE-CNAE451 para venta, censo DGT-CAT para desguace) y verdicts (SELLADO≥85 / PARCIAL 50-85 / GAP<50 / NO_DENOM) vive en [`stages/07-quality-seal.md`](stages/07-quality-seal.md) `[VERIFIED migrations/0042_province_seal_view.sql:18-44; 0043:16-66]`.

**El defecto estructural de hoy:** este pipeline ideal no está cableado. El numerador que llega al sello (`compraventa+concesionario_oficial`, 0042:24) **no es** el PdV canónico (`v_servable_dealer.has_inventory`), y el número público (`stats.dealers`) usa un **tercer** predicado inline. La detección y la clasificación existen; el "→sello" usa una definición distinta en cada salto. Cablear `v_servable_dealer` como el ÚNICO PdV que fluye a stats/geo/sello es lo que vuelve este diagrama real.

---

## Country-proof (no cruzar/mal-clasificar por país)

Esta faceta es el **cuello de botella country-proof de TODO el censo**. Hay dos modos de fallo, ambos activos hoy:

### (1) Ciego entre países — fuga silenciosa de la cifra pública
`country_code CHAR(2) NOT NULL DEFAULT 'ES'` ya existe en `entity` + backbone geo `[VERIFIED migrations/0052_country.sql:51-54]`, y el PK geo se promovió a compuesto `(country_code,code)` con FKs reescritos en 0053 `[VERIFIED stages/08-serve.md:37]`. **Pero el gate es ciego al país:**
- `servable_entity` (0046) **no proyecta** `country_code` (proyección de 37 columnas, sin país) `[VERIFIED 0046:18-23]`.
- `v_servable_dealer` (0056) **no lo expone ni filtra** `[VERIFIED 0056:26-37]`.
- `stats.dealers` agrega a una **única fila** `product_stats WHERE id=1` `[VERIFIED services/api/routers/ops.py:86-89]`, sin `GROUP BY` país.
- El sello agrupa solo por `province_code` `[VERIFIED 0042:28]`, sin país.

**Consecuencia:** en cuanto entre un 2º país, **TODAS** sus filas se pliegan en la misma fila `product_stats` y en el mismo numerador del sello — sumando manzanas de DE con peras de ES en una sola cifra, **sin error, solo mal**. El `DEFAULT 'ES'` es además una trampa de ruido: una entidad mal atribuida hereda 'ES' en silencio.

### (2) Mal-clasificación — taxonomía ES incrustada
El predicado son **literales kind ES** soldados en SQL y código (`'particular'`, `'desguace'`, `'garaje'`, `'compraventa'`, `'concesionario_oficial'`). La taxonomía de otro mercado no mapea 1:1: un *Schrottplatz* alemán no es la cadena de bytes `'desguace'`, así que la exclusión hardcodeada **no dispara** (los desguaces se cuelan como PdV) o el numerador del sello (2 kinds ES) cae a **0** (país sellado como GAP falso). Ver los breaks DE/FR/IT/PT en [Open items](#open-items).

### El ángulo correcto (diseño genérico)
El gate debe ser **UNA vista canónica con predicado-como-parámetro-de-pack** y `country_code` como **clave de partición obligatoria**:
- **Predicado como parámetro:** el pack de país declara tres conjuntos sobre **su** taxonomía — `SALE_POINT_KINDS` (núcleo que siempre cuenta), `EXCLUDED_KINDS` (rechazo duro: C2C + scrapyard-equivalente), `INVENTORY_REQUIRED_KINDS` (condicionales tipo garaje/taller). El motor **no hardcodea** literales: lee el pack.
- **Partición país:** `country_code` proyectado en `servable_entity`→`v_servable_dealer` y clave de `GROUP BY` en TODO conteo público; `product_stats` con PK `(country_code)` en vez de `CHECK(id=1)`; `v_province_seal` agrupando por `(country_code, province_code)`.
- **Denominador por pack:** el sello necesita un techo registral (DIRCE-CNAE451 en ES) y un censo de scrapyards (DGT-CAT en ES) como **adaptadores** por país; sin pack → verdict `NO_DENOM` honesto, nunca un 0 silencioso.
- **Un solo lector:** stats/geo/sello leen `v_servable_dealer.<has_inventory>` filtrada por `country_code` ⇒ `numerador==paginado==scope-certificado` **por construcción, en cualquier país.**

> Complementa —no duplica— a [`COUNTRY-PROOF-INVARIANT.md`](COUNTRY-PROOF-INVARIANT.md): aquel blinda el **false-merge cross-border** en identidad (G4); este blinda el **predicado y la partición** del gate (G1-G3 + agregación). Juntos cierran "no cruzar" **y** "no mal-clasificar".

---

## Verificación multi-vía + golden

VAM cero-confianza aplicado al gate. **Estado hoy: parcial y tautológico.**

- **2ª-vía existente, pero tautológica:** el test recomputa el **MISMO** predicado de `stats.py` contra sí mismo y asegura `abs(dealers - vdr_count) <= _DEALER_COUNT_TOLERANCE` `[VERIFIED tests/test_api_gaps.py:203-222]`, con `_DEALER_COUNT_TOLERANCE = 200` `[VERIFIED tests/test_api_gaps.py:144]`. No compara contra la vista **canónica**: no detectaría divergencia entre el número servido y `v_servable_dealer`, ni una re-inflación si alguien cambia el predicado en ambos sitios a la vez.
- **Precompute == live:** `/stats` lee `product_stats` con fallback a `compute_counts` (mismo SQL) `[VERIFIED services/api/routers/ops.py:78-98]` — verifica caché-vs-cálculo, no predicado-vs-canónica.

**Lo que falta (criterios de aceptación de este capítulo):**
1. **2ª-vía INDEPENDIENTE:** recomputar el conteo desde la vista **canónica** (`v_servable_dealer.has_inventory` por país) y exigir igualdad con lo servido.
2. **Golden de equivalencia:** aplicar 0056 en dry-run `:5434` y probar que el conteo reproduce la cifra honesta (~19,1k `[VERIFIED services/api/stats.py:18-21]`) **± delta EXPLICADO línea-a-línea** (fuentes esperadas del delta: la regla `garaje`-con-inventario, el colapso de dedup G4, y el eje `active`-vs-`unverified` que separa `stats.py` —que no filtra status— de la canónica —que exige `active`—), con hash-golden congelado, **antes** de tocar `:5433`.
3. **Gate de coherencia cross-scope:** un test que **falle** si `stats.dealers ≠ numerador-venta-del-sello ≠ v_servable_dealer.has_inventory` (hoy divergen ~19,1k / ~18,3k / ~18,3k, y geo usa un 4º universo).
4. **Gate de escritura:** cablear la canónica cambia una cifra de cara al usuario ⇒ **dry-run→golden→Ferrari→CI** `[VERIFIED stages/07-quality-seal.md:136]`.

**Limitación dura (BLINDAJE):** stack vivo CAÍDO ⇒ ningún conteo es verificable en vivo ahora; toda cifra de este capítulo es **punto-en-el-tiempo** de docs/migraciones. La cifra precisa "19.144" que circula en plans es `[ASSUMED]` (no re-derivada en fuente); lo verificado es el predicado y el orden de magnitud ~19,1k `[VERIFIED stats.py:18-21]`.

---

## Costuras ES→fix (tabla consolidada)

Las 7 costuras donde la taxonomía/gate está soldada a ES, cada una verificada, con su fix genérico:

| # | Localización | Costura (ES-hardcoded / defecto) | Fix |
|---|---|---|---|
| 1 | `services/api/stats.py:22-28` | El número SERVIDO (~19,1k) reimplementa el gate **inline** con literales ES, hace JOIN a `entity` CRUDA (sin gate de status → cuenta `unverified`-con-stock), sin país. Es el predicado de cara al usuario y **NO es el canónico** `[VERIFIED]` | Repuntar a `SELECT count(*) FROM v_servable_dealer WHERE country_code=$1 AND has_inventory` tras probar equivalencia en `:5434`; eliminar los literales del código |
| 2 | `migrations/0056_v_servable_dealer.sql:35-37` | La vista CANÓNICA hardcodea literales kind ES y está **NO CABLEADA** (0 lectores); el predicado vive en SQL, no en un pack; no proyecta ni filtra `country_code` `[VERIFIED]` | Parametrizar `EXCLUDED_KINDS`/`INVENTORY_REQUIRED_KINDS` vía tabla/función de pack; añadir `se.country_code` a la proyección + índice; cablearla como ÚNICO numerador |
| 3 | `services/api/routers/geo.py:51-62` | Completeness usa `kind <> 'particular'` a secas (incluye desguace + cascarones): **4º scope** divergente del de stats `[VERIFIED]` | Derivar numerador/denominador de completeness desde `v_servable_dealer` (mismo predicado) |
| 4 | `services/api/routers/geo.py:378-391` | El árbol `/geo/{prov}/tree` hardcodea **9 literales kind ES** en `FILTER(WHERE e.kind=...)` `[VERIFIED]` | Generar las facetas de kind desde el catálogo de kinds del pack, no desde literales |
| 5 | `migrations/0042_province_seal_view.sql:24` + `0043_province_seal_desguace.sql:22,34` | Numerador del sello usa SOLO `kind IN (compraventa,concesionario_oficial)` (**5º scope**, más estrecho que el canónico); denominadores ES: DIRCE-CNAE451 (venta) y `source_key='dgt_cat'` (desguace) `[VERIFIED]` | Numerador = `v_servable_dealer.has_inventory` por país; denominadores como adaptadores de pack (`registral_ceiling`, `scrapyard_census`) |
| 6 | `migrations/0052_country.sql:54` vs `0046:18-23` / `0056` | `country_code` existe en `entity` (DEFAULT 'ES') pero `servable_entity` no lo proyecta y `v_servable_dealer` no lo expone ni filtra: el gate es **ciego al país** aunque la columna ya está `[VERIFIED]` | Reproyectar `servable_entity` con `country_code` (CREATE OR REPLACE, aditivo); exponerlo en `v_servable_dealer`; añadir predicado país en stats/geo/sello |
| 7 | `tests/test_api_gaps.py:203-222` | La 2ª-vía es **tautológica**: recomputa el predicado de stats contra sí mismo dentro de tolerancia (200) `[VERIFIED]` | Reemplazar por gate de igualdad cross-scope: `stats == numerador-venta-sello == v_servable_dealer.has_inventory` (por país) sobre `:5434`, hash-golden |

---

## Mejoras nivel-inalcanzable

Todas €0, aditivas, en la línea "la máquina impone la regla y la prueba sola":

1. **Gate de primera clase como invariante mecánico.** No solo cablear `v_servable_dealer`, sino añadir un **trigger/meta-test** que asserta `stats.dealers == numerador-sello == v_servable_dealer.has_inventory` por país en cada push: hace **imposible** que reaparezca un scope divergente sin poner el build en rojo (patrón [`COUNTRY-PROOF-INVARIANT`](COUNTRY-PROOF-INVARIANT.md): fix + guard + golden).
2. **Predicado-como-parámetro-de-pack** materializado en tabla `country_pack_kind_policy(country_code, kind, role_in_gate)` — el gate hace JOIN, no `IN (literal)`. Onboarding de país #2 = insertar filas, no editar SQL.
3. **Golden de equivalencia con delta explicado** congelado: cada componente del delta (`garaje`-con-inv, dedup G4, `active`-vs-`unverified`) como aserción independiente, no un `±tolerancia` ciego. Sustituye `_DEALER_COUNT_TOLERANCE=200` (hoy demasiado laxo: absorbería una regresión de 199 entidades en silencio) por igualdad-con-delta-nombrado.
4. **Confianza + provenance por clasificación de kind/tier/group:** cada asignación lleva su `kind_source`/regla/offset (BLINDAJE §1.2); el clasificador ambiguo escala a Claude (capa-3) en vez de adivinar. Un eje `sells_cars` saneado o retirado (no un tercer estado muerto).
5. **Meta-test "toda cifra pública lleva país"** extendido del invariante de país (hoy enfocado en queries geo) a **todo conteo del gate** — enumera stats/geo/sello y asserta partición `country_code` o allow-list justificada `[VERIFIED COUNTRY-PROOF-INVARIANT.md:18-19]`.

---

## Open items

Cada break adversarial integrado con su severidad y resolución. **Ninguno oculto.** Los breaks comparten una raíz (predicado ES-hardcoded + sin partición país) y una resolución de diseño (predicado-como-pack + `country_code` partición + cablear la canónica); quedan ABIERTOS porque (a) la canónica sigue NO CABLEADA y (b) el stack caído impide correr el golden que los cerraría.

| ID | Break / defecto | Fuga | Severidad | Resolución / estado |
|---|---|---|---|---|
| **B-DE** | Taxonomía alemana (Autohaus/Vertragshändler, Freie Werkstatt, Autoverwertung/Schrottplatz). El gate excluye la cadena literal `'desguace'` y el sello incluye solo `compraventa+concesionario_oficial` | La exclusión de scrapyards **no dispara** (Autoverwertung≠'desguace') → desguaces DE contados como PdV; y el numerador del sello (2 kinds ES) = **0** → cobertura DE reportada como GAP total pese a miles de Autohäuser. Doble mentira en una cifra | **CRITICAL** | Resuelto-por-diseño con predicado-como-pack (DE declara sus `EXCLUDED_KINDS`/`SALE_POINT_KINDS`). ABIERTO hasta cablear canónica + pack DE + golden cross-country en `:5434` |
| **B-FR** | `vendeur particulier`, `casse auto` (≠'desguace'), `stand`/`mandataire` (≠compraventa) | `casses` se filtran al conteo de PdV **y** `mandataires`/`stands` quedan fuera del núcleo → sobre-cuenta piezas e infra-cuenta venta a la vez; sello FR mal numerado | **HIGH** | Igual que B-DE: pack FR + cableado + golden. ABIERTO |
| **B-IT/PT** | `concessionaria`/`autosalone` (IT), `stand`/`comércio` (PT); `ferro-velho`/`sfasciacarrozzerie` (≠'desguace') | Núcleo de venta infra-contado (kinds no incluidos) + scrapyards sobre-contados; numerador de 2 kinds ES ≈ 0 → países sellados como GAP falso | **HIGH** | Pack IT/PT + cableado + golden. ABIERTO |
| **B-noUE** | CH/UK/US: no existe DIRCE-CNAE451 (techo registral ES) ni censo DGT-CAT (scrapyards ES) | `v_province_seal` venta → `denominator NULL` → verdict `NO_DENOM` en todo el país; segmento desguace sin censo → `denominator 0`. El numerador del gate sigue contando, pero toda fracción es inservible: el sello no certifica scope | **HIGH** | Denominadores como adaptadores de pack (`registral_ceiling`, `scrapyard_census`); sin pack → `NO_DENOM` honesto por diseño (nunca 0 silencioso). ABIERTO |
| **B-ruido** | Multi-país sin predicado de país: `country_code DEFAULT 'ES'` + `product_stats` PK `id=1` + stats/sello sin `GROUP BY` país | Las filas de un 2º país se pliegan TODAS en la única fila `product_stats` y en el mismo numerador del sello: el "Puntos de venta" público suma ES+CC **sin error, solo mal** (corrupción silenciosa del titular); `DEFAULT 'ES'` atribuye país en silencio a filas mal etiquetadas | **CRITICAL** (corrupción silenciosa de la cifra pública) | Partición `country_code` obligatoria: proyectar en `servable_entity`/`v_servable_dealer`, PK `product_stats(country_code)`, `GROUP BY (country_code,province_code)` en sello. ABIERTO |
| **OI-cableado** | `v_servable_dealer` definida pero **NO CABLEADA** (0 lectores en `services/api/`) `[VERIFIED 0056:26-37; 08-serve.md:39]` | Mientras 6 scopes sigan vivos (geo-raw / 54,6k legacy / ~19,1k stats / ~36,3k directorio / ~18,3k has_inventory / ~18,3k sello), toda fracción es atacable y el titular nunca cuadra con lo paginado | **HIGH** | OPEN ITEM central, compartido con sello (B8 en [`07-quality-seal.md`](stages/07-quality-seal.md)). Cablear como ÚNICO numerador tras dry-run→golden→Ferrari→CI |
| **OI-sellscars** | `sells_cars` es un eje de gate **diseñado pero no usado**, con datos incoherentes (596 desguaces=true/0-inv; 7.201 garajes=NULL) `[VERIFIED AUDIT_2026-06-15.md:64,82; 0006:34]` | Confunde: aparenta un gate de negocio que el predicado real ignora | **MEDIUM** | Sanear el dato y cablearlo, **o** retirarlo del esquema. Decisión de modelo pendiente |
| **OI-tolerancia** | `_DEALER_COUNT_TOLERANCE = 200` `[VERIFIED test_api_gaps.py:144]` sobre una 2ª-vía tautológica | Una regresión de hasta 199 PdV pasaría en verde, y la tautología no detecta divergencia con la canónica | **MEDIUM** | Sustituir por igualdad-con-delta-nombrado contra la canónica (ver §Mejoras #3) |

> **Limitación meta (honestidad cruda):** este capítulo se construyó sobre **1 de las 6 facetas** entregadas en el encargo (`servable-gate`); las otras 5 no llegaron en el prompt (truncado). Compensé verificando la taxonomía de tiers/grupos **directamente en la fuente** (0016/0002/0005/00-TIER1-REGISTRY/SEGMENT_TAXONOMY). Todo break adversarial de la faceta recibida está integrado arriba; si las facetas restantes aportan breaks adicionales, se añaden a esta tabla sin reabrir el diseño.
