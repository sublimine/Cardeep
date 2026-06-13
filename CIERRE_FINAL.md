# CARDEEP — PARTE DE ENTREGA FINAL (auditoría adversarial, 2026-06-13)

> Estándar del owner: **NINGÚN número sin verificar; mejor confesar un hueco que vender una mentira.**
> Cada cifra de este documento fue contada por el Director a mano con `psycopg2` contra la DB viva
> `cardeep-pg :5433`, bajo snapshots `REPEATABLE READ`. La DB está **ingiriendo en vivo**: los valores
> absolutos suben entre snapshots. Donde lo declaro, el número es de un snapshot único punto-en-el-tiempo.

---

## 1. MARCADOR VERIFICADO (DB viva, snapshot único punto-en-el-tiempo)

### Globales (un solo snapshot congelado)
| Métrica | Valor verificado | Camino |
|---|---|---|
| `vehicle` (filas totales) | **1.030.185** | `count(*) FROM vehicle` |
| `entity` (puntos de venta + plataformas) | **207.934** | `count(*) FROM entity` |
| `platform_listing` (aristas) | **983.981** | `count(*) FROM platform_listing` |
| `vehicle_event` (delta/historial) | **1.033.279** | `count(*) FROM vehicle_event` |
| `vehicle` status=available | **1.028.810** | `count(*) WHERE status='available'` |
| Provincias con entidades | **52 / 52** | `distinct province_code` |
| Municipios con entidades | **4.181** | `distinct municipality_code` |
| Plataformas (`platform`) | **22** | `count(*) FROM platform` |

> El total de vehículos del proyecto es **1.030.185** en este snapshot. NO es la suma limpia de
> grupos disjuntos: incluye el doble-conteo cross-surface de coches.com (20.432, ver §2) y la capa
> long-tail que NO es aditiva-disjunta (ver §2). El número honesto "deduplicado y sin solapes" exige
> las correcciones de §2 antes de sumarse a una cifra global de marketing.

### Tier-1 marketplaces — VAM 3 caminos (snapshot único congelado)
| Plataforma | A: aristas-distinct vehicle | C: distinct listing_ref | Dealer | Particular | Veredicto |
|---|---|---|---|---|---|
| coches.net  | 272.903 | 272.884 | 155.086 | 117.817 | TRUSTWORTHY (div 0.00007) |
| milanuncios | 259.034 | 259.033 | 135.250 | 123.784 | TRUSTWORTHY (div 0.000004) |
| wallapop    | 224.596 | 224.577 | 157.255 |  67.341 | TRUSTWORTHY (div 0.00008) |
| coches.com  | 111.498 | **91.066** | 111.498 | 0 | **REFUTED (div 0.183)** |
| autocasion  | 16.225 | 16.225 | 16.225 | 0 | TRUSTWORTHY (div 0.0) |
| motor.es    | 30.497 | 30.497 | 30.497 | 0 | TRUSTWORTHY (div 0.0) |

- Path A (`platform_listing` aristas-distinct) **== Path B (vehicle-ownership join) EXACTAMENTE** en las 6:
  cero dup-explosion, cero aristas colgantes, cero owners huérfanos. Cada vehículo tiene exactamente 1 arista.
- Path C (distinct `listing_ref`) concuerda <0.01% en 5 plataformas; **REFUTA coches.com** (18,3% inflado).
- Split dealer/particular reconcilia exacto (suma == total, 0 huérfanos) en las 6.
- **Tier-1 suma de aristas (distinct-vehicle): 914.753 · deduplicado (distinct ref): 894.282.**

> NOTA DE DERIVA: el snapshot de la auditoría de veredictos persistió autocasion=15.765 y motor.es=29.847.
> El snapshot de cierre (más tarde, DB siguió drenando) los cuenta en 16.225 y 30.497. Ambos son ciertos
> en su propio instante. Las filas `verification_verdict` 549/550 conservan el valor del snapshot original.

Veredictos persistidos: `verification_verdict` ids **545–550** (`subject_type='platform_slice'`).

### Grupos no-marketplace — VAM ≥2 caminos (snapshot congelado)
| Grupo | Entidades | Vehículos | Veredicto | Notas |
|---|---|---|---|---|
| OEM-VO (14 portales) | 5.752 | **31.448** | TRUSTWORTHY (div 0.0) | Supera el SCOREBOARD viejo (22.222); la DB drenó más allá del checkpoint |
| Cadenas (Flexicar/OcasionPlus) | 187 | 37.319 | TRUSTWORTHY (div 0.0) | Bucket heterogéneo (mezcla Arval/Ayvens leasing, ver §2) |
| rentacar_vo (OK Mobility) | 1 | 166 | TRUSTWORTHY (div 0.0) | Entidad única |
| subastas (Ayvens) | 2 | 27 | TRUSTWORTHY (div 0.0) | Anclado en `kind=subasta` (su `source_group` es official_registry) |
| long_tail_families | 103 | 10.178 | **REFUTED (div 0.991)** | NO aditivo-disjunto: 10.083 ya pertenecen a directory/marketplace/oem_dealer_network |

