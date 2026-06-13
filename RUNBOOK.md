# CARDEEP RUNBOOK — la guía maestra de TODO lo que funciona, validado

> **Bitácora viva del sistema soberano.** Esta es la guía operativa única de **cómo se
> scrapea España end-to-end** y de cada unidad **validada + funcional** que sirve hoy. Regla
> dura, cero maquillaje: **nada entra al runbook sin (a) un `verification_verdict` persistido
> `TRUSTWORTHY` —cito su `id`— Y (b) un conector commiteado que se confirma ejecutable.** Lo
> aspiracional, no validado o roto vive SOLO en el apéndice final **§"NO validado (fuera del
> runbook)"**, nunca en el cuerpo.
>
> **Fuente de verdad de cada número:** la DB viva
> `postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep` (contenedor `cardeep-pg`,
> `127.0.0.1:5433->5432`, UP) cruzada contra la tabla `verification_verdict`. Verificado
> **2026-06-13**. `[VERIFICADO]` = leí la fuente real (código / DB / verdict); `[ASUMIDO]` se
> etiqueta siempre.
>
> **ENV de ejecución:** `python = C:/Users/elias/AppData/Local/Programs/Python/Python311/python`
> (`$PY` en los CLI) · DB arriba · conectores invocados como
> `python -m pipeline.platform.<module>` desde `C:\Users\elias\projects\cardeep`.
>
> **Idioma:** prosa en español, código y comandos en inglés.

---

## 0. Disciplina del número (CRÍTICA, leer antes de cualquier cifra)

El número del runbook es **el del verdict persistido** (`verdict_N`), porque es el único valor
con VAM registrado (≥2 caminos ortogonales coincidentes, `divergence` dentro de tolerancia). La
DB está en **ingesta viva**: en varias unidades el `live_edges` ha drenado por encima del
verdict (cosecha continua sin re-VAM). Ese live se reporta como columna informativa **delta**,
nunca como el número validado. Donde el delta es grande (autocasión), se declara explícitamente
como **pendiente de re-VAM** y NO se presenta como validado. La metodología (A==B exacto) se
reconfirma viva; la deriva absoluta es ingesta, no descuadre.

---

## 1. OVERVIEW — cómo se scrapea el país end-to-end

El sistema cosecha el 100% direccionable del mercado VO/VN español por un pipeline único, y
sirve el resultado por una API viva con delta + historial. El flujo soberano:

```
DESCUBRIR → SCRAPEAR → RECETA → CAGE (ingesta) → VAM → API → DELTA → S-HEALTH
```

1. **DESCUBRIR.** Enumerar el universo de fuentes: marketplaces Tier-1, portales OEM-VO,
   cadenas, rent-a-car, subastas, y la web propia de cada dealer (long-tail). Cada fuente se
   acuña con un `cdp_code` **inmutable y determinista** (`services/api/codes.py`): re-descubrir
   la misma entidad por otra fuente NO acuña un segundo código (clave canónica: seller-id >
   dominio pelado > CIF > nombre|municipio).
2. **SCRAPEAR.** El motor de fetch tiered (`pipeline/engine/fetch.py`, `curl_cffi`
   `impersonate="chrome131"`) emite el fingerprint TLS/JA3 de Chrome real. Tier-0 optimista
   primero; escala a navegador stealth (camoufox/Playwright) SOLO ante una respuesta de
   challenge tipada ("optimism is free; escalation is on evidence"). CADA fetch pasa por el
   **governor** (`pipeline/engine/governor.py`), un token-bucket por host registrable que es el
   ÚNICO choke point de rate (la cicatriz AS24: nunca repetir el ban por carga agregada).
3. **RECETA.** Por fuente se escribe la receta data-layer reproducible (endpoint, headers,
   partición/tope, micro-acciones, parser de identidad). En el long-tail, **una receta por
   FAMILIA CMS/DMS** drena N dealers que comparten markup (el multiplicador).
4. **CAGE (ingesta).** Persistencia idempotente `ON CONFLICT`: el coche a `vehicle`, el dealer
   a `entity`, la membresía de plataforma a `platform_listing` (arista). Propiedad singular
   (`vehicle.entity_ulid` = dealer vendedor), membresía plural (aristas a 0..M plataformas).
5. **VAM.** El juez de "verificado" (`verification_verdict`): ≥2 caminos ortogonales por claim
   con la **invariante de landed-count** (el conteo que vive en la DB DEBE estar entre los que
   coinciden). Sin quórum → no entra al runbook.
6. **API.** FastAPI (`services/api/main.py`) sirve entidad / inventario / delta / geo-tree /
   completeness / platform-inventory con envelope consistente `{ok, data, error, meta}`.
7. **DELTA.** `vehicle_event` append-only (`NEW, GONE, REAPPEARED, PRICE_CHANGE, …`): el
   historial soberano por coche, servido por `/entities/{cdp}/delta?since=ISO`.
8. **S-HEALTH.** El watchdog (`pipeline/ops/health.py` + breaker durable): si una fuente falla,
   alerta con el ORIGEN EXACTO, auto-clasifica la reparación, abre breaker y Cardeep nunca se
   cae.

### 1.1 La lógica de separación de grupos (el eje del runbook)

El inventario se reparte en **seis especies de fuente disjuntas** (eje `source_group` /
`kind` de `migrations/0016_tiering_groups.sql`). La disjunción es `[VERIFICADO]` a nivel
vehículo: ningún coche físico se comparte entre grupos (las membresías plurales son entre
plataformas DENTRO de Tier-1, no entre grupos).

| Grupo | `source_group` | `kind` entidad-plataforma | Naturaleza | Capítulo |
|---|---|---|---|---|
| **Tier-1 marketplaces** | `marketplace_motor` / `marketplace_generalist` | `plataforma` | gigantes C2C+PRO, surface uncapped o facet-particionado | §3 |
| **OEM-VO** | `oem_vo_portal` | `oem_vo_portal` | fabricante-dueño sirviendo el VO certificado de su PROPIA red oficial | §4 |
| **Cadenas (chains)** | `chain` | `cadena` | cadena nacional VO con muchos puntos físicos | §5 |
| **Rent-a-car VO** | `rentacar_vo` | `rent_a_car_vo` | operador que liquida su ex-flota VO directo | §5 |
| **Subastas** | `official_registry` | `subasta` | remarketing B2B/B2C; precio bid-login-gated (NULL honesto) | §5 |
| **Long-tail** | `long_tail_web` | `compraventa`/`concesionario_oficial` | web propia del dealer, agrupada por familia CMS/DMS | §6 |

