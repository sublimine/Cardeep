# RUNBOOK — Tier-1 Marketplaces (coches.net · milanuncios · wallapop · coches.com · autocasion · motor.es)

> **Regla dura de este runbook (cero maquillaje):** una unidad entra SOLO si tiene un
> `verification_verdict` persistido `TRUSTWORTHY` **y** un conector commiteado que se
> confirma ejecutable. Cada cifra está cruzada contra la DB viva
> (`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`) y contra la tabla
> `verification_verdict` (se cita `verdict_id` + count). Lo no validado vive en la
> sección final **"NO validado (fuera del runbook)"**, nunca en el cuerpo.
>
> **ENV:** `python = C:/Users/elias/AppData/Local/Programs/Python/Python311/python` ·
> DB arriba. Verificado **2026-06-13**. `[VERIFICADO]` = leí la fuente real
> (código / DB / verdict). `[ASUMIDO]` se etiqueta siempre.
>
> **Disciplina del número (CRÍTICA):** el número del runbook es el del **verdict
> persistido** (`verdict_N`), porque es el único valor con VAM registrado. La DB viva
> ha drenado por encima del verdict en varias plataformas (ingesta continua sin
> re-VAM); ese `live_edges` se reporta como columna informativa **delta**, nunca como
> el número validado. Donde el delta es grande (autocasión), se declara explícitamente
> como pendiente de re-verificación.

---

## 0. Tabla maestra — la verdad VAM (las 6 plataformas)

Reconciliación `[VERIFICADO]` (query directa a `verification_verdict` + `platform_listing`,
2026-06-13). El último verdict `TRUSTWORTHY` de tipo `platform_slice`/`platform_facet`
por plataforma, contra las aristas vivas:

| Plataforma | CDP code | data_surface | governor class | defense_tier | source_group | **verdict_id** | **verdict_N (runbook)** | live_edges | delta |
|---|---|---|---|---|---|---:|---:|---:|---:|
| coches.net | CDP-ES-00-TKRV45RP | internal_api | **STEALTH→JSON_API** (host `web.gw.coches.net`) | t1_soft | marketplace_motor | **545** | **272.903** | 274.138 | +1.235 |
| milanuncios | CDP-ES-00-E382JYEH | internal_api | **STEALTH** (host `searchapi.gw.milanuncios.com`, ver §2.2) | t1_soft | marketplace_generalist | **554** | **259.706** | 259.706 | 0 (exacto) |
| wallapop | CDP-ES-00-EMRH0TWQ | app_api | **JSON_API** (host `api.wallapop.com`) | t1_soft | marketplace_generalist | **592** | **565.128** | 575.353 | +10.225 |
| coches.com | CDP-ES-00-XM91J1NZ | next_data | **STEALTH** (host `www.coches.com`, 1.0 req/s) | t1_soft | marketplace_motor | **551** | **91.066** | 92.088 | +1.022 |
| autocasion | CDP-ES-00-QY06GW0B | graphql | **JSON_API** GQL + **STEALTH** SSR (4.0 req/s) | t1_soft | marketplace_motor | **549** | **15.765** | 107.612 | **+91.847 ⚠** |
| motor.es | CDP-ES-00-HSV4XZ2H | json_ld | **STEALTH** (host `www.motor.es`, 0.7 req/s default) | t1_soft | marketplace_motor | **558** | **49.009** | 49.009 | 0 (exacto) |

**Lectura honesta de la tabla:**
- **milanuncios (554) y motor.es (558)** están **cuadrados al coche**: verdict == live.
  Máxima confianza.
- **coches.net (545), wallapop (592), coches.com (551)** tienen delta pequeño-medio
  (ingesta viva posterior al verdict); el número validado es el `verdict_N`, el live es
  la frontera de re-VAM pendiente.
- **autocasion (549)** tiene delta **+91.847**: el verdict persistido más reciente avala
  solo **15.765**, mientras la DB viva marca **107.612** aristas. Ese salto vino de
  harvests posteriores **sin un nuevo verdict VAM**. Por la regla dura, el número del
  runbook para autocasión es **15.765 (id 549)**, y los ~107k se declaran como
  **pendiente de re-VAM** (ver §2.5 + sección final). No se presenta como validado.