- **CORE-4 (oem_vo, chain, rentacar_vo, subasta) es una partición LIMPIA**: 0 vehículos y 0 entidades
  en más de un grupo, a nivel entidad y vehículo. Suma core-4 = **68.960 vehículos**.
- OEM-VO: bamboleo de +32 vehículos root-caused a una entidad 'BYD Las Rozas de Madrid'
  (`source_key oem_byd`) correctamente clasificada `oem_dealer_network` (coche nuevo), NO uno de los 14
  portales VO usados. Artefacto de regex `^oem_`, no fallo de datos. Cifra autoritativa = 31.448.

Veredictos persistidos: `verification_verdict` ids **540–544** (`subject_type='group_vam'`).
`platform.listing_counter` = **NULL en las 22 plataformas** (no hay contador pre-calculado contra el
que cruzar; todos los conteos se derivan en vivo de `platform_listing`/`vehicle`/`entity`).

---

## 2. HUECOS DECLARADOS (sin maquillaje — lo que falta para el 100%)

### A. Defectos de calidad de datos confirmados en DB
1. **coches.com doble-conteo cross-surface (REFUTED, defecto real).**
   El scraper asigna un `vehicle_ulid` distinto por URL completa, pero el mismo listing aparece bajo
   `/coches-segunda-mano/` [25.247] y `/km0/` [15.617] con id= idéntico. 40.864 filas-vehículo colapsan
   a 20.432 listing-ids únicos. La cifra publicada 111.498 carga **20.432 vehículos fantasma (18,3% inflado)**;
   el conteo verdadero de listings distintos es **91.066**. Causa raíz: clave de identidad = URL, no listing-id.
   Flagged REFUTED en `verification_verdict` id=548. **Pendiente de fix de deduplicación por listing-id.**

2. **long_tail_families NO aditivo-disjunto (REFUTED).**
   98 de 103 entidades (10.083 de 10.178 vehículos) llevan un `source_group` primario de
   directory/marketplace_motor/oem_dealer_network. `family_*` es un clasificador CMS/DMS encima de un
   grupo primario, NO una partición. Solo 5 entidades / 95 vehículos son 'puros' (`source_group` NULL).
   Sumar long-tail como grupo independiente doble-contaría ~10.083 vehículos. Flagged REFUTED id=544.
   **Necesita regla de partición antes de incluirse en un total global.**

3. **Etiqueta 'chain' mezcla leasing con cadenas VO reales (data-quality, no doble-conteo).**
   `source_group='chain'` contiene Arval (6 entidades) y Ayvens (1) POS de leasing/rentacar más 177
   compraventa genéricas; solo Flexicar (2) + OcasionPlus (1) son cadenas VO reales por `trade_name`.
   El conteo 37.319 es internamente consistente en ambos caminos, pero la etiqueta del grupo es impura.

### B. Segmentos de marketplace no cosechados (techo del vector gratuito)
4. **wallapop → 651k.** El faceto cursor-plano drena ~224.6k; el total declarado por la fuente es ~651k.
   El resto exige paginación por faceta o cursor profundo aún no completado.
5. **coches.net new/km0/renting tras Imperva (~10k).** Los backends Imperva de nuevo/km0/renting están
   separados del VO ya cerrado (272.903) y requieren navegador con anti-bot, no alcanzable por XHR plano.
6. **coches.com renting XHR (~8.9k).** Endpoint XHR de renting en cola, no drenado.
7. **autocasion / motor.es segmentos VN/km0** post-VO no auditados por segmento.

### C. Fuentes muradas / con verja (gated)
8. **kia geo-skip** y portales OEM con data-layer murado (Mazda/Honda/Suzuki sin data-layer expuesto).
9. **subastas con verja (gated).** Ayvens Carmarket subasta = 27 vehículos visibles; el grueso está
   tras login/credenciales no provistas.
10. **Long-tail inalcanzable (`unreachable` family, 246 vehículos).** Webs propias de dealers que exigen
    **Tier-2 residential proxy** para superar defensa; no alcanzable con el vector gratuito actual.

### D. Caminos de verificación muertos / limitaciones de cross-check
11. **`organization` VAM muerto.** La tabla `organization` tiene 0 filas y `entity.org_id` es NULL en las
    207.934 entidades. El camino ortogonal org-type no se pudo ejecutar; se sustituyó por
    `entity_source.source_key`. Declarado, no fingido.
12. **`platform.listing_counter` NULL en las 22 plataformas.** No hay contador pre-calculado contra el que
    cruzar; todo se deriva en vivo. Sin segunda fuente independiente de conteo a nivel plataforma.