- **Tier-1 está separado absolutamente del resto** por su eje `defense_tier`
  (t0_open..t4_spend_gated) y por ser surface marketplace (membresía plural por coche).
- **OEM-VO, cadenas, rentacar y subastas** comparten el modelo de doble-membresía pero difieren
  en el dueño atómico: dealer oficial (OEM-VO), sucursal/cadena (chains/rentacar), lote de venta
  (subastas).
- **Long-tail** es la mitad más simple: la web propia es la fuente PRIMARIA → **no hay arista
  `platform_listing`**, cada coche es `vehicle.entity_ulid = el dealer`. Propiedad singular y
  directa.
- **El motor/geo/VAM/health/API** (§7) es transversal: la ÚNICA arquitectura por la que fluyen
  los seis grupos.

> **Disjunción `[VERIFICADO]`:** la suma de los conteos por grupo iguala el `COUNT(DISTINCT
> vehicle)` sobre todos los grupos a la vez → cero coches compartidos entre grupos.

---

## 2. ÍNDICE DE CAPÍTULOS — la estructura canónica `docs/runbook/`

La documentación sigue la arquitectura canónica del spec
([`docs/runbook/README.md`](docs/runbook/README.md)): **una entrada = un fichero**, *toda entrada
con la MISMA plantilla*, *todo número con su prueba*. Navegable de arriba (overview) a abajo (un
conector) sin ambigüedad.

| Nivel | Fichero | Qué contiene |
|---|---|---|
| Overview | [`docs/runbook/00-OVERVIEW.md`](docs/runbook/00-OVERVIEW.md) | cómo se scrapea el país END-TO-END (DESCUBRIR→SCRAPEAR→RECETA→API→DELTA) |
| Motor | [`docs/runbook/01-ARCHITECTURE.md`](docs/runbook/01-ARCHITECTURE.md) | governor · fetch · schema · geo · cdp_code · VAM · S-HEALTH · API · dedup |
| Separación | [`docs/runbook/02-GROUP-SEPARATION.md`](docs/runbook/02-GROUP-SEPARATION.md) | el eje `source_group`/`kind`/`defense_tier` que separa los seis grupos |
| Grupos | [`docs/runbook/groups/`](docs/runbook/groups/) | un capítulo por grupo (resumen + tabla de miembros validados) |
| Conectores | [`docs/runbook/platforms/`](docs/runbook/platforms/) | un fichero por conector validado (plantilla uniforme §3 del spec) |
| Ledger | [`docs/runbook/VALIDATION-INDEX.md`](docs/runbook/VALIDATION-INDEX.md) | unidad → verdict id → count → CLI → fecha (55 ids confirmadas en DB) |
| Apéndice | [`docs/runbook/NOT-VALIDATED.md`](docs/runbook/NOT-VALIDATED.md) | lo intentado/aspiracional/roto que NO entra al runbook |

| § (resumen abajo) | Capítulo | Unidades validadas | Grupo / ficheros conector |
|---|---|---:|---|
| §3 | **Tier-1 marketplaces** | 6 | [`groups/tier1-marketplaces.md`](docs/runbook/groups/tier1-marketplaces.md) → `platforms/{coches-net,milanuncios,wallapop,coches-com,autocasion,motor-es}.md` |
| §4 | **OEM-VO portals** | 14 | [`groups/oem-vo.md`](docs/runbook/groups/oem-vo.md) → `platforms/{spoticar,mercedes-benz,…,ford}.md` |
| §5 | **Otros grupos** (chains · rentacar · subastas) | 10 | [`groups/{chains,rentacar-vo,subastas}.md`](docs/runbook/groups/) → 10 ficheros conector |
| §6 | **Long-tail** (own-site, multiplicador CMS/DMS) | 7 | [`groups/long-tail.md`](docs/runbook/groups/long-tail.md) → 7 ficheros `platforms/family-*.md` |
| §7 | **Motor · Geo · VAM · S-HEALTH · API · Esquema** | 8 | [`01-ARCHITECTURE.md`](docs/runbook/01-ARCHITECTURE.md) |
| §8 | **VALIDATION INDEX** (ledger: unidad → verdict → count → CLI) | 45 | [`VALIDATION-INDEX.md`](docs/runbook/VALIDATION-INDEX.md) |
| §9 | **NO validado (fuera del runbook)** | apéndice | [`NOT-VALIDATED.md`](docs/runbook/NOT-VALIDATED.md) |
| §10 | **Regla de BITÁCORA VIVA** (LIVING-LEDGER) | protocolo | — |

> Cada capítulo enlaza su sección de detalle completa (data-layer, micro-acciones paso a paso,
> receta, trampas). El cuerpo de abajo es el resumen navegable; los ficheros `groups/` +
> `platforms/` son la verdad extendida. Alta cohesión (un fichero = un conector), bajo acoplamiento
> (los grupos referencian, no copian).

---

## 3. CAPÍTULO — Tier-1 marketplaces (6 unidades)

> **Detalle completo:** [`docs/runbook/groups/tier1-marketplaces.md`](docs/runbook/groups/tier1-marketplaces.md)
> + un fichero por conector en `docs/runbook/platforms/`.
> coches.net · milanuncios · wallapop · coches.com · autocasion · motor.es.

Los seis marketplaces VO/generalistas líderes. Modelo **platform-as-entity**: cada marketplace
es una fila `entity` con `kind='plataforma'` (sentinel provincia `00` = nacional), portadora de
receta y monitorizada. **Doble-membresía:** un coche físico en coches.net *y* wallapop = 1
`vehicle`, 2 aristas `platform_listing`. El **particular (C2C)** se modela como bucket
per-platform (sentinel sintético por plataforma), no per-seller ni per-province — el denominador
soberano cuenta puntos de venta REALES; los C2C son inventario servido atribuido a la
plataforma.

La verdad VAM por plataforma (verdict persistido vs live):