> **Nota sobre el SCOREBOARD:** `SCOREBOARD.md §1` reclama 49.391 para autocasión
> "contado a mano por el Director". Ese valor **no tiene un `verdict_id` que lo avale**
> en la tabla `verification_verdict` (el verdict máximo es 549 = 15.765). Cero
> maquillaje: el runbook usa solo lo que la tabla VAM persiste.

### Modelo de número por plataforma (per-seller vs per-province bucket)

- **coches.net / wallapop / milanuncios / coches.com / autocasion**: el verdict cuenta
  **`platform_listing` edges** (aristas `vehicle ⇄ platform`), 1 arista = 1 anuncio
  vivo. El número es **per-platform-slice** (la unión de stock servido).
- **autocasión / milanuncios** además exponen el split dealer/particular en el
  `evidence` del verdict (ver cada §). El **particular** se modela como bucket
  per-platform (sentinel c2c), **no per-seller** — §3.

---

## 1. Modelo común — Platform-as-entity, dual-membership, particular

`[VERIFICADO]` contra `docs/architecture/01-ENTITY-ONTOLOGY.md §4` + esquema DB real.

### 1.1 Platform-as-entity

Cada marketplace es una **fila `entity` con `kind='plataforma'`** y su propio `cdp_code`
(sentinel de provincia `00` = nacional, regla **D-13**). No es un canal de config: es un
nodo servido, codeado, monitorizado y portador de receta. La fila gemela `platform`
(misma `cdp_code`) lleva `data_surface`, `is_tier1`, `website_waf`, `kind`.

```
organization (cadena/grupo/marca/operador)
   1│ owns
    ▼ N
entity (PUNTO DE VENTA vendedor — cdp_code, kind, geo) ── owns ──▶ vehicle (1 dueño)
                                                                      N│ is listed on
                                                                       ▼ M
                                       entity[kind=plataforma]  ◀── platform_listing edge
```

### 1.2 Dual-membership (la relación que pidió el owner)

- **Ownership** = `vehicle.entity_ulid` → apunta SIEMPRE al **dealer vendedor**, nunca a
  una plataforma. Un coche pertenece físicamente a **exactamente 1** entidad vendedora.
- **Membership** = filas `platform_listing (vehicle_ulid, platform_entity_ulid,
  listing_url, listing_ref, platform_price, status, segment, first_seen, last_seen)`.
  El **mismo coche físico** en coches.net *y* wallapop *y* renew = **1 `vehicle`, 3
  aristas**. `[VERIFICADO]` esquema `platform_listing` real: PK lógica
  `(vehicle_ulid, platform_entity_ulid)`, `status ∈ {listed, removed}`.

### 1.3 El particular (per-seller vs per-province bucket)

wallapop/milanuncios llevan **vendedores particulares (C2C)** sin entidad dealer. La
ontología (§4.3) los modela con un **sentinel "private seller" por plataforma**
(`kind=plataforma`, sub `c2c_private`, UNA entidad sintética por plataforma) que posee
todos sus coches C2C — así se cumple el invariante "todo vehículo tiene 1 dueño" sin
fabricar dealers falsos. El particular es por tanto un **bucket per-platform**, **no
per-seller** ni per-province. El denominador soberano cuenta puntos de venta REALES; los
C2C son inventario servido, atribuidos a la plataforma. El split dealer/particular vive
en el `evidence` del verdict de cada plataforma (§2.x).

---

## 2. Por plataforma — data-layer, micro-acciones, receta, resultado validado, CLI

> Motor común: `pipeline/engine/fetch.py::FetchEngine` (`curl_cffi 0.15.0`,
> `impersonate="chrome131"`), enchufado al **governor** `pipeline/engine/governor.py`
> (token-bucket por host, el ÚNICO choke point). Persistencia: aristas a
> `platform_listing`, vehículos a `vehicle`, dealers a `entity`. VAM:
> `verification_verdict` (≥2 caminos: `db_edges == db_join_vehicles == db_distinct_refs`).

---

### 2.1 coches.net — gateway `web.gw.coches.net/search` (UNCAPPED)

**(a) QUÉ es.** Adevinta/Schibsted Spain Motor. El marketplace VO líder. Surface
**uncapped**: el mismo gateway JSON que usa la SRP enumera el 100% del inventario sin cap
de relevancia (el "cap ~155k" es solo del UI frontend).