13. **Snapshot no es instante único cross-plataforma.** Cada fila de veredicto es internamente consistente
    dentro de su `REPEATABLE READ`, pero las 11 filas NO son un único instante. Un total Tier-1
    punto-en-el-tiempo exigiría un snapshot combinado (el §1 da una foto congelada aproximada).

### E. Bug de impresión cp1252 (Σ) en conectores — confirmado y reproducido
14. **`UnicodeEncodeError` en stdout cp1252 al imprimir el carácter Σ.** Confirmado real:
    `oem_bmw_mini_wholesale.py:1064` → `print(f"  declared full (Σtotal): {...}")`.
    Reproducido: `'Σ'.encode('cp1252')` → `'charmap' codec can't encode character 'Σ'`.
    En una consola Windows cp1252 (no-UTF8) este print **crashea el conector**. El símbolo Σ aparece
    también en recetas/docs y prints verbose de varios conectores. **No corrompe datos** (las escrituras
    a DB son UTF-8, verificado byte a byte en el front de calidad), solo rompe la salida de consola
    verbose en el vector afectado. Fix recomendado: `sys.stdout.reconfigure(encoding='utf-8')` al arranque
    o reemplazar Σ por 'sum' en los prints. **Pendiente.**

### F. Hueco de API (reportado, no fingido)
15. **`oem_vo_portal` no se sirve como catálogo propio.** `/entities/{cdp}/inventory` devuelve 0 (estos
    portales no poseen vehículos vía `vehicle.entity_ulid`) y `/platforms/{cdp}/inventory` los rechaza con
    HTTP 400 ('is kind oem_vo_portal, not a plataforma', guard de kind línea 122-123). Sus coches
    (ej. spoticar 5.884 aristas) solo son alcanzables indirectamente por el inventario de cada dealer dueño.
    14 entidades afectadas. Decisión pendiente: relajar el guard o nuevo endpoint.

### G. Acciones de auto-reparación con gasto (P10-scaffold, por diseño)
16. **Efectos con coste (refingerprint / escalate_tier / re_receta) scaffolded tras la puerta P10.**
    `repair_attempt.succeeded=FALSE`, `repair_outcome='pending'`, marcado explícito en código
    (`_SPEND_GATED_ACTIONS`, 'P10-SCAFFOLD'). El **lazo** de auto-reparación (clasificación + audit
    `repair_attempt` + alerta de origen exacto + breaker) SÍ corre real cada ciclo; `quarantine` y
    `escalate_owner` son 100% efectivas a coste 0. La ejecución del remedio caro queda pendiente de
    autorización de gasto. Honestamente NO fingido como hecho.

---

## 3. REGRESIONES ENCONTRADAS + CORREGIDAS

| # | Regresión | Estado | Evidencia verificada en DB |
|---|---|---|---|
| R1 | **trade_name vacío en 41 'particular'** (NULL/whitespace) | **CORREGIDA** | UPDATE idempotente `trade_name = 'Particular ' || provincia`. PRE=41, updated=41, **POST=0** (re-conteo en vivo: `0 blank/null trade_name`). Nombres acentuados válidos UTF-8 byte a byte (`b'Particular M\xc3\xa1laga'`). El '?' en consola es solo display cp1252. Filas 'Particular %' presentes: 109. |
| R2 | **coches.com doble-conteo cross-surface (18,3%)** | **DETECTADA + FLAGGED, fix pendiente** | Persistida REFUTED `verification_verdict` id=548 (div 0.183) para que NO se sume en silencio. Verdad = 91.066 listings únicos. Causa raíz documentada. |
| R3 | **long_tail doble-conteo (~10.083 veh)** | **DETECTADA + FLAGGED, regla pendiente** | Persistida REFUTED id=544 (div 0.991) para bloquear el doble-conteo en un total de grupo. |
| R4 | **SCOREBOARD OEM-VO obsoleto (22.222 vs 31.448 vivo)** | **CORREGIDA en SCOREBOARD** | Live DB = 31.448 (la DB drenó más allá del checkpoint). SCOREBOARD.md reescrito con el estado verificado. |

> Las regresiones R2/R3 son **defectos de calidad de datos del scraper**, no errores de mis caminos de
> conteo (verificados por la ruta `listing_url`, que también da 111.498 porque las URLs SÍ son distintas).
> Quedan honestamente flagged en el ledger como REFUTED en vez de maquilladas.

---

## 4. QUÉ SIGNIFICA "100%" DADO EL TECHO DEL VECTOR GRATUITO

El objetivo soberano (CLAUDE.md) es el 100% de los puntos de venta de España + plataformas con TODO su
inventario (usados, nuevos, km0, renting, particulares) en API viva con delta. El "100%" honesto tiene
**dos definiciones que no debo confundir**:

- **100% del vector GRATUITO (alcanzado / verificado):** todo lo cosechable por XHR/data-layer plano sin
  navegador de pago ni proxy residencial. Aquí el sistema está cerrado y verificado: las 5 plataformas
  Tier-1 limpias VAM-TRUSTWORTHY, los 4 grupos core-4 partición limpia, OEM-VO 31.448, API sirviendo 7
  endpoints sobre 207.934 entidades / 1.03M vehículos / 1.03M eventos delta, S-HEALTH (record→breaker→
  alerta de origen exacto→auto_repair→recovery) probado E2E contra la DB real.

- **100% ABSOLUTO de España (NO alcanzado — techo del vector gratuito):** exige superar lo declarado en §2:
  wallapop→651k, los segmentos Imperva/XHR de coches.net/coches.com, las subastas con verja, y la cola
  larga `unreachable` que necesita **Tier-2 residential proxy / navegador anti-bot de pago** (puerta de
  gasto P10). Esa última milla NO es alcanzable con el vector gratuito y queda **declarada, no fingida**.

**Veredicto de cierre:** el SISTEMA está cerrado y verificado al 100% en el vector gratuito; cada cifra
está contada por ≥2 caminos o marcada UNVERIFIED/REFUTED; cada hueco para el 100% absoluto está declarado
con su criterio de aceptación. **Cero números inflados. Cero huecos ocultos.**

---

## 5. EVIDENCIA / TRAZABILIDAD
- Veredictos en el ledger: `verification_verdict` ids 540–544 (group_vam) + 545–550 (platform_slice).
- Scripts de auditoría: `cardeep/scratch/` (vam_groups_audit.py, vam_groups_disjoint.py,
  vam_longtail_overlap.py, vam_groups_final.py) + scripts de verificación del Director.
- API probada en vivo (uvicorn 127.0.0.1:8093): /health, /entities/{cdp}/inventory, /entities/{cdp}/delta,
  /platforms/{cdp}/inventory, /geo/{prov}/entities — todos sirviendo coches reales con precio/make/model/geo.
- Sin `git commit` (por instrucción del owner).

---

## 6. SEGUNDA OLA — FRENTES POST-CIERRE (auditoría adversarial, 2026-06-13)

> Cada cifra de esta sección contada por el Director con `asyncpg`/`psycopg2` contra la DB viva
> `cardeep-pg :5433`, VAM ≥2 caminos ortogonales, con la verja de no-fingir intacta. La DB **siguió
> ingiriendo** tras el §1: los globales de abajo son un snapshot más reciente y por eso superan al §1.

### Globales (snapshot vivo único, `now()` = 2026-06-13 06:37:18 UTC, REPEATABLE READ)
| Métrica | §1 (snapshot anterior) | Valor actual verificado | Camino |
|---|---|---|---|
| `vehicle` (filas totales) | 1.030.185 | **1.332.617** | `count(*) FROM vehicle` |
| `vehicle` status=available | 1.028.810 | **1.331.242** | `count(*) WHERE status='available'` |
| `entity` (puntos de venta + plataformas) | 207.934 | **309.147** | `count(*) FROM entity` |
| `platform_listing` (aristas) | 983.981 | **1.286.413** | `count(*) FROM platform_listing` |
| `vehicle_event` (delta/historial) | 1.033.279 | **1.335.715** | `count(*) FROM vehicle_event` |
| Provincias con entidades | 52 / 52 | **52 / 52** | `distinct province_code` |
| Municipios con entidades | 4.181 | **4.712** | `distinct municipality_code` |
| Plataformas (`platform`) | 22 | **22** | `count(*) FROM platform` |

> El salto absoluto (≈+302k vehículos, +303k aristas) refleja los frentes de esta ola más la ingesta
> viva continua entre snapshots; NO debe leerse como una suma disjunta limpia. Las advertencias de §2
> (doble-conteo coches.com, long-tail no aditivo, dedup cross-plataforma) siguen vigentes sobre este total.

### A. wallapop facet → +37.731 aristas (techo del cursor plano superado)
- DB antes=457.766 aristas → tras runs de faceta=**495.497 aristas** (+37.731 coches verificados-nuevos
  que el cursor plano **nunca alcanzó**). Run profesional: 18/18 celdas limpias / 0 erroradas, +24.934
  aristas + 24.934 eventos delta NEW.
- **VAM 3 caminos DB ortogonales** (asyncpg propio, quiesced tras salida del proceso):
  PATH1 `platform_listing` edges = **495.497** == PATH2 distinct join-reachable vehicles = **495.497**
  (e==jv EXACTO) ; PATH3 distinct native `listing_ref` = **495.448** (|delta|=49 = 0,010%, re-listed
  native ids, dentro de tolerancia). Veredicto **TRUSTWORTHY**, health healthy / breaker closed, no-drop guard OK.
- Owners: 3.932 compraventa + 160.847 particular. Oracle de conteo vivo (next_page JWT
  `pointers.ORGANIC.remaining_documents`) baseline ≈ **651.328–651.372**.