| Plataforma | `cdp_code` | data_surface | Governor | **verdict_id** | **verdict_N** | live_edges | delta |
|---|---|---|---|---:|---:|---:|---:|
| **coches.net** | `CDP-ES-00-TKRV45RP` | internal_api | JSON_API `web.gw.coches.net` (12 r/s) | **545** | **272.903** | 274.138 | +1.235 |
| **milanuncios** | `CDP-ES-00-E382JYEH` | internal_api | STEALTH `searchapi.gw.milanuncios.com` (ver nota) | **554** | **259.706** | 259.706 | 0 ✓ |
| **wallapop** | `CDP-ES-00-EMRH0TWQ` | app_api | JSON_API `api.wallapop.com` (12 r/s) | **592** | **565.128** | 575.353 | +10.225 |
| **coches.com** | `CDP-ES-00-XM91J1NZ` | next_data | STEALTH `www.coches.com` (1.0 r/s) | **551** | **91.066** | 92.088 | +1.022 |
| **autocasion** | `CDP-ES-00-QY06GW0B` | graphql | JSON_API GQL + STEALTH SSR (4.0 r/s) | **549** | **15.765** | 107.612 | **+91.847 ⚠** |
| **motor.es** | `CDP-ES-00-HSV4XZ2H` | json_ld | STEALTH `www.motor.es` (0.7 r/s) | **558** | **49.009** | 49.009 | 0 ✓ |

**Lectura honesta:** milanuncios (554) y motor.es (558) están cuadrados al coche (verdict ==
live), máxima confianza. coches.net / wallapop / coches.com tienen delta pequeño-medio (re-VAM
pendiente, no contradice el verdict). **autocasion (549)** tiene delta +91.847: el verdict avala
SOLO 15.765; los ~107k vivos vinieron de harvests sin re-VAM → **pendiente, NO validado** (§9).

- **3.1 coches.net** — gateway `web.gw.coches.net/search` UNCAPPED (el cap ~155k es solo UI;
  el gateway JSON enumera el 100%). Connectors `coches_net_wholesale.py` + `_facet.py` +
  `_segments.py`. VO slice **272.903 (id 545)**; segmentos `platform_segment_slice` TRUSTWORTHY:
  new 6.151 (584) · km0 3.107 (585) · renting 1.212 (587). Split dealer 155.086 · particular 117.817.
- **3.2 milanuncios** — gateway `searchapi.gw.milanuncios.com/v4/classifieds` FACET (province ×
  price-band; cap duro `from+size ≤ 10.000`; oráculo `totalHits` ES). Connector
  `milanuncios_wholesale.py`. **259.706 (id 554)**, split dealer 135.250 · particular 123.784.
- **3.3 wallapop** — gateway `api.wallapop.com/api/v3/search/section` UNCAPPED por
  `order_by=newest` (la perilla de uncap; oráculo `remaining_documents`). Connectors
  `wallapop_wholesale.py` (flat-cursor) + `_facet.py` (cola profunda). **565.128 (id 592)**;
  denominador oráculo ≈651.340 (cola profunda en §9).
- **3.4 coches.com** — SRP `__NEXT_DATA__` per-make FACET (20 coches/req; cap page 500 = 10k →
  partición por make). Connector `coches_com_wholesale.py`. **91.066 únicos (id 551)** — historial:
  id 548 REFUTED (111.498 con 20.432 fantasmas cross-surface; fix dedup → 551). Renting 1.034 (564).
- **3.5 autocasion** — GraphQL `gql.autocasion.com` + SSR make-facet (cap ES 10k → make →
  make×province para MERCEDES-BENZ >10k). Connectors `autocasion_facet.py` + `_wholesale.py`.
  **15.765 (id 549)**, dealer 15.765 · particular 0. ⚠ live 107.612 sin re-VAM (§9).
- **3.6 motor.es** — SSR `?pagina=N` make→model facet MECE (cap universal 50 páginas/facet →
  partición path). Connector `motor_es_wholesale.py`. **49.009 (id 558)**, dealer 49.009.

> **Nota governor milanuncios `[VERIFICADO]`:** el connector afirma host en "JSON_API class",
> pero `searchapi.gw.milanuncios.com` NO está en `_HOST_RATE_CLASSES` → hereda STEALTH 0.7 r/s
> en ejecución. No invalida el VAM (id 554 cuadra al coche); discrepancia comentario↔código
> en §9.

---

## 4. CAPÍTULO — OEM-VO portals (14 unidades)

> **Detalle completo:** [`docs/runbook/groups/oem-vo.md`](docs/runbook/groups/oem-vo.md)
> + un fichero por portal en `docs/runbook/platforms/`.

Un **portal OEM-VO** es la TERCERA especie de fuente: un fabricante-dueño publicando el stock
certificado de ocasión de su PROPIA red de concesionarios oficiales. No es marketplace, no hay
particulares. **Regla de propiedad:** los coches son de los concesionarios
(`vehicle.entity_ulid` → dealer `kind='compraventa'`), el PORTAL tiene 0 coches directos; el
coche EN el portal es una arista `platform_listing`. Las 14 entidades-portal se aíslan con
`entity.kind='oem_vo_portal'`.

**Disjunción `[VERIFICADO]`:** Σ por portal = `COUNT(DISTINCT vehicle)` sobre los 14 = **32.360**
(cero coches compartidos; cada marca publica solo su marca). Dealers oficiales distintos = **5.755**
(`COUNT(DISTINCT)`, no la suma — solape mínimo de 3 dealers entre programas).