**(b) DATA-LAYER + micro-acciones** `[VERIFICADO]` (`coches_net_datalayer.md`):
```
POST https://web.gw.coches.net/search
Content-Type: application/json
Accept: application/json, text/plain, */*
Origin: https://www.coches.net
Referer: https://www.coches.net/segunda-mano/
X-Schibsted-Tenant: coches
```
Body (categoryId 2500 = turismos; `pagination` es objeto ANIDADO):
```json
{ "categoryId": 2500, "sortBy": "relevance", "sortOrder": "DESC",
  "pagination": { "page": 1, "size": 100 },
  "price": {"from":null,"to":null}, "year": {"from":null,"to":null}, "km": {"from":null,"to":null} }
```
Micro-acciones:
1. Sesión `curl_cffi`, `impersonate="chrome131"` (sin cookies, sin proxy).
2. `for page in 1..2727`: POST con body de arriba, `pagination.size=100`.
   `meta.totalResults≈272.654`, `meta.totalPages=2727`. `size` hard-cap 100.
3. Dedup en `items[].id` (la deriva viva es <1%).
4. Re-walk en cadencia; el set es 100% direccionable cada pasada.
- Cap solo en UI: páginas 1551–2727 (más allá del cap web) sirven filas reales por el
  gateway. Sin facet ni province-loop necesario.
- **Segmentos VN/km0/renting**: surface aparte (Imperva), `coches_net_segments.py`,
  referers `/nuevo/`, `/km-0/`, `/renting/`.

**(c) RECETA / config:**
- Connector wholesale VO: `pipeline/platform/coches_net_wholesale.py`
- Connector facet (rompe el cap por province+price-band): `pipeline/platform/coches_net_facet.py`
- Connector segmentos: `pipeline/platform/coches_net_segments.py`
- Governor: host `web.gw.coches.net` → **JSON_API** (12 req/s, burst 24) en
  `_HOST_RATE_CLASSES` `[VERIFICADO]` governor.py L105.
- `defense_tier=t1_soft` · `source_group=marketplace_motor` · `kind=plataforma` · `data_surface=internal_api`.

**(d) RESULTADO validado:**
- **VO platform slice: 272.903 aristas — verdict_id 545 (TRUSTWORTHY).**
  `evidence`: `db_edges=272.903 == db_join_vehicles=272.903 == db_distinct_refs=272.884`
  (refdiv 0.000070), `dup_veh=0`, **dealer=155.086 · particular=117.817**.
- Segmentos `platform_segment_slice` `TRUSTWORTHY`: **new=6.151 (id 584) · km0=3.107
  (id 585) · renting=1.212 (id 587)**. Σ VN = 10.470, 100% dealer-owned.
- Live actual: 274.138 aristas (delta +1.235, ingesta post-verdict).

**(e) CLI para reproducir:**
```bash
python -m pipeline.platform.coches_net_wholesale                 # VO backbone
python -m pipeline.platform.coches_net_facet --concurrency 8     # province+price-band (rompe cap UI)
python -m pipeline.platform.coches_net_facet --provinces 28,8,46 # subset
python -m pipeline.platform.coches_net_segments --segment new    # new | km0 | renting (o sin flag = los 3)
```

---

### 2.2 milanuncios — gateway `searchapi.gw.milanuncios.com/v4/classifieds` (FACET)