- Cobertura capture-recapture: Σ(celda declarada) pro=348.058 + priv=344.286 vs baseline oracle 651k
  (overhang de band-boundary colapsado por dedup global de item-id).
- CLI: `python -m pipeline.platform.wallapop_facet --seller-types professional,private --cell-max 40000
  --target 700000 --concurrency 12` (HOST LIBRE, sin proxy/navegador, curl_cffi chrome131).

### B. coches.com renting XHR → 1.035 aristas (era 13)
- 1.035 aristas `platform_listing` de renting enjauladas: 1.034 del drenaje per-make MECE de hoy + 1
  oferta envejecida aún listada (BMW X1) del run previo. **1.034 = inventario paginable COMPLETO** de
  renting hoy; el `totalOffers=8767/~8908` del hub es una faceta HEADLINE (cada modelo contado por
  dealer/config), **NO un set paginable** — probado abajo.
- **VAM 4 caminos DB ortogonales ALL agree = 1.035**: PATH1 edges `LIKE '%renting-coches/%'` = 1.035 ;
  PATH2 distinct vehicles vía edge→vehicle join = 1.035 ; PATH3 `vehicle_event` NEW con
  `new_value->>'segment'='renting'` = 1.035 ; PATH4 distinct `listing_ref` (offer UUIDs) = 1.035.
  **(Re-verificado en este cierre: PATH1 live = 1.035 EXACTO.)**
- VAM in-run TRUSTWORTHY: harvested_cageable=1.034 == db_edges run-scoped=1.034 (el +1 BMW X1 envejecido
  excluido del peg in-run por `last_seen>=run_start`). Prueba MECE: Σ per-make `data.search.total` sobre
  52 makeOptions == |unión distinct card ids| == 1.034 exacto, 0 dups cross-make. Re-run idempotente
  (0 coches / 0 eventos), health=healthy, breaker=closed, 0 page errors, 39/39 makes completados.
- CLI: `python -m pipeline.platform.coches_com_wholesale --segment renting --all --concurrency 10`.

### C. OEM-VO geo + recuperación de provincia → grupo a 32.271 (era 31.448)
- **kia_vo** (`CDP-ES-00-YK54F18S`): edges=**1.519** == distinct vehicles=1.519 == distinct deep_links=1.519
  (VAM 3 caminos AGREE; 4º path listing_ref también=1.519), 63 dealers, 36 provincias, 0 huérfanos,
  0 bad-province. Drain vivo: declared_full=1.520, dealer_items=1.513, dup_ids=7, **geo_fallback_recovered=476**,
  geo_skipped 481→**0**. TRUSTWORTHY.
- **volvo_jlr_suzuki_vo** (`CDP-ES-00-T0G18J3M`): edges=**1.801** == vehicles=1.801 == deep_links=1.801
  (AGREE), 98 dealers, 38 provincias, 0 huérfanos/bad-province; geo_skipped 46→**0**, +46 aristas nuevas. TRUSTWORTHY.
- **nissan_intelligent_choice** (`CDP-ES-00-TDWVVTAF`): edges=1.622, geo_skipped=0 — **YA COMPLETO** (sin trabajo).
- **seat_cupra_vo** (`CDP-ES-00-3N995HG6`): edges=1.323=declared, geo_skipped=0 — **YA COMPLETO** (sin trabajo).
- Idempotencia: re-runs kia y volvo → 0 aristas nuevas / 0 geo-skip. **Grupo OEM-VO ahora 32.271 vehículos /
  5.755 dealers** (sube desde 31.448 del SCOREBOARD). Provincias recuperadas spot-checked en DB:
  kia Sant Boi→08 (242 cars NULL-muni: AR MOTORS 228 + DELTA PRAT 14), GRANDA SIERO→ASTURIANA prov 33,
  BIZKAIA→48, Granada→18, PALMA/MENORCA→07, Fuenlabrada→28, Oyarzun→20, San Ciprian de Viñas→32;
  volvo Oleiros→15 (muni 15058, 33 cars), Madrid→28 (muni 28079, 13 cars). Sumas distinct-province:
  476 (kia) + 46 (volvo) EXACTAS.
- CLI: `python -m pipeline.platform.oem_kia_wholesale` ; `python -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale`.

### D. Tier-1 residuales
- **milanuncios**: edges 259.034 → **259.706** (band prov29 vehicles 1.595 → 2.259, 12/12 bands clean).
- **motor.es VN**: edges 48.997 → **49.009** (offers 1 → 14), renting 0 enjaulado.
- VAM sacrificial-slot, ≥2 caminos DB: milanuncios listing rows 259.706 / prov29 band vehicles 2.259
  quorum **TRUSTWORTHY** ; motor.es listing rows 49.009 / km null offers 14 quorum **TRUSTWORTHY** ;
  renting cero — los 37 links son breadcrumb-only.