| Portal | `cdp_code` | Cars | Dealers | `defense_tier` | `family` | Verdict id |
|---|---|--:|--:|---|---|--:|
| **spoticar** (Stellantis) | `CDP-ES-00-D6X2282Y` | **6.138** | 136 | `t1_soft` | stellantis_vo | **573** |
| **mercedes_benz** | `CDP-ES-00-A57R0YK8` | **4.792** | 4.749 | `t0_open` | mercedes_benz_vo | **515** |
| **toyota_lexus** | `CDP-ES-00-GNAJ5S16` | **3.834** | 129 | `t0_open` | toyota_lexus_vo | **572** |
| **audi** | `CDP-ES-00-NP3AWN4X` | **3.798** | 56 | `t0_open` | audi_vo | **482** |
| **bmw** | `CDP-ES-00-ZXZD056M` | **2.848** | 51 | `t1_soft` | bmw_group_vo | **524** |
| **hyundai** | `CDP-ES-00-C2SVJWB5` | **1.994** | 63 | `t1_soft` | hyundai_vo | **569** |
| **volvo_jlr_suzuki** | `CDP-ES-00-T0G18J3M` | **1.801** | 98 | `t1_soft` | volvo_jlr_suzuki_vo | **571** |
| **nissan** | `CDP-ES-00-TDWVVTAF` | **1.622** | 41 | `t0_open` | nissan_intelligent_choice | **566** |
| **kia** | `CDP-ES-00-YK54F18S` | **1.519** | 63 | `t1_soft` | kia_vo | **570** |
| **seat_cupra** | `CDP-ES-00-3N995HG6` | **1.323** | 87 | `t1_soft` | seat_cupra_vo | **567** |
| **renew** (Renault Group) | `CDP-ES-00-DT59NK3D` | **918** | 115 | `t0_open` | renault_group | **423** |
| **mini** | `CDP-ES-00-EV9ECTV7` | **678** | 83 | `t1_soft` | bmw_group_vo | **527** |
| **das_weltauto** (VW Group) | `CDP-ES-00-XWX9RHG7` | **552** | 56 | `t1_soft` | vw_group | **428** |
| **ford** | `CDP-ES-00-ZB6C77HC` | **543** | 31 | `t1_soft` | ford_vo | **488** |
| **TOTAL** | — | **32.360** | **5.755** | — | — | **14/14 TRUSTWORTHY** |

**Convergencia VAM:** en los 14, `db_edges == db_join_vehicles == primary_value` exacto; la
`divergence` solo aparece en `harvested_cageable` (snapshot API ligeramente por detrás de la DB
tras re-runs), toda dentro de tolerancia → TRUSTWORTHY. Receta UNA (no un fork): los 14
conectores espejan `spoticar_wholesale.py` / `oem_toyota_lexus_wholesale.py` (misma doble
membresía, misma jaula bulk, mismo cableado governor/health/VAM). 3 hosts en JSON_API
(`es.renew.auto`, `scs.audi.de`, `kiaokasion.net`); el resto STEALTH default.

Superficies por portal (resumen): spoticar Drupal/ES API JSON · mercedes_benz SSR+AJAX `/ajxvl` ·
toyota_lexus Toyota-Europe USC API · audi SCS `scs.audi.de` (token público `FJ54W6H`) · bmw/mini
Motorflash SSR barrido por dealer (BMW slash final / MINI sin slash) · hyundai OpenCart listado
plano + directorio · volvo_jlr_suzuki dos backends (Codeweavers + GForces AVL) un conector ·
nissan Next.js + AppSync GraphQL + Cognito idToken público · kia servlet IIS barrido por cluster ·
seat_cupra VTP `vtpapi.seat.com` paginación por headers · renew AEM loader React-Router `.data` ·
das_weltauto AEM SSR por provincia + Motorflash · ford SPA eUsed Akamai gate consumidor blando.

---

## 5. CAPÍTULO — Otros grupos: chains · rentacar · subastas (10 unidades)

> **Detalle completo:** [`groups/chains.md`](docs/runbook/groups/chains.md) ·
> [`groups/rentacar-vo.md`](docs/runbook/groups/rentacar-vo.md) ·
> [`groups/subastas.md`](docs/runbook/groups/subastas.md) + un fichero por conector en
> `docs/runbook/platforms/`.

Las tres fuentes no-marketplace y no-OEM-VO. Misma arquitectura única (governor + GeoResolver +
doble-membresía + ingesta idempotente + delta + VAM). Tres veredictos `group_vam` persistidos
cubren el dominio:

| `id` | grupo | `primary_value` sellado | live actual | `verdict` |
|---:|---|---:|---:|---|
| **541** | `chains` | **37.319** | 39.201 | TRUSTWORTHY (div 0.0) |
| **542** | `rentacar_vo` | **166** | 215 | TRUSTWORTHY (div 0.0) |
| **543** | `subastas` | **27** | 6.785 | TRUSTWORTHY (div 0.0) |

**Disjunción `[VERIFICADO]`:** `DISTINCT(edges ∪ owned)` = 46.201 = 39.201 (chain) + 215
(rentacar) + 6.785 (subastas) → ningún vehículo compartido entre los tres. Los tres veredictos se
sellaron a las 00:37Z; drenes posteriores commiteados ampliaron el live por encima del verdict
(el verdict es la validación formal; el live se reporta como cross-check, no como certificado).

### 5.1 GRUPO `vo_chains` (verdict 541) — 4 miembros validados

Connector `group_vo_chains_wholesale.py`. Governor: `services.flexicar.es` → JSON_API; resto
STEALTH (`www.ocasionplus.com` override 1.0). Todos `t0_open`.

| Miembro | `cdp_code` | Surface | edges vivos | Atribución |
|---|---|---|--:|---|
| **Flexicar** | `CDP-ES-00-FYECEGD5` | REST `services.flexicar.es/api/v1/vehicles` (JSON, size cap 24) | **23.874** | per-branch (186 sucursales) |
| **OcasionPlus** | `CDP-ES-00-SWN09H0C` | SSR JSON-LD `ItemList` (`?page=N`) | **13.445** | chain-as-owner |
| **Clicars** | `CDP-ES-00-QCMVM26T` | SSR HTML `__NEXT_DATA__` cards | **1.470** | chain-as-owner |
| **Carplus** | `CDP-ES-00-4YVMXZ3T` | SSR JSON-LD `Vehicle` | **412** | chain-as-owner |

### 5.2 GRUPO `rentacar_vo` (verdict 542) — 3 miembros validados

Connector `group_rentacar_vo_wholesale.py`. Rent-a-car single-operator → la empresa es el punto
de venta y dueña de cada coche. Precio retail 100% no-NULL.

| Miembro | `cdp_code` | Surface | edges vivos |
|---|---|---|--:|
| **OK Mobility** (base del verdict) | `CDP-ES-07-KWGRMQ7B` | SSR HTML `okmobility.com/en/buy-car/used` | **169** |
| **Centauro** | `CDP-ES-03-BMPR08V3` | SSR `ventas.centauro.net/coches-ocasion/?pagina=N` (hidden inputs) | **28** |
| **Record Go** | `CDP-ES-12-H26EC1KD` | CMS DealerK/MotorK `vcard-*` (`?page=N`) | **18** |