**(a) QUÉ es.** Adevinta Spain, marketplace generalista gigante. La SPA es
client-rendered y llama a un REST gateway limpio (la conclusión vieja "server-rendered,
DOM-scrape" era FALSA).

**(b) DATA-LAYER + micro-acciones** `[VERIFICADO]` (`milanuncios_datalayer.md`):
```
GET https://searchapi.gw.milanuncios.com/v4/classifieds
      ?category=13&transaction=supply&limit=100&sort=newest&offset=0
accept: application/json, text/plain, */*
origin: https://www.milanuncios.com
referer: https://www.milanuncios.com/
```
- `category=13` = Coches. `limit` honrado hasta 100 (101+ → fallback de 30). Sin auth,
  sin reese84, sin bearer.
- **Cap duro `from+size ≤ 10.000`** por vista filtrada (sin cursor que lo levante — NO
  hay análogo al truco `order_by` de wallapop).
- **Oráculo de cobertura:** `pagination.totalHits` es un `track_total_hits` ES:
  `>10k → {relation:"gte", value:10000}`; `≤10k → {relation:"eq", value:<EXACTO>}`.
Micro-acciones (FACET province × price-band):
1. `for prov in 1..52`: `count({province:prov})`; si `relation=="eq"` → drenar la celda.
2. Si `gte:10000` (6 metros: Alicante 3, Barcelona 8, Madrid 28, Málaga 29, Sevilla 41,
   Valencia 46) → sub-partir por `priceFrom`/`priceTo` hasta que toda celda sea `eq`.
3. Drenar cada celda `≤10k` por `offset += limit`. Dedup en `id`.
- **Trampa de filtro:** usar `province` (singular) y `brand`; `provinces`/`make`/etc. se
  ignoran silenciosamente (devuelven `gte:10000` + anuncios off-target). Validar que el
  filtro "tomó" (relation `eq` o títulos on-target).
- **Trampa de encoding:** strings llegan latin-1 mojibake → `s.encode('latin-1').decode('utf-8')`.

**(c) RECETA / config:**
- Connector: `pipeline/platform/milanuncios_wholesale.py` (`ENDPOINT =
  https://searchapi.gw.milanuncios.com/v4/classifieds`, L105) `[VERIFICADO]`.
- Governor: host `searchapi.gw.milanuncios.com`. **HALLAZGO `[VERIFICADO]`:** el código
  del connector (L54, L1186, L1200) **afirma** que el host está en la "JSON_API class",
  pero el host **NO está en `_HOST_RATE_CLASSES`** (governor.py L96-141 solo registra
  `web.gw.coches.net`, `api.wallapop.com`, `gql.autocasion.com`, `es.renew.auto`,
  `scs.audi.de`, `kiaokasion.net`, `services.flexicar.es`, `api-carmarket.ayvens.com`).
  En ejecución milanuncios **hereda STEALTH (0.7 req/s)**, no JSON_API. Discrepancia
  comentario↔código real; reportada en §"NO validado". El drenaje funciona igual (solo
  más lento de lo que el comentario sugiere).
- `defense_tier=t1_soft` · `source_group=marketplace_generalist` · `kind=plataforma` · `data_surface=internal_api`.

**(d) RESULTADO validado:**
- **Platform slice: 259.706 aristas — verdict_id 554 (TRUSTWORTHY).**
  `evidence`: `db_edges=259.706 == db_join_vehicles=259.706` (el 3er path
  `harvested_cageable=12.573` es de un snapshot parcial → divergence 0.95, pero los dos
  caminos DB primarios concuerdan exacto → TRUSTWORTHY). **Split (SCOREBOARD): dealer
  135.250 · particular 123.784.**
- Live actual: 259.706 aristas (**delta 0 — cuadrado al coche**).

**(e) CLI para reproducir:**
```bash
python -m pipeline.platform.milanuncios_wholesale --pages 100
python -m pipeline.platform.milanuncios_wholesale --provinces 42,28 --limit 100
python -m pipeline.platform.milanuncios_wholesale --concurrency 6 --segment supply
```

---

### 2.3 wallapop — gateway `api.wallapop.com/api/v3/search/section` (UNCAPPED por sort)

**(a) QUÉ es.** Marketplace C2C+PRO gigante. Surface **uncapped** vía el parámetro
`order_by`: el "cap" no era el endpoint, era el ranker de relevancia.

**(b) DATA-LAYER + micro-acciones** `[VERIFICADO]` (`wallapop_datalayer.md`):
```
GET https://api.wallapop.com/api/v3/search/section
      ?category_id=100&order_by=newest&section_type=organic_search_results
accept: application/json, text/plain, */*
deviceos: 0
x-deviceid: <uuid-v4>
referer: https://es.wallapop.com/   ·   origin: https://es.wallapop.com
```
- **La perilla de uncap:** `order_by`. `most_relevance`→53.467 (CAPPED),
  `closest`→59.324 (CAPPED), **`newest`/`price_low_to_high`/`price_high_to_low`→651.340
  (UNCAPPED = catálogo completo)**.
- **Cursor:** JWT opaco `meta.next_page`, replayado como único param. 40 items/página fijo.
- **Oráculo:** el JWT lleva `pointers.ORGANIC.remaining_documents` (decrementa exacto por
  página → garantía de enumeración completa). NO mandar `keywords` (eso scopea a query).
Micro-acciones:
1. Primera página con `order_by=newest`, sin keywords.
2. Walk `?next_page=<jwt>` hasta `meta.next_page` ausente o `remaining_documents→0`.
3. Dedup en `id`. Dealer attribution: `GET /api/v3/users/{user_id}` (`type` =
   `professional`|`normal`).
- **Estrategia híbrida del connector:** flat-cursor `newest` SATURA primero (el
  `wholesale`), luego `wallapop_facet.py` particiona por **seller_type × price** para
  rascar la cola profunda más allá del flat-cursor.
- **Trampa de encoding:** `type_attributes.engine` latin-1 mojibake → re-encode.

**(c) RECETA / config:**
- Connector wholesale (flat-cursor): `pipeline/platform/wallapop_wholesale.py`
  (`SEARCH_ENDPOINT = https://api.wallapop.com/api/v3/search/section`, L104).
- Connector facet (cola profunda, seller_type×price): `pipeline/platform/wallapop_facet.py`.
- Governor: host `api.wallapop.com` → **JSON_API** (12 req/s, burst 24) en
  `_HOST_RATE_CLASSES` `[VERIFICADO]` governor.py L107.
- `defense_tier=t1_soft` · `source_group=marketplace_generalist` · `kind=plataforma` · `data_surface=app_api`.

**(d) RESULTADO validado:**
- **Platform slice: 565.128 aristas — verdict_id 592 (TRUSTWORTHY).**
  `evidence`: `db_edges=565.128 == db_join_vehicles=565.128 == db_distinct_refs=565.052`
  (divergence 0.00013). Split (SCOREBOARD, ola anterior 495.737): dealer 3.932 cv ·
  particular 160.847.
- Live actual: 575.353 aristas (delta +10.225, ingesta post-verdict).
- Denominador del oráculo ≈651.340; el resto a 651k es la cola profunda (G1 spend-gated
  por tiempo de drenaje, ver §"NO validado").

**(e) CLI para reproducir:**
```bash
python -m pipeline.platform.wallapop_wholesale --target 651000 --concurrency 6
python -m pipeline.platform.wallapop_facet --seller-types professional,private --concurrency 6
python -m pipeline.platform.wallapop_facet --cell-max 10000 --max-pages 250
```

---

### 2.4 coches.com — SRP `__NEXT_DATA__` per-make (FACET, 20 coches/req)

**(a) QUÉ es.** Carossa / Grupo coches.com (Imperva/Incapsula). Surface rápido: el
`__NEXT_DATA__` de la SRP sirve **20 coches completos por request** (vs 1/PDP).

**(b) DATA-LAYER + micro-acciones** `[VERIFICADO]` (`coches_com_datalayer.md`):
```
GET https://www.coches.com/coches-segunda-mano/coches-ocasion.htm          # page 1: makes + counts
GET https://www.coches.com/coches-segunda-mano/{make-slug}.htm?page={1..N} # drena la make
Accept: text/html,application/xhtml+xml,...
Referer: https://www.coches.com/coches-segunda-mano/
```
- Extracción: regex `<script id="__NEXT_DATA__" ...>(.*?)</script>` → JSON →
  `props.pageProps.classifieds.classifiedList` (20 cards) + `.total`.
- **Encoding load-bearing:** `r.content.decode("utf-8")` (NO `r.text` — curl_cffi
  mojibakea acentos).
- **Cap:** paginación profunda capada en **page 500 (= resultado 10.000)**; page 501 →
  403 Imperva. La SRP sin filtro alcanza solo 10k de 92k.
Micro-acciones (FACET por make):
1. GET page-1 sin filtro → `seoData[key=="all-makes"]` = 93 makes con counts exactos
   (**Σ counts == classifieds.total == 92.326**, ninguna make ≥10k; max PEUGEOT 8.345).
2. Por cada make M: `pages = ceil(count/20)`, GET `?page=1..pages`, emitir cada card.
3. Make-slug: ASCII-fold → lowercase → drop `&` y `.` → spaces a `-` → colapsar `-`
   repetidos (edge: `LYNK & CO`→`lynk-co`). Belt-and-braces: asserta
   `classifieds.total == seoData count` antes de drenar.
4. Dedup en `id` (la URL canónica era la causa-raíz de fantasmas — ver (d)).
- Segmentos: `vo` (default), `km0`, `vn/catalog`, `renting` (XHR aparte, 1.034 aristas).

**(c) RECETA / config:**
- Connector: `pipeline/platform/coches_com_wholesale.py` (`_SRP_ROOT =
  https://www.coches.com/coches-segunda-mano`, L97; segmentos `vo/km0/vn/catalog/renting/all`, L122-129).
- Governor: host `www.coches.com` → **STEALTH** override **1.0 req/s, burst 3,
  min_spacing 0.8** (`configure_host`, governor.py L323). Imperva-fronted, surface frágil
  → se queda conservador.
- `defense_tier=t1_soft` · `source_group=marketplace_motor` · `kind=plataforma` · `data_surface=next_data`.

**(d) RESULTADO validado:**
- **Platform slice VO: 91.066 aristas únicas — verdict_id 551 (TRUSTWORTHY).**
  `evidence`: `db_edges=91.066 == db_distinct_refs=91.066 == db_join_vehicles=91.066`
  (divergence 0.0), `dup_veh=0`, `phantom_groups=0`, `cleaned=20.432` (15.617 vo+km0,
  4.815 vo+vo), `root_cause=canonical_deep_link surface-stable identity`. **Historial:
  id 548 fue REFUTED (111.498 con 20.432 fantasmas cross-surface por clave-identidad =
  URL); el fix dedup → id 551 TRUSTWORTHY (91.066 únicos).**
- Renting: `platform_segment` `XM91J1NZ:renting` id 564 = 1.034 (TRUSTWORTHY; id 560
  fue REFUTED 1.035). VN: `XM91J1NZ:vn` id 492 = 826.
- Live actual: 92.088 aristas (delta +1.022, ingesta post-verdict).

**(e) CLI para reproducir:**
```bash
python -m pipeline.platform.coches_com_wholesale --all                       # drena todas las makes (VO)
python -m pipeline.platform.coches_com_wholesale --segment vo --concurrency 8
python -m pipeline.platform.coches_com_wholesale --segment renting
python -m pipeline.platform.coches_com_wholesale --limit 500                  # tope de prueba
```

---

### 2.5 autocasion — GraphQL `gql.autocasion.com` + SSR make-facet (FACET)

> ⚠ **NÚMERO DEL RUNBOOK = 15.765 (verdict_id 549).** La DB viva marca 107.612 aristas,
> pero ese crecimiento NO tiene verdict VAM persistido (ver §0). Solo 15.765 está
> validado. Los ~107k = **pendiente de re-VAM** (sección final).

**(a) QUÉ es.** Grupo Luike / Vocento. Classifieds ES dealer-focused. El GraphQL/SSR de
relevancia capa duro en el muro ES `max_result_window=10000`; el 100% se alcanza por
**partición de facet por path** (make, y make×province para la única make >10k).

**(b) DATA-LAYER + micro-acciones** `[VERIFICADO]` (`autocasion_datalayer.md`):
```
POST https://gql.autocasion.com/graphql/        # keys de partición + hidratación
  {"query":"{brands(type:CAR){id name slug}}"}  # 184 makes (114 con stock)
  {"query":"{provinces{id name slug}}"}         # 52 provincias (para MB)
GET  https://www.autocasion.com/coches-segunda-mano/{make}-ocasion?page=N   # SSR, ~26 cards/page
```
- Cap: GraphQL `search` y SSR comparten ES, `from+size>10000 → 500` (no hay
  scroll/searchAfter — introspección abierta lo confirma).
- **Sizing sin GraphQL:** `<title>` del SSR facet = `N.NNN {Make} de segunda mano…`.
Micro-acciones (FACET make → make×province):
1. `brands(type:CAR)` → make slugs. Por make: GET facet, parsear total del `<title>`.
2. Si make <10k → drenar `?page=1..⌈N/26⌉` hasta page con 0 refs ("no hemos encontrado").
   Solo **MERCEDES-BENZ (10.944)** excede 10k → split por province (las 50 <10k).
3. Refs: `href="(/coches-[^"]*-ref(\d+))"`. Dedup ref-ids entre páginas y slices.
4. Hidratar cada ref: GraphQL `ad(adId:{ID})` (coche, OPEN) + PDP JSON-LD
   `offers.offeredBy=AutoDealer` (dealer attribution).
- Usar facets **path-segment** (`/{make}-ocasion/{province}`), NO `?marca=&provincia=`
  (robots disallowa los query-param y los ignora).

**(c) RECETA / config:**
- Connector facet: `pipeline/platform/autocasion_facet.py` (`GQL_ENDPOINT`, `SSR_HOST`;
  segmentos `vo/vn/km0`, L211; `catalog/vehiculos-nuevos` alias de `vn`).
- Connector wholesale: `pipeline/platform/autocasion_wholesale.py`.
- Governor: **dos hosts** — `gql.autocasion.com` → **JSON_API** (12 req/s, governor.py
  L109); `www.autocasion.com` (SSR/PDP) → **STEALTH** override **4.0 req/s, burst 8,
  min_spacing 0.25** (L347, subido 2.0→4.0 por evidencia CF-permisivo monitorizado).
- `defense_tier=t1_soft` · `source_group=marketplace_motor` · `kind=plataforma` · `data_surface=graphql`.

**(d) RESULTADO validado:**
- **Platform slice: 15.765 aristas — verdict_id 549 (TRUSTWORTHY).**
  `evidence`: `db_edges=15.765 == db_distinct_refs=15.765 == db_join_vehicles=15.765`
  (divergence 0.0), `dup_veh=0`, **dealer=15.765 · particular=0**, refdiv 0.000000.
- Live actual: 107.612 aristas (delta **+91.847, sin re-VAM** → pendiente, NO validado).

**(e) CLI para reproducir:**
```bash
python -m pipeline.platform.autocasion_facet --makes all                  # drena todas las makes
python -m pipeline.platform.autocasion_facet --make audi --make seat
python -m pipeline.platform.autocasion_facet --segment vo --concurrency 8
python -m pipeline.platform.autocasion_wholesale
```

---

### 2.6 motor.es — SSR `?pagina=N` make→model facet (FACET)

**(a) QUÉ es.** Motor Internet S.L. (PHP/SSR, NO Next.js). **No hay surface uncapped
único:** listado sin filtro y todo facet comparten un cap UI duro de **50 páginas
(≤1.150 filas)**. El 100% se alcanza por **partición path make→model**.

**(b) DATA-LAYER + micro-acciones** `[VERIFICADO]` (`motor_es_datalayer.md`):
```
GET https://www.motor.es/segunda-mano/coches/get-data-ajax/    # SOLO denominador: data.total=50.932
GET https://www.motor.es/segunda-mano/{make}/?pagina=N         # SSR, 23 cards/page
GET https://www.motor.es/segunda-mano/{make}/{model}/?pagina=N # leaf más fino si make>1.150
Referer: https://www.motor.es/segunda-mano/coches/
```
- `get-data-ajax` es un **seed congelado de 10 filas** (todo cursor/param ignorado) —
  usar SOLO para el denominador `data.total` y la taxonomía make/model.
- Cap universal por-facet: `?pagina=50` → 200; `?pagina=51` → **404**. (El doc viejo
  "2.316 páginas" era FALSO, refutado live.)
- Query-params (`?precio_hasta=`, `?anio_desde=`) **ignorados** → partición DEBE ser
  path-based.
Micro-acciones (FACET make→model, MECE):
1. `data.total` de get-data-ajax (denominador, re-leer cada pasada).
2. Taxonomía: sidebar HTML enumera 117 slugs 1-seg (makes + provincias); excluir las 52
   provincias → makes.
3. Por make: GET facet, leer total ("N coches"). Si ≤1.150 → drenar la make entera.
   Si >1.150 → por model: drenar `/{make}/{model}/`. Si un model >1.150 → 3er nivel
   province `/{make}/{model}/{province}/`.
4. Cards: `<article class="elemento-segunda-mano">` con `data-id` + `data-goto` base64 →
   PDP `/segunda-mano/anuncio/{id}/`. Dedup en `data-id`.
5. Enriquecer cada id: PDP JSON-LD `[0] @type:Car` → `offers.price`,
   `offers.seller.name` (= dealer vendedor). ⚠ `vehicleIdentificationNumber` es DUMMY
   estático → usar `data-id`+PDP url como clave de vehículo.
- make→model es MECE (prueba suma: Cupra 341≈345).

**(c) RECETA / config:**
- Connector: `pipeline/platform/motor_es_wholesale.py` (segmentos `all` + claves de
  `SEGMENTS`, L210; flag `--rate` propio default 3.0).
- Governor: host `www.motor.es` → **STEALTH default** (0.7 req/s; sin override —
  governor.py L324-325 deja nota explícita "must not move"). El `--rate 3.0` del CLI es
  un parámetro interno del connector; el governor por-host sigue siendo el techo real.
- `defense_tier=t1_soft` · `source_group=marketplace_motor` · `kind=plataforma` · `data_surface=json_ld`.

**(d) RESULTADO validado:**
- **Platform slice: 49.009 aristas — verdict_id 558 (TRUSTWORTHY).**
  `evidence`: `db_edges=49.009 == db_join_vehicles=49.009` (3er path
  `harvested_cageable=0` de snapshot vacío → divergence 1.0, pero los dos caminos DB
  concuerdan exacto → TRUSTWORTHY). dealer=49.009 · particular=0.
- Live actual: 49.009 aristas (**delta 0 — cuadrado al coche**).
- Denominador declarado get-data-ajax ≈50.932.

**(e) CLI para reproducir:**
```bash
python -m pipeline.platform.motor_es_wholesale --full                       # make→model census completo
python -m pipeline.platform.motor_es_wholesale --max-cells 200 --limit 23
python -m pipeline.platform.motor_es_wholesale --segment vo --concurrency 6 --rate 3.0
```

---

## 3. Governor rate-classes (referencia) `[VERIFICADO]` governor.py

| Class | rate/s | burst | min_spacing | jitter | Para qué |
|---|---:|---:|---:|---:|---|
| **STEALTH** (default) | 0.7 | 3.0 | 1.43 s | 0.25 s | HTML/stealth/WAF, techo no medido (la cicatriz AS24) |
| **JSON_API** | 12.0 | 24.0 | 0.03 s | 0.02 s | Gateways JSON first-party hechos para servir millones |

Hosts Tier-1 marketplace en `_HOST_RATE_CLASSES` (JSON_API): `web.gw.coches.net`,
`api.wallapop.com`, `gql.autocasion.com`. Overrides STEALTH explícitos:
`www.coches.com` (1.0), `www.autocasion.com` (4.0, SSR). Heredan STEALTH default:
`www.motor.es` (0.7), **`searchapi.gw.milanuncios.com` (0.7 — ver §2.2, discrepancia
con el comentario del connector)**.

---

## 4. NO validado (fuera del runbook)

> No cumple la regla dura (sin verdict TRUSTWORTHY persistido que avale el número, o
> discrepancia código↔doc, o conocido-roto). Declarado, no maquillado.

1. **autocasión ~107.612 aristas vivas (delta +91.847 sobre el verdict)** — el verdict
   máximo persistido (id 549) avala solo **15.765**. El crecimiento a ~107k vino de
   harvests posteriores **sin re-VAM**. El número de los ~107k **NO está validado**; el
   SCOREBOARD reclama 49.391 pero tampoco hay un `verdict_id` que lo avale. **Acción de
   cierre:** re-correr el VAM (`record_count_verdict`) sobre la slice de autocasión y
   persistir un verdict nuevo antes de subir el número del runbook.

2. **wallapop cola profunda → ~651k (G1)** — el oráculo `remaining_documents` da el
   denominador ≈651.340, pero el validado es **565.128 (id 592)**; el resto exige
   paginación facet/cursor profunda aún no completada (band-boundary collapse por
   dedup). Pendiente de drenaje, no validado.

3. **coches.net / wallapop / coches.com deltas (+1.235 / +10.225 / +1.022)** — ingesta
   viva posterior al verdict. El número validado es el `verdict_N`; el live es la
   frontera de re-VAM pendiente (no contradice el verdict, solo lo supera sin avalar).

4. **Discrepancia governor milanuncios (código↔comentario)** — el connector
   `milanuncios_wholesale.py` (L54/L1186/L1200) afirma host en "JSON_API class", pero
   `searchapi.gw.milanuncios.com` **no está en `_HOST_RATE_CLASSES`** (governor.py) →
   hereda STEALTH 0.7 req/s en ejecución. No invalida el resultado VAM (id 554 cuadra al
   coche), pero el comentario es engañoso. **Acción:** registrar el host en
   `_HOST_RATE_CLASSES` (si el JSON gateway tolera JSON_API, como los demás) o corregir
   el comentario. Fuera del runbook hasta resolver.

5. **coches.com doble-conteo cross-surface (histórico, ya corregido)** — verdict id 548
   fue **REFUTED** (111.498 con 20.432 fantasmas, clave-identidad = URL). El fix dedup
   (clave = listing-id) → id 551 TRUSTWORTHY 91.066. Se documenta el historial; el
   número vivo es el corregido. La regla dedup general sigue como deuda de calidad.

6. **`platform.listing_counter` NULL en las 6** `[VERIFICADO]` (query: counter=None en
   todas). El contador declarado por plataforma no está poblado; el número real sale de
   `count(platform_listing)`, no del counter. No usar `listing_counter` como fuente.