### E. cp1252 (Σ) global fix — RESUELVE el hueco §2.E / R-print
- **31 módulos `pipeline/platform/` parcheados** (cada uno recibe `def _force_utf8_stdout()` + una llamada
  como primera línea de `main()`); 2 ficheros correctamente saltados (`__init__.py` sin `main()`;
  `coches_com_wholesale.py` ya tenía el helper canónico que espejé). Total dir = 33 → 31 cambiados +
  1 pre-existente + 1 sin-main = **cobertura completa**.
- **VERIFICACIÓN 2 caminos DB-free**: (1) `importlib.import_module` sobre los 32 módulos con main →
  IMPORT OK 32 / FAIL 0 ; (2) `py_compile pipeline/platform/*.py` → todos OK. Audit de ocurrencias:
  cada fichero exactamente 1 def + 1 call (sin doble-insert).
- **PRUEBA FUNCIONAL root-cause** bajo stdout cp1252 simulado: BUG_REPRODUCED (print crudo de
  `'Σ → Híbrido Diésel Automática —'` lanza `UnicodeEncodeError`)=True ; FIX_WORKS (mismo print tras
  `_force_utf8_stdout` NO crashea)=True ; UTF8_BYTES_WRITTEN=True. `git status --porcelain` = exactamente
  los 31 `.py` modificados, nada más (patcher temporal + backup eliminados de scratch/).
- Esto **cierra el hueco §2.E (item 14)**: el bug cp1252 estaba "Pendiente" en el §2; ahora corregido y
  probado por raíz. CLI: `python -m py_compile pipeline/platform/*.py && python -c "import importlib,glob,os;
  [importlib.import_module('pipeline.platform.'+os.path.basename(p)[:-3]) for p in
  sorted(glob.glob('pipeline/platform/*.py')) if os.path.basename(p)!='__init__.py']"`.

### F. Jerarquía geo a escala (provincia → comarca → municipio)
- provinces=**52** ; comarcas=**323** en 50 provincias (Ceuta/Melilla 0 por construcción) ;
  municipalities=**8.132**, con comarca=8.130 (99,98%, solo 51001 Ceuta + 52001 Melilla sin cubrir).
- entities total=297.927, FULL prov+comarca+muni=231.425 (77,68%); 231.425/232.076=99,72% de las
  entidades muni-resueltas llevan comarca (el déficit 651 = Ceuta 466 + Melilla 185 exacto).
  vehicles total=1.287.200, FULL geo=877.026 (68,13%).
- **VAM Path A vs Path B** sobre comarca de entidad: count directo (231.425) == count vía join
  `geo_municipality` (231.425), drift **0**. Invariantes todos 0: drift entity.comarca_id vs
  municipality.comarca_id=0; cruces de provincia muni→comarca=0; entity→comarca=0; FK comarca→province
  huérfanos=0. Cobertura muni cross-check 2 vías (NOT NULL 8.130 == DISTINCT join 8.130). Fuente comarca:
  8.089/8.092 INE matched (3 códigos fusionados obsoletos), bug de parser corregido (Pontevedra header
  'Montaña' pelado). Trigger verificado vivo: insertar entity en muni 08019 auto-set comarca_id=50
  (Bajo Llobregat), rollback limpio. API viva (port 8097) `/geo/completeness` y `/geo/08/tree` consistentes;
  `/geo/51/tree` (Ceuta) → 0 comarcas correctamente.
- CLI: `python -m scripts.migrate up && python -m scripts.backfill_comarca && uvicorn services.api.main:app --port 8097`.

### G. Watermark de dedup cross-plataforma (mismo coche en ≥2 plataformas)
- **Cota INFERIOR estricta de sobre-conteo = 134.027 filas-vehículo excedentes** (suelo exacto:
  make+model+year+km+price+province coincidente abarcando ≥2 plataformas). **VAM 2 caminos**: SQL GROUP BY
  134.027 == Python set-grouping 134.027, divergencia 0,0% (snapshots previos 132.016/132.178 conforme los
  scrapers crecían). = **14,36% de tasa de dup cross-plataforma** sobre 933.417 listings candidatos de clave-completa.
- Strong-key (VIN-exacto) cross-plataforma: solo ≈110 grupos (`photo_hash` poblado en 0 vehículos; VINs
  reales de 17 chars en solo 18.087 de 1.293.546 vehículos). Ledger: `verification_verdict` ids 574 (y 556/566),
  `subject_type='cross_platform_dedup_watermark'`, verdict TRUSTWORTHY. `vin_ref` NO es VIN: almacena
  `v.listing_ref` (ad id nativo); solo len-17 charset-limpio son VINs reales.
- Esto **cuantifica el hueco de dedup global** que el §1 advertía sin cifra: el total 1.33M carga ≥134.027
  duplicados cross-plataforma. MEASURE-ONLY por defecto (no merge). CLI:
  `python -m scripts.cross_platform_dedup_watermark` (`--dry-run` rollback total ; `--merge-vin` colapso VIN-exacto reversible).