Verdict 542 certificó 166 (OK Mobility solo, snapshot 00:37Z); Centauro+Record Go están en la DB
viva bajo `source_group=rentacar_vo` (dentro del verdict por pathA). Live actual del grupo: 215.

### 5.3 GRUPO `subastas` (verdict 543) — 3 plataformas validadas

**PRICE-GATE honesto:** precio NULL por diseño en los 6.785 lotes (puja con login: Ayvens
`fixedPrice` solo tender, BCA `CanViewPricing=false`, Autorola `loginRequired=true`). El vehículo
es público y se cagea; el precio jamás se inventa (`price_gate='bid_login_gated'`).

| Plataforma | `cdp_code` | family | edges vivos | Surface |
|---|---|---|--:|---|
| **Ayvens Carmarket** (base del verdict) | `CDP-ES-00-H1VCV020` | ayvens_carmarket | **3.977** | GraphQL `api-carmarket.ayvens.com` (JSON_API) |
| **BCA España** | `CDP-ES-00-WYJKTP6S` | bca_europe | **1.752** | SPA faceted-search vía stealth browser JS (Cloudflare) |
| **Autorola** | `CDP-ES-00-RJ109M0T` | autorola | **1.056** | SPA REST `old.autorola.es` vía stealth browser (JWT anón) |

> **Nota Autorola/BCA `[VERIFICADO]`:** los docs viejos los listaban "GATED sin data-layer
> público" (sonda `curl_cffi` sin JS que no arranca los SPA Angular). Conducidos por stealth
> browser JS-executing (`scripts/cage_autorola_bca_subastas.py`), ambos exponen el stock per-lote
> ES sin login (precio sigue gateado → NULL). El código + DB viva (3 plataformas, 6.785 aristas)
> mandan sobre el `.md` aspiracional → entran al runbook.

---

## 6. CAPÍTULO — Long-tail: own-site, multiplicador CMS/DMS (7 unidades)

> **Detalle completo:** [`docs/runbook/groups/long-tail.md`](docs/runbook/groups/long-tail.md)
> + un fichero por familia en `docs/runbook/platforms/family-*.md`.

Más allá de Tier-1 y OEM-VO, el inventario vive en la **web propia de cada dealer**. Rasparlos
uno a uno no escala; el multiplicador es la **familia CMS/DMS**: agrupar dealers por la
plataforma que corre su web y escribir UNA receta por familia. **Modelo de propiedad:** la web
propia es la fuente PRIMARIA → **sin arista `platform_listing`**, cada coche es
`vehicle.entity_ulid = el dealer` (propiedad singular y directa).

**Totales own-site vivos `[VERIFICADO]`:** **20.165** coches own-site (website + owned +
no-edge). Las 7 familias VAM-firmadas (`subject_type='family_slice'`, `divergence=0.0`):

| source_key | verdict id | primary_value (VAM) | health / breaker |
|---|---:|---:|---|
| `family_dealerk_wp` | **606** | **2.270** | healthy / closed |
| `family_builder_wholesale` | **598** | **1.224** | healthy / closed |
| `family_generic_custom` | **597** | **1.029** | healthy / closed |
| `family_dms_vendor_platforms` | **596** | **799** | healthy / closed |
| `family_cms_wp` | **535** | **518** | healthy / closed |
| `family_framework_webbuilder` | **525** | **358** | healthy / closed |
| `family_unreachable` | **498** | **246** | healthy / closed |
| **TOTAL VAM family-slice** | — | **6.444** | 7/7 healthy, 7/7 closed |

Cada verdict reza `paths={'db_family_vehicles':N, 'harvested_pairs':N, 'cars_ingested_distinct':N}`
con los tres iguales y `divergence=0.0`. Tres conteos legítimos NUNCA conflados: (1) VAM harvest
slice = pares `(dealer, deep_link)` firmados (tabla, la cifra fiable); (2) no-edge def #2
(superset own-site); (3) global 20.165.

Las 7 familias (resumen; todas STEALTH default, t0_open salvo unreachable t1_browser):

- **6.1 `family_dealerk_wp`** (606, **2.270**) — DealerK/MotorK WordPress, markup `vcard-*`
  byte-idéntico. Connector `family_dealerk_wholesale.py`.
- **6.2 `family_dms_vendor_platforms`** (596, **799**) — inventario.pro + motorflash (dos
  subfamilias, una receta). Connector `family_dms_vendor_platforms__wholesale.py`.
- **6.3 `family_cms_wp`** (535, **518**) — WordPress-dominado; Strategy A Vehica REST
  `/wp-json/vehica/v1/cars` + Strategy B HTML cards ranked-slug. Connector
  `family_cms_wordpress_dominated__wholesale.py`.
- **6.4 `family_generic_custom`** (597, **1.029**) — bespoke; UN spine drena N recetas
  per-dealer en `REGISTRY`. Connector `family_generic_custom_wholesale.py`.
- **6.5 `family_framework_webbuilder`** (525, **358**) — Next/Astro/Nuxt/Angular SaaS; sitemap +
  JSON-LD `Car`. Connector `family_framework_next_astro_nuxt_angular__wholesale.py`.
- **6.6 `family_builder_wholesale`** (598, **1.224**) — Wix/Ueni/Google Sites/…; schema.org
  `ItemList` JSON-LD degradado en estrategias. Connector
  `family_builder_wix_ueni_google_sites_basekit__wholesale.py`.
- **6.7 `family_unreachable`** (498, **246**) — Tier-1 browser-only; body-gate ciego al status
  (hrmotor.com sirve listado bajo 403 honeypot). Connector `family_unreachable_wholesale.py`.
  Re-test stealth de las 92 unreachable con camoufox: 1 recuperado, 89 genuinamente muertas (§9).

---

## 7. CAPÍTULO — Motor · Geo · VAM · S-HEALTH · API · Esquema (8 unidades)

> **Detalle completo:** [`docs/runbook/01-ARCHITECTURE.md`](docs/runbook/01-ARCHITECTURE.md).