### H. S-HEALTH battle-test → 25/25 PASS, cascada probada E2E
- 25/25 checks PASS, RC:0. Cascada probada por filas DB vivas sobre clave desechable
  (`TEST_SHEALTH_CASCADE`): 3 fallos 403 consecutivos → `source_breaker` state='open' consecutive_fails=3,
  `breaker_tripped` edge una sola vez; `source_health` status='down' fails=3; `harvest_run` auditó los 3
  fallos; `fire_alert` UNA alerta deduped con origen exacto `TEST_SHEALTH_CASCADE:scrape`; `auto_repair`
  3 `repair_attempt` (action=refingerprint, succeeded=False = P10 spend-gated); classify matrix 6/6 correcto.
- Degradación elegante: `is_open(TEST)=True` (harvest lo salta) mientras el source real
  `coches_net_wholesale` quedó closed/healthy/0 byte-idéntico antes/después, y un 2º vecino desechable
  activo quedó closed/healthy (bulkhead no-vacuo). Snapshot servido por API inmóvil: entity 297.602→297.602,
  vehicle_available 1.282.647→1.282.647. Cooldown exponencial: 4º fallo ≈1.800s = 2× base 900s.
  Recovery: un run limpio → breaker closed/0, health healthy/0, alert resolved.
- **Audit 2º-camino independiente**: 0 residuo TEST en las 5 tablas; totales restaurados a baseline exacto
  (breaker=31, health=31, repair_attempt=7, alert=5). CLI: `python scratch/shealth_battletest.py` (PYTHONUTF8=1).

> **Cierre de la 2ª ola:** 8 frentes, cada cifra contada por ≥2 caminos DB ortogonales o probada por
> reproducción funcional. Se **cierra el hueco §2.E (cp1252)**. Se **cuantifica el hueco de dedup global**
> (≥134.027 cross-plataforma). wallapop sube a 495.497 aristas (+37.731 reales), renting a 1.035, OEM-VO a
> 32.271, milanuncios a 259.706, motor.es VN a 49.009. Cero números inflados; cada hueco restante (wallapop
> →651k, segmentos Imperva, subastas con verja, Tier-2 proxy) sigue declarado, no fingido.

---

## 7. TERCERA OLA — DOS VERJAS DERRIBADAS GRATIS (auditoría adversarial, 2026-06-13)

> Esta ola **mueve dos huecos de la columna "spend-gated" a la columna "cerrado-gratis"**. Ambos estaban
> declarados como bloqueadores con verja en §1/§2; el navegador stealth con JS los falsificó. Cada cifra
> contada por el Director con `psycopg2` contra `cardeep-pg :5433` bajo `REPEATABLE READ`. Veredictos
> persistidos en `verification_verdict` ids **584–587** (`subject_type='platform_segment_slice'`).

### A. coches.net VN/km0/renting tras Imperva → +10.470 aristas (era hueco §2.5 "~10k Imperva")
- **CRACKED FREE: 10.470 aristas** capturadas por **camoufox** (navegador SPA-router) interceptando el
  contrato del gateway, luego drenaje plano. El segmento VO (`used`) queda **inmóvil en 263.668**; los tres
  segmentos nuevos son aditivos limpios sobre él. coches.net total = **274.138 aristas** (263.668 + 10.470).
- **Desglose por segmento (VAM Path A `platform_listing` por `segment`, plataforma CDP-ES-00-TKRV45RP):**
  `new`=**6.151** · `km0`=**3.107** · `renting`=**1.212** = 10.470 exacto.
- **100% dealer-owned** (VAM 2º camino, JOIN edge→vehicle→entity): los tres segmentos cuelgan
  íntegramente de entidades `kind='compraventa'`. Dealers distintos: new→**230**, km0→**323**,
  renting→**45**. CERO particulares, CERO huérfanos. Veredictos ids 584/585/586/587 TRUSTWORTHY.
- Esto **cierra el hueco §2.5** (los backends Imperva de nuevo/km0/renting que el §2 declaraba
  "requieren navegador anti-bot, no alcanzable por XHR plano"): alcanzados gratis con camoufox.

### B. subastas Autorola + BCA → +140 lotes (PRIOR VEREDICTO REVOCADO)
- **CRACKED FREE: 140 lotes** por un **navegador stealth que ejecuta JS (Playwright)**, que arrancó las
  SPA Angular de www.autorola.es y bca.com y renderizó stock de coche por-lote público sin login.