La arquitectura transversal: el sistema único por el que fluyen los seis grupos. Estado vivo de
la flota (la cicatriz AS24 NO se repite, recontado esta sesión): `source_breaker` 35 closed / 0
open · `source_health` 33 healthy / 2 degraded / 0 down · `harvest_run` 170 ok / 9 fail.

- **7.1 GOVERNOR** (`pipeline/engine/governor.py`) — token-bucket por host registrable, único
  choke point. Dos clases: **STEALTH** (0.7 r/s default, la cicatriz codificada) y **JSON_API**
  (12 r/s, gateways first-party). 8 hosts JSON_API + overrides STEALTH explícitos (AS24 0.5,
  coches.com 1.0, autocasion SSR 4.0, …). Validado: 0 breakers abiertos + battle-test 25/25 PASS.
- **7.2 FETCH** (`pipeline/engine/fetch.py`) — motor tiered `curl_cffi` `chrome131`. Tier-0
  optimista; Tier-1 es un **seam que lanza `NotImplementedError`** (no fallback silencioso — el
  caller elige camoufox/Playwright explícito). Retry `{429,500,502,503,504}`, backoff jitter,
  **falla en voz alta** ante no-retryable. Validado vivo (Tier-0 + seam Tier-1 falla fuerte).
- **7.3 GEO** (`migrations/0001_geo.sql` + `0018`) — jerarquía INE `pais→PROVINCIA→COMARCA→ciudad`
  + `cdp_code` inmutable (`services/api/codes.py`). **Verdict `geo_hierarchy` id=581**: Path A
  (`entity.comarca_id` directo) == Path B (vía muni) = 240.245; 52/52 prov, 322/323 comarcas,
  8.130/8.132 muni con comarca (los 2 sin = Ceuta/Melilla).
- **7.4 VAM** (`verification_verdict`, `migrations/0004`) — el juez: ≥2 caminos ortogonales +
  invariante landed-count. Ledger vivo (recontado esta sesión): **587 veredictos, 577 TRUSTWORTHY,
  10 REFUTED**. `global_count` ids **577-580** (vehicle/entity/platform_listing/vehicle_event
  totals, `count*` == Σ partición, div 0).
- **7.5 S-HEALTH** (`pipeline/ops/health.py` + `migrations/0013`) — watchdog: `record_run` (único
  escritor, breaker trip a 3 fallos), `build_origin` (origen exacto machine-readable), `fire_alert`
  (dedup: 138 dealers = 1 alerta), `classify_failure` (€0 determinista), `auto_repair`. Validado:
  battle-test 25/25 PASS cascada E2E. `repair_attempt` coherente con spend-gate P10.
- **7.6 API** (`services/api/main.py`) — FastAPI envelope `{ok,data,error,meta}`, 9 endpoints
  (health/entities/inventory/delta/geo-tree/completeness/platforms/vehicle-platforms). **Verdict
  `api_serves` id=583**: `/geo/28/tree` API `entities_geo_clean` == DB Path B exacto (reconcile
  A==B vivo). Arranque confirmado vivo esta sesión.
- **7.7 ESQUEMA** — migraciones `0001-0019` (huecos 0008/0010-0012/0014-0015 intencionados).
  Enums vivos: `entity_kind` (13 valores), `defense_tier` (t0..t4), `source_group` (11),
  `entity_role` (6). `platform_listing` = arista dual-membership (PK `(vehicle, platform)`,
  `segment` used/new/km0/renting). `vehicle_event` delta append-only.
- **7.8 WATERMARK dedup cross-platform** — `dedup_watermark` **id=582** (partición 1:1 limpia,
  0 vehículos multi-plataforma) + `cross_platform_dedup_watermark` **ids 556/559/574** (cota
  inferior sobre-conteo same-car ≈134.027, **MEASURE-ONLY, NO merge** — confesado, `photo_hash`
  sin poblar).

---

## 8. VALIDATION INDEX — el ledger (unidad → verdict id → count → CLI)

> Cada fila es una unidad validada: su `verification_verdict` TRUSTWORTHY (id), su count, y el
> CLI exacto que la reproduce. `$PY = C:/Users/elias/AppData/Local/Programs/Python/Python311/python`
> · `DSN = postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`. **45 unidades validadas.**
> **Ledger extendido (con fecha + motor):** [`docs/runbook/VALIDATION-INDEX.md`](docs/runbook/VALIDATION-INDEX.md).
> Las **55 verdict ids** de este índice se confirmaron una a una en la DB viva esta sesión (55/55
> encontradas, `primary_value` coincidente al dígito).

### 8.1 Tier-1 marketplaces (6)

| Unidad | verdict id | count | CLI |
|---|---:|---:|---|
| coches.net (VO slice) | **545** | 272.903 | `$PY -m pipeline.platform.coches_net_wholesale` |
| milanuncios | **554** | 259.706 | `$PY -m pipeline.platform.milanuncios_wholesale --pages 100` |
| wallapop | **592** | 565.128 | `$PY -m pipeline.platform.wallapop_wholesale --target 651000 --concurrency 6` |
| coches.com (VO) | **551** | 91.066 | `$PY -m pipeline.platform.coches_com_wholesale --all` |
| autocasion | **549** | 15.765 | `$PY -m pipeline.platform.autocasion_facet --makes all` |
| motor.es | **558** | 49.009 | `$PY -m pipeline.platform.motor_es_wholesale --full` |

### 8.2 OEM-VO portals (14)

| Unidad | verdict id | count | CLI |
|---|---:|---:|---|
| spoticar | **573** | 6.138 | `$PY -m pipeline.platform.spoticar_wholesale --pages 528` |
| mercedes_benz | **515** | 4.792 | `$PY -m pipeline.platform.oem_mercedes_benz_wholesale --pages 401` |
| toyota_lexus | **572** | 3.834 | `$PY -m pipeline.platform.oem_toyota_lexus_wholesale --pages 80` |
| audi | **482** | 3.798 | `$PY -m pipeline.platform.oem_audi_wholesale --pages 40` |
| bmw | **524** | 2.848 | `$PY -m pipeline.platform.oem_bmw_mini_wholesale --brand bmw` |
| hyundai | **569** | 1.994 | `$PY -m pipeline.platform.oem_hyundai_wholesale` |
| volvo_jlr_suzuki | **571** | 1.801 | `$PY -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale --pages 20` |
| nissan | **566** | 1.622 | `$PY -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 104` |
| kia | **570** | 1.519 | `$PY -m pipeline.platform.oem_kia_wholesale` |
| seat_cupra | **567** | 1.323 | `$PY -m pipeline.platform.oem_seat_cupra_wholesale --pages 14` |
| renew | **423** | 918 | `$PY -m pipeline.platform.renew_wholesale --pages 8` |
| mini | **527** | 678 | `$PY -m pipeline.platform.oem_bmw_mini_wholesale --brand mini` |
| das_weltauto | **428** | 552 | `$PY -m pipeline.platform.dasweltauto_wholesale --provinces 3 --pages 8` |
| ford | **488** | 543 | `$PY -m pipeline.platform.oem_ford_wholesale --pages 1` |

### 8.3 Otros grupos — chains · rentacar · subastas (10)

| Unidad | verdict id (grupo) | count (edges vivos) | CLI |
|---|---:|---:|---|
| chains/Flexicar | **541** | 23.874 | `$PY -m pipeline.platform.group_vo_chains_wholesale --members flexicar --pages 1000` |
| chains/OcasionPlus | **541** | 13.445 | `$PY -m pipeline.platform.group_vo_chains_wholesale --members ocasionplus --pages 1000` |
| chains/Clicars | **541** | 1.470 | `$PY -m pipeline.platform.group_vo_chains_wholesale --members clicars --pages 1000` |
| chains/Carplus | **541** | 412 | `$PY -m pipeline.platform.group_vo_chains_wholesale --members carplus --pages 1000` |
| rentacar/OK Mobility | **542** | 169 | `$PY -m pipeline.platform.group_rentacar_vo_wholesale --member okmobility --pages 6` |
| rentacar/Centauro | **542** | 28 | `$PY -m pipeline.platform.group_rentacar_vo_wholesale --member centauro` |
| rentacar/Record Go | **542** | 18 | `$PY -m pipeline.platform.group_rentacar_vo_wholesale --member recordgo` |
| subastas/Ayvens Carmarket | **543** | 3.977 | `$PY -m pipeline.platform.group_subastas_wholesale` |
| subastas/BCA España | **543** | 1.752 | `$PY scripts/cage_autorola_bca_subastas.py --bca bca_es_full.json` |
| subastas/Autorola | **543** | 1.056 | `$PY scripts/cage_autorola_bca_subastas.py --autorola autorola_es_full.json` |

> Grupo-level: chains (37.319 sellado / 39.201 vivo) · rentacar (166 / 215) · subastas (27 / 6.785).
> El verdict de grupo cubre cada miembro por su pathA `source_group`/`kind`.

### 8.4 Long-tail family-slices (7)

| Unidad | verdict id | count (VAM) | CLI |
|---|---:|---:|---|
| family_dealerk_wp | **606** | 2.270 | `$PY -m pipeline.platform.family_dealerk_wholesale --from-db --limit 5` |
| family_builder_wholesale | **598** | 1.224 | `$PY -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale --from-fingerprints --limit 12` |
| family_generic_custom | **597** | 1.029 | `$PY -m pipeline.platform.family_generic_custom_wholesale --all` |
| family_dms_vendor_platforms | **596** | 799 | `$PY -m pipeline.platform.family_dms_vendor_platforms__wholesale --seeds` |
| family_cms_wp | **535** | 518 | `$PY -m pipeline.platform.family_cms_wordpress_dominated__wholesale --from-db --limit 8` |
| family_framework_webbuilder | **525** | 358 | `$PY -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale --from-db --limit 6` |
| family_unreachable | **498** | 246 | `$PY -m pipeline.platform.family_unreachable_wholesale --dealers hrmotor.com` |

### 8.5 Motor · Geo · VAM · S-HEALTH · API · Esquema (8)

| Unidad | verdict id | count / estado | CLI de verificación |
|---|---:|---|---|
| GOVERNOR (cicatriz AS24) | — (battle-test 25/25) | 35 closed / 0 open | `$PY -c "from pipeline.engine.governor import governor, host_of; ..."` |
| FETCH (curl_cffi tiered) | — (validado vivo) | Tier-0 OK + seam Tier-1 falla fuerte | `$PY -c "from pipeline.engine.fetch import fetch_text; print(len(fetch_text('https://example.com')))"` |
| GEO hierarchy | **581** | A==B = 240.245; 52/52 prov | ver [`01-ARCHITECTURE.md §4`](docs/runbook/01-ARCHITECTURE.md) |
| VAM global_count | **577-580** | vehicle/entity/PL/event totals | `$PY -c "...verification_verdict WHERE subject_type='global_count'..."` |
| S-HEALTH | — (battle-test 25/25) | 33 healthy / 2 degraded / 0 down | `$PY -c "...source_health GROUP BY status..."` |
| API serves | **583** | `/geo/28/tree` A==B exacto | `$PY -m uvicorn services.api.main:app --port 8096` |
| SCHEMA migrations | — (verificado) | 0001-0019 aplicadas | `$PY -c "...schema_migrations ORDER BY version..."` |
| WATERMARK dedup | **582 + 556/559/574** | 1:1 limpia (0) + ≈134k measure-only | ver [`01-ARCHITECTURE.md §8`](docs/runbook/01-ARCHITECTURE.md) |

---

## 9. NO validado (fuera del runbook) — apéndice

> Declarado explícito, sin maquillaje. NO entra al cuerpo porque carece de verdict TRUSTWORTHY
> que avale el número, o hay discrepancia código↔doc, o es conocido-roto. Consolidado de los
> apéndices de las cinco secciones.

**Tier-1:**
1. **autocasión ~107.612 vivas (delta +91.847)** — el verdict máximo (549) avala solo 15.765;
   crecimiento sin re-VAM. Acción: re-correr el VAM y persistir verdict nuevo antes de subir el número.
2. **wallapop cola profunda → ~651k (G1)** — oráculo da ≈651.340; validado 565.128 (592). Resto
   exige paginación facet/cursor profunda no completada.