- **REVOCACIÓN EXPLÍCITA DE VEREDICTO PREVIO:** `docs/architecture/tier1_recipes/subastas_datalayer.md`
  y `pipeline/platform/group_subastas_wholesale.py` declaraban Autorola+BCA **'GATED, sin data-layer
  público de lotes'** — basándose en una sonda `curl_cffi` **sin JS**. El navegador con JS **falsificó
  esa conclusión para ambos**. La sonda plana veía solo la shell SPA y los COUNTS agregados; la
  ejecución de JS reveló el stock real.
  - **AUTOROLA FREE:** www.autorola.es (SPA Angular, tras aceptar cookies) renderiza `/vehicles` +
    `/auctions` públicos con stock completo por lote, SIN login. Data layer:
    `GET https://old.autorola.es/rest/vehiclesearchenrollment/result?locale=es_ES&offset&limit[&auctionId]`
    → `groups[].vehicleDTOS[]` con `vehicleDTO.countryCode` (filtro ES). La subasta ES **671406** mostró
    públicamente 51 lotes de Madrid (p.ej. **Seat Arona 12/2024 64.740 km** — verificado byte a byte en DB).
- **Estado en DB viva (10 entidades `kind='subasta'`, 167 vehículos):**
  Autorola=**90** veh (2 entidades-subasta) · BCA Espana=**50** veh (6) · Ayvens Carmarket=**27** veh (2).
  Edges `platform_listing`: Autorola 90 + BCA 50 + Ayvens 27 = **167**. Las 3 plataformas subasta viven
  ahora en `platform` (de ahí el conteo de plataformas **22 → 24** y `kind='subasta'` 2 → 10).
- **Lo que sigue con verja (solo el PRECIO, NO el stock):** los 167 lotes traen make/model/year/km
  **completos**; el **precio es el único campo murado** (`price` NULL en 165 de 167 — `loginRequired=True`,
  bid-based). El stock está cerrado-gratis; la puja/precio exige login dealer. Honesto: el coche está, el
  precio de subasta no.
- Esto **degrada el hueco §2.C-9** ("subastas con verja, grueso tras login"): el *stock* de Autorola+BCA
  ya NO está con verja (cosechado gratis); lo que queda con verja es el **precio de puja** y la cola
  profunda per-subasta paginable (declared `lotsCount` en cientos, sin paginación key-free).

### Globales tras la 3ª ola (snapshot vivo único, `now()` ≈ 2026-06-13 07:04 UTC, REPEATABLE READ)
| Métrica | 2ª ola (§6) | 3ª ola (actual) | Camino |
|---|---|---|---|
| `vehicle` (filas totales) | 1.332.617 | **1.336.553** | `count(*) FROM vehicle` |
| `vehicle` available | 1.331.242 | **1.335.178** (+ gone 1.375 == count*) | `count(*) WHERE status='available'` |
| `entity` | 309.147 | **309.214** | `count(*) FROM entity` |
| `platform_listing` (aristas) | 1.286.413 | **1.290.349** | `count(*) FROM platform_listing` |
| `vehicle_event` (delta) | 1.335.715 | **1.339.652** | `count(*) FROM vehicle_event` |
| Plataformas (`platform`) | 22 | **24** | +Autorola +BCA (subastas) |
| Provincias / Municipios con entidades | 52 / 4.712 | **52 / 4.712** | `distinct province/municipality_code` |

> **Reconcile autoritativo (snapshot único REPEATABLE READ, certificación final_certification):**
> `now()`=2026-06-13 06:49:13 UTC → vehicle_total=**1.332.986** (available 1.331.611 + gone 1.375 ==
> count*); entity_total=**309.148** en 3 caminos idénticos: `count(*)` == `Σ kind` == `Σ role` = 309.148
> (kinds: particular 267.843, compraventa 31.150, garaje 7.219, concesionario_oficial 1.617, desguace
> 1.292, oem_vo_portal 14, plataforma 8→**ahora 10**, subasta 2→**ahora 10**, cadena 2, rent_a_car_vo 1);
> platform_listing=1.286.782; vehicle_event=1.336.085; platforms(role)=**22→ahora 24**. Re-verificado en
> este cierre a las 07:04 UTC: la DB siguió drenando (+3.567 vehículos), el reconcile de 3 caminos
> **sigue == exacto** (count*==Σkind==Σrole=309.214) y vehicle av+gone==count* sigue TRUE. La deriva
> absoluta es ingesta viva, NO descuadre: cada snapshot cuadra consigo mismo.

> **Cierre de la 3ª ola:** 2 verjas derribadas gratis. coches.net Imperva (§2.5) **cerrado** (+10.470
> aristas, 100% dealer-owned, VAM 2 caminos). subastas Autorola+BCA **stock cerrado-gratis** (140 lotes,
> veredicto previo 'GATED' revocado por navegador JS); solo el **precio de puja** queda con verja. Los
> huecos genuinamente con-gasto restantes (wallapop →651k profundo, Tier-2 residential proxy para la
> cola `unreachable`, precio de subasta tras login, P10 auto-repair caro) siguen declarados, no fingidos.