3. **deltas coches.net / wallapop / coches.com (+1.235 / +10.225 / +1.022)** — ingesta post-verdict;
   frontera de re-VAM (no contradice el verdict).
4. **discrepancia governor milanuncios** — connector afirma JSON_API, pero el host hereda STEALTH
   0.7 r/s. Registrar el host o corregir el comentario.
5. **coches.com doble-conteo histórico (id 548 REFUTED)** — 20.432 fantasmas cross-surface; ya
   corregido a 91.066 (551). Deuda dedup general abierta.

**OEM-VO (reconocidos, sin surface data-layer limpia):**
6. **Mazda** (`mazdaselected.es`) — AMURALLADO (TLS timeout a curl_cffi).
7. **Honda** (`vehiculosdeocasion.honda.es`) — SIN DATA-LAYER (jQuery SSR, sin JSON).
8. **Suzuki** (`auto.suzuki.es`) — DIFERIDO long-tail (~30 subsitios `redsuzuki.es` sin JSON central).

**Otros grupos:**
9. **rentacar:** Sixt ES (sin storefront VO ES), Europcar "2nd Move" / Goldcar (solo B2B con
   registro → duplicaría). **chains:** Aurgi, GpsAutos, Crandon (sin probe ni aristas).
   **subastas:** Allane (DE-céntrico), Aucto (connection refused).
10. **Desfase verdict↔DB chains/rentacar/subastas** — 541/542/543 certifican 37.319/166/27 (00:37Z);
    live creció a 39.201/215/6.785 sin re-VAM. Acción: re-emitir el VAM por grupo.

**Long-tail:**
11. **89 unreachable genuinamente muertas/walled** (39 NXDOMAIN + 50 hard wall) — confirmadas
    no-recuperables por camoufox stealth.
12. **avolo.net** (HTTP 500) y **renaultleioa.es** (0 precios own-site) — resuelven sin stock que cagear.
13. **9.828 cars own-site sin familia asignada** (de 20.165 globales) — long-tail real pendiente de
    asignar a familia, no validado como cosechado.
14. **roster generic excluido honestamente** — homepages OEM/global, delegadores cuyo stock vive en
    otro connector, shells JS sin cards SSR, parked/thin.
15. **miembros builder sin superficie machine-readable** (Wix warmupData, Squarespace/BaseKit vacío,
    Google Sites) — reachable-pero-sin-inventario-SSR (9 members → 2 productores).
16. **grupogamboa.com, setienherra.es** (inventario.pro) — cert errors; probable misma familia, no confirmados.

**Motor / esquema (defectos de calidad flagged, sin spend):**
17. **`organization` / `group_vam` VAM muerto** — tabla `organization` vacía (0 filas), `entity.org_id`
    NULL. Capa cadena/grupo existe en esquema pero no poblada.
18. **`source` veredictos REFUTED (5):** `oem_mg`(55), `oem_byd`(56), `oem_skoda`(57), `oem_hyundai`(59),
    `osm`(63) — conteo entidades ≠ declarado. NO servidos (outcomes de primera clase, no fallos del verificador).
19. **`long_tail_families` no aditivo (id 544 REFUTED)** — 10.083 ya en otros grupos; `family_*` es
    clasificador CMS, no partición disjunta.
20. **auto_repair efectos caros (P10-scaffold):** `refingerprint`/`escalate_tier`/`re_receta`
    `succeeded=FALSE`, `repair_outcome='pending'`. El LAZO corre real (€0); el EFECTO con gasto espera P10.
21. **escalada Tier-1 en `fetch.py`** — el seam lanza `NotImplementedError` (por diseño); el motor
    camoufox/Playwright vive FUERA de `fetch.py`.
22. **`platform.listing_counter` NULL en las 24 plataformas** · **API sin endpoint propio `oem_vo_portal`**
    (HTTP 400 guard). No usar `listing_counter` como fuente; el número real sale de `count(platform_listing)`.
23. **watermark cross-platform ≈134k excedentes** — MEASURE-ONLY; NO se ha ejecutado merge.

---

## 10. Regla de BITÁCORA VIVA (LIVING-LEDGER)

> **Este runbook es una bitácora viva: cada cierre E2E futuro se APPENDEA aquí. Obligatorio.**

Cada vez que se cierre algo **end-to-end y validado** (plataforma, receta, config, herramienta):

1. **Detalle:** crear `docs/runbook/platforms/<slug>.md` con la plantilla uniforme §3 del spec
   (identidad · data-layer · micro-acciones · receta/config · validación VAM con verdict id · CLI ·
   trampas), SOLO si el verdict es TRUSTWORTHY.
2. **Ledger:** añadir una fila a [`docs/runbook/VALIDATION-INDEX.md`](docs/runbook/VALIDATION-INDEX.md)
   (y al resumen §8 de aquí): `unidad | verdict id | count | CLI | fecha`.
3. **Capítulo:** referenciar la unidad desde su `docs/runbook/groups/<grupo>.md`.
4. **NO validado:** si se intentó y NO se validó → va a
   [`docs/runbook/NOT-VALIDATED.md`](docs/runbook/NOT-VALIDATED.md) (resumen §9 de aquí) con la
   evidencia del bloqueo, nunca al cuerpo.
5. **Commit:** `docs(runbook): <unidad> validada` → GitHub main.

**Definición de "validado y funcional" (la puerta, las tres a la vez):**
- existe fila `verification_verdict` **TRUSTWORTHY**, **Y**
- el conector re-ejecuta **idempotente** (re-run = 0 nuevos), **Y**
- el número concuerda por **≥2 caminos DB** ortogonales.

Si falta una, NO entra. La DB viva + el verdict persistido mandan siempre sobre cualquier `.md`
de rollup; donde discrepen, gana la DB y el delta se declara inline.

---

> **Cierre de honestidad.** Todas las cifras de este runbook son del verdict persistido (id
> citado) cruzado contra `cardeep-pg :5433` a 2026-06-13. Donde la ingesta viva supera el
> verdict, el delta se reporta como columna informativa y se marca como re-VAM pendiente en §9,
> nunca como número validado. 45 unidades validadas: 6 Tier-1 + 14 OEM-VO + 10 otros grupos + 7
> long-tail + 8 motor/geo/VAM/health/API. Lo no validado vive en §9, jamás disfrazado de cosechado.
