# Auditoría adversarial Fase 2 — 2026-06-15

> Mandato: "AUDITA TODO el proyecto internamente, verifica coherencia y lógica de negocio.
> No confiamos en ningún resultado." Método: barrido adversarial multi-agente sobre 6
> dimensiones (A-datos, B-identidad, C-conectores, D-verificación, E-API, F-método/ops),
> read-only, evidencia obligatoria. CADA hallazgo fue re-verificado por un segundo camino
> independiente (query distinta, lectura de fuente, o prueba transaccional) antes de
> entrar a este backlog. Este documento es el registro triado de los 37 hallazgos
> confirmados REAL. Complementa —no reemplaza— `AUDIT_2026-06-15.md` (Fase 1): aquel
> selló B-1 (bug de escritura de quórum) y las fugas geo/status de la API; esta fase
> destapa el corpus heredado *grandfathered* que B-1 no retroactivó, y una clase entera
> de defectos CRÍTICOS de scheduler/conectores/evicción que Fase 1 no cubrió.

## Resumen ejecutivo

Treinta y siete hallazgos confirmados REAL (re-verificados átomo a átomo): **10 CRÍTICOS,
10 ALTOS, 11 MEDIOS, 6 BAJOS**. La señal dominante NO es corrupción de datos servidos hoy
—la API ya deduplica y filtra por las vistas correctas en la mayoría de rutas— sino una
**brecha sistémica entre lo construido y lo que late en cadencia**: el scheduler durable
nunca se ha arrancado contra la DB viva (sin tabla `apscheduler_jobs`), carece de cerrojo
singleton de host (recreando el escenario que costó 138 dealers AS24), y para CUATRO
plataformas Tier-1 (coches.net, wallapop, coches.com, motor.es) ejecuta en cadencia el
módulo de PRUEBA acotado (~500 coches / 16k / flat-cap) en vez del cosechador completo
(~272k / 651k / 92k / 51k) que existe pero está sin programar; autocasion además quedó
con CERO ruta de cadencia tras el swap a facet (key de `source_health` desincronizada de
la key del REGISTRY → alerta-y-nunca-recupera). En verificación, el 96,6% de los veredictos
TRUSTWORTHY (989/1024) son heredados con `quorum_n<2` porque `independent_values` se
guardó como objeto JSON (no array), la CHECK que lo prohíbe está `NOT VALID`, y la
cadena de auditoría tamper-evident solo cubre 46/1085 filas; el motor Inquisición (0032)
jamás ha adjudicado un claim en vivo. La evicción tiene un Gate-1 que une veredictos por
`entity_ulid` cuando todos los `entity_inventory` se claves por `cdp_code` → la mitad
protectora ("no evictar dealer vivo con TRUSTWORTHY activo") es código muerto (hoy
fail-closed, peligro latente). En la API, dos endpoints de inventario hacen INNER JOIN a
`v_canonical_vehicle` y **ocultan 9.827 coches disponibles de 1.329 dealers que muestran
stock CERO** (la brecha crece con cada cosecha hasta el siguiente clustering). En datos,
~400k coches (23,5%) tienen make+model NULL pese a título parseable, y precios centinela
(999.999.999€) y 0/1€ fluyen sin filtrar al producto. **El hallazgo más importante:
`E-inventory-innerjoin-dataloss` (CRÍTICO)** — viola directamente el contrato del producto
("sacarle TODO su stock"): 1.329 dealers reales devuelven inventario vacío por un INNER
JOIN que debería ser LEFT JOIN + COALESCE-a-sí-mismo, y es un peligro operativo *creciente*,
no un evento puntual. Ninguna dimensión salió limpia; la única nota positiva verificada es
`D-gestion-resolved-proof` (los guards forward 0034/0035/0036 SÍ funcionan y aceptan prueba
válida mientras rechazan no-pruebas).

### Conteo por dimensión

| Dim | CRÍTICO | ALTO | MEDIO | BAJO | Total |
|---|---|---|---|---|---|
| A — datos | 0 | 3 | 3 | 1 | 7 |
| B — identidad | 0 | 2 | 1 | 1 | 4 |
| C — conectores | 4 | 2 | 3 | 0 | 9 |
| D — verificación | 2 | 2 | 1 | 1 | 6 |
| E — API | 2 | 0 | 2 | 2 | 6 |
| F — método/ops | 2 | 1 | 1 | 1 | 5 |
| **Total** | **10** | **10** | **11** | **6** | **37** |

Ninguna dimensión "no encontró nada": las seis tienen al menos un hallazgo REAL.

---

## CRÍTICOS (10)

### Dimensión C — conectores (4)

#### C-cochesnet-scheduler-runs-500car-proof
- **Título:** El scheduler corre `coches_net_wholesale` (slice de PRUEBA 5 páginas / ~500 coches) en cadencia, en vez de `coches_net_facet` (~272k completo).
- **Ubicación:** `pipeline/ops/scheduler.py:130-131,329` ; `pipeline/platform/coches_net_wholesale.py:102,949,1122-1123` ; `pipeline/platform/coches_net_facet.py:440-441,526-539`.
- **Evidencia:** `SourceEntry("coches_net_wholesale","pipeline.platform.coches_net_wholesale",[])` con `extra_args` vacío; `_build_cmd`=`[python,-m,module,*extra_args]` → lanza `python -m pipeline.platform.coches_net_wholesale` sin `--pages`. `DEFAULT_MAX_PAGES=5`, argparse `--pages` default=5 → cosecha ~5×100=500. `coches_net_facet` escribe el MISMO `COCHES_SOURCE_KEY` (drop-in) y dren por partición provincia+banda-precio, pero NO está en el REGISTRY (grep=0). DB viva: `source_health` solo tiene `coches_net_wholesale` (24h, last_ok hoy); `platform_listing` de coches.net (CDP-ES-00-TKRV45RP) = 274.144 edges — órdenes de magnitud sobre lo que 5 páginas producen, prueba de que el inventario completo se construyó con un dren facet MANUAL mientras la cadencia solo refresca ~500.
- **Por qué importa:** En el latido vivo (24h) coches.net decae a una foto de ~500 coches entre drenes manuales; el inventario completo nunca se refresca en cadencia.
- **Fix propuesto:** Apuntar el módulo del SourceEntry a `pipeline.platform.coches_net_facet` con `extra_args=[]` (facet auto-particiona, no tiene `--pages`), exactamente como `autocasion_facet` ya reemplazó al wholesale en `scheduler.py:126-127`.

#### C-wallapop-scheduler-runs-flat-wholesale
- **Título:** El scheduler corre `wallapop_wholesale` (cursor flat newest, tope-profundidad ~347k) en vez de `wallapop_facet` (~651k por seller_type×precio, completo).
- **Ubicación:** `pipeline/ops/scheduler.py:136-137` ; `pipeline/platform/wallapop_wholesale.py:1277-1300` ; `pipeline/platform/wallapop_facet.py:8-9,515`.
- **Evidencia:** `SourceEntry("wallapop_wholesale","pipeline.platform.wallapop_wholesale",[])`. El docstring del facet declara que la pasada flat tapa ~347k antes de `remaining_documents→0`; el facet dren los 651.372 declarados por partición `seller_type×price-band`. `wallapop_facet` escribe el MISMO `WP_SOURCE_KEY` (drop-in) pero NO está en el REGISTRY. DB: wallapop (CDP-ES-00-EMRH0TWQ) = 592.790 edges (de drenes facet manuales; la cadencia es la flat wholesale). Nota: el wholesale corre flat-primario + un barrido suplementario de ~40 keywords×geo-centroide (tail-catcher), no es cursor flat *puro*, pero ese suplemento NO es la partición demostrable por conteo del facet.
- **Por qué importa:** Wallapop es el mayor inventario español de la DB (592k edges); en el latido 24h se sub-cosecha ~300k por debajo del catálogo declarado de ~651k. La cadencia no mantiene la profundidad que dieron los drenes manuales.
- **Fix propuesto:** `scheduler.py:136-137` → `SourceEntry("wallapop_wholesale","pipeline.platform.wallapop_facet",[])` (drop-in: misma key, misma fila de salud), igual que el patrón autocasion.

#### C-cochescom-scheduler-omits-all-flag
- **Título:** El scheduler corre `coches_com_wholesale` con `--limit 16000` por defecto (prueba acotada, solo VO); el dren completo de ~92.312 exige `--all`, nunca pasado.
- **Ubicación:** `pipeline/ops/scheduler.py:128-129` ; `pipeline/platform/coches_com_wholesale.py:154,180,1303,2071,2074`.
- **Evidencia:** `extra_args=[]` → argv sin `--all` ni `--segment`. `DEFAULT_LIMIT=16000`, `--all` store_true off, `--segment` default `SEGMENT_VO`; el gate real `cage_limit = None if drain_all else max(1, limit)` (línea 1303) tapa la jaula en 16000 con `drain_all=False`. `SEGMENT_VO=92381`. DB viva: `platform_listing` de coches.com (CDP-ES-00-XM91J1NZ) = 92.090 edges, 100% `used` (VO), CERO km0/vn/renting/catalog → solo producible por un `--all` manual. `source_health`: 24h, last_ok hoy.
- **Por qué importa:** Plataforma Tier-1 (la mayor a ~92k) sub-cosechada ~76k en cada tick programado; vn/renting NUNCA se refrescan; el censo decae en silencio entre drenes manuales.
- **Fix propuesto:** `extra_args=["--all","--segment","all"]` en el SourceEntry (resuelve tanto el tope como los segmentos ausentes).

#### C-motores-scheduler-omits-full-flag
- **Título:** El scheduler corre `motor_es_wholesale` con `--max-cells 6` / `--limit 10000` por defecto (prueba acotada, solo VO); el censo de ~50.932 exige `--full`, nunca pasado.
- **Ubicación:** `pipeline/ops/scheduler.py:134-135` ; `pipeline/platform/motor_es_wholesale.py:146-147,226-235,1283,1562,1578`.
- **Evidencia:** `extra_args=[]` → argv pelado. `DEFAULT_MAX_CELLS=6`/`DEFAULT_LIMIT=10000`; `--full` store_true off; `--segment` default `'vo'`. Gate `cells_to_drain = cells if full else cells[:max_cells]` (1283) — el tope solo se evita con `--full`. DB viva: `platform_listing` de motor.es (CDP-ES-00-HSV4XZ2H) = 49.011 edges, TODOS `used`, CERO `new` → firma de un `--full --segment vo` manual. `source_health`: 24h, last_ok hoy. `resolve_segments()` confirma `all`=vo+vn+renting (km0⊂vo, catalog⊃vn excluidos por redundancia) → `all` es la unión aditiva correcta sin pérdida.
- **Por qué importa:** Dos degradaciones en el latido: (a) el censo VO decae de ~50.932 hacia el tope ~10k según envejece el dren manual; (b) los segmentos vn/new NUNCA se refrescan.
- **Fix propuesto:** `extra_args=["--full","--segment","all"]` en el SourceEntry.

### Dimensión D — verificación (2)

#### D-grandfathered-trustworthy-no-quorum
- **Título:** 989 de 1024 veredictos TRUSTWORTHY tienen `quorum_n<2` — el inventario "verificado" del producto vivo nunca fue certificado por quórum.
- **Ubicación:** `verification_verdict` (vivo) ; `migrations/0026_verification_deep.sql:157-170` (CHECK NOT VALID) ; `pipeline/verify.py:124-146`.
- **Evidencia:** GROUP BY: TRUSTWORTHY total=1024, `quorum_n<2`→989, `>=2`→35. Mecanismo: `jsonb_typeof(independent_values)` → object=987, NULL=2 (los 989) vs array=35; `cdp_modal_cluster()` RETURNs 0 inmediato si el input no es array → los 989 forzados a `quorum_n=0`. `chk_trustworthy_needs_quorum` `convalidated=f` (NOT VALID). Por `subject_type`: entity_inventory=734, platform_slice=155, family_slice=38. Los sellos B1/β/B7 leen TRUSTWORTHY sin satisfacer q≥2∧family≥2∧origin≥2. *Caveat de blast-radius (corrige el why_it_matters original):* `services/api/` NO consume `verification_verdict` (0 referencias); la cadencia de cierre RESOLVED del gestionador está endurecida contra exactamente este caso (`route.py:243` + trigger 0036); evict Gate-1 trata un TRUSTWORTHY rancio como razón para BLOQUEAR borrado (fail-safe). El `verify.py` actual ya escribe arrays y gatea por `has_independence` → el defecto es DATA heredada, no escrituras nuevas.
- **Por qué importa:** La promesa de la Dimensión D ("ningún número es TRUSTWORTHY sin ≥2 caminos ortogonales") solo la cumplen 35 filas post-0026; el 96,6% son afirmaciones de verdad sin independencia forzada.
- **Fix propuesto:** Re-formar los 987 `independent_values` objeto/NULL a arrays (o recomputar los sellos), luego `VALIDATE CONSTRAINT chk_trustworthy_needs_quorum` para cerrar la ventana de grandfathering. (Es DATA-fix + re-VAM, no urgencia de servicio porque la API no los lee.)

#### D-evict-gate1-wrong-join-key
- **Título:** El Gate-1 de evicción une veredictos por `entity_ulid` pero TODOS los `entity_inventory` se claves por `cdp_code` — el gate es ciego al estado real del veredicto.
- **Ubicación:** `pipeline/evict.py:82-108` (`_GATE1_*_SQL`) vs `pipeline/ingest.py:154-161` ; `pipeline/verify.py:153-176`.
- **Evidencia:** El SQL del gate une `vv.subject_key = e.entity_ulid`; `ingest.py` escribe `subject_key=code` (el cdp_code). Prueba conductual sobre dealer real CDP-ES-46-NM30P5P0 (tiene TRUSTWORTHY *y* REFUTED): gate como-escrito → `has_trustworthy=FALSE`, `has_death_evidence=FALSE`; gate corregido a `cdp_code` → TRUE/TRUE. Longitudes disjuntas: `subject_key` len 18 (CDP-ES-46-NM30P5P0) vs `entity_ulid` len 26 — estructuralmente no pueden igualar. 750 veredictos entity_inventory, los 750 por cdp_code, 0 matchean entity_ulid.
- **Por qué importa:** Hoy el efecto neto es **fail-CLOSED** (nada se evicta vía este gate), así que no destruye datos activamente — PERO la mitad protectora ("no evictar dealer vivo con TRUSTWORTHY activo") es código muerto y el gate es estructuralmente ciego a la señal que dice gatear. En cuanto la evidencia de muerte se claves bien (o entre un REFUTED por ULID), la protección sigue ciega. Un gate de seguridad que no puede leer su propia señal es un peligro de pérdida de datos latente.
- **Fix propuesto:** Corregir ambos JOINs a `vv.subject_key = e.cdp_code` para `subject_type='entity_inventory'` (o resolver el `subject_key` a ULID en escritura de forma consistente). Añadir un test conductual que ejerza el dealer con ambos veredictos.

### Dimensión E — API (2)

#### E-inventory-innerjoin-dataloss
- **Título:** `/entities/{cdp}/inventory` hace INNER JOIN a `v_canonical_vehicle`, ocultando todo coche disponible sin cluster — 1.329 dealers muestran stock CERO.
- **Ubicación:** `services/api/routers/entities.py:124-143` (JOIN en :132); mismo patrón en `entities.py:71-74` (agregado de `get_entity`).
- **Evidencia:** El query es `JOIN v_canonical_vehicle vc ON vc.vehicle_ulid = v.vehicle_ulid` (INNER). La vista solo incluye filas del último `vehicle_cluster_run` con `vam_verified=true`. Anti-join (LEFT JOIN ... IS NULL): total disponible=1.697.247 vs en-vista=1.687.420 → **9.827 ocultos**; por dealer: `dealers_fully_invisible=1329`, `total_avail_cars_hidden=9827`. Los 9.827 están AUSENTES de `vehicle_cluster` entero (cada uno es su propio canónico → debe aparecer). Ejemplo: CDP-ES-28-YSW14N9G total_avail=450, mostrado=0. Solo existe un cluster run (`vehicle-identity-det-v1`, run_at 2026-06-15 01:13) mientras el coche más nuevo first_seen=2026-06-15 16:02 → ~15h de coches invisibles, y la brecha CRECE con cada cosecha.
- **Por qué importa:** Viola directamente el contrato ("Return available CANONICAL stock for ALL cluster members" / "sacarle TODO su stock"): 1.329 dealers reales devuelven inventario vacío y 9.827 coches son inalcanzables por el endpoint primario. Peligro operativo continuo y creciente.
- **Fix propuesto:** Cambiar el INNER por `LEFT JOIN v_canonical_vehicle vc ... ` y usar `COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid)` para que el coche sin cluster aflore como su propio canónico. **Aplicar la misma corrección a AMBOS call-sites** (`:132` listado y `:71-74` agregado de cabecera). La implementación de referencia correcta ya existe en `vehicles.py:91`.

#### E-entity-available-count-undercount
- **Título:** El `available_inventory` de `/entities/{cdp}` usa el mismo INNER JOIN, reportando 0 stock para los 1.329 dealers invisibles.
- **Ubicación:** `services/api/routers/entities.py:70-76`.
- **Evidencia:** `SELECT count(DISTINCT vc.canonical_vehicle_ulid) FROM vehicle v JOIN v_canonical_vehicle vc ON vc.vehicle_ulid=v.vehicle_ulid WHERE v.entity_ulid=ANY($1) AND v.status='available'` (INNER). Para CDP-ES-28-YSW14N9G: total_avail=450 pero el conteo da 0. Escala global verificada EXACTA: 1.697.247 vs 1.687.420 → 9.827 ocultos; 1.329 dealers fully-invisible. `resolve_cluster` (deps.py:104-114) resuelve un dealer sin cluster a sí mismo, así que el conteo defectuoso corre sobre él. El patrón corregido `count(DISTINCT COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid)) ... LEFT JOIN` devuelve 450.
- **Por qué importa:** El resumen de entidad anuncia `available_inventory=0` para dealers con cientos de coches; cualquier UI/consumidor cree que el dealer está vacío. (Corrección al finding: su "why_it_matters" decía "usar el mismo fix que el listado de inventario" — pero el listado TIENE el mismo bug; la referencia correcta es `vehicles.py:91`.)
- **Fix propuesto:** `LEFT JOIN v_canonical_vehicle` + `count(DISTINCT COALESCE(vc.canonical_vehicle_ulid, v.vehicle_ulid))` en cabecera Y listado de `entities.py`.

### Dimensión F — método/ops (2)

#### F-scheduler-no-singleton-lock
- **Título:** El scheduler NO tiene cerrojo singleton de host — la cicatriz "dos gobernadores en un host" de AS24 no está estructuralmente prevenida.
- **Ubicación:** `pipeline/ops/scheduler.py:599-665` (`_start_scheduler`, sin advisory lock) ; `pipeline/engine/governor.py:20-28,311`.
- **Evidencia:** Grep `advisory_lock|pg_advisory|pidfile|flock|lockfile|singleton|fcntl|filelock` sobre `pipeline/` → 0 matches de scheduler/launcher. La garantía single-producer descansa SOLO en `max_instances=1` de APScheduler (in-proceso, evita ticks solapados dentro de UN proceso, nada entre procesos). El governor es un `_default_governor` módulo-global con buckets `asyncio.Lock` in-memory; la versión Redis GCRA cross-proceso está marcada futura/no-construida. Arrancar `python -m pipeline.ops.scheduler` dos veces → dos governors independientes → la tasa agregada al host se duplica, recreando el 4x-hammer que perdió 138 dealers AS24 (`docs/architecture/06-RESILIENCE-OPS.md:37-49`, verificado verbatim). Sin docker-compose `replicas:1` / systemd que sustituya el guard a nivel infra.
- **Por qué importa:** La cicatriz que toda esta capa de resiliencia existe para hacer "estructuralmente imposible" solo se previene si un operador nunca arranca un segundo proceso. El invariante "nunca dos governors en un host" es convención humana, no mecanismo. Como `apscheduler_jobs` no existe (ver `F-scheduler-never-deployed`), el primer deploy real ES el momento de riesgo.
- **Fix propuesto:** Una línea: `pg_try_advisory_lock(<const>)` al inicio de `_start_scheduler`, fail-fast si no se adquiere. Debe aterrizar antes/con el primer deploy productivo.

#### F-autocasion-orphaned-no-schedule-path
- **Título:** Autocasion (Tier-1) tiene CERO ruta de scheduling: la key de `source_health` y la del REGISTRY quedaron desincronizadas por el swap a facet.
- **Ubicación:** `pipeline/ops/scheduler.py:126-127` (REGISTRY=`autocasion_facet`) vs fila viva de `source_health` `autocasion_wholesale`.
- **Evidencia:** `source_health` solo contiene `autocasion_wholesale` (is_tier1=t, 24h, last_ok hoy). El REGISTRY mapea SOLO `autocasion_facet`. `_due_sources()` lee solo `source_health` → devuelve `autocasion_wholesale` cuando vence, pero `heartbeat_tick` lo SALTA (`if source_key not in REGISTRY: ... continue`, :399-404); `autocasion_facet` NUNCA puede seleccionarse (no está en source_health). Los tests propios del repo `test_scheduler_due.py::test_all_tier1_mapped` y `::test_registry_covers_live_source_health` AHORA FALLAN con `Unmapped source_keys: ['autocasion_wholesale']`. `silence_watchdog.py:128/194` pone severity=critical (is_tier1) y solo UPSERTea una alerta — cero acción de cosecha → **alerta-y-nunca-recupera**.
- **Por qué importa:** Una plataforma Tier-1 (la superficie de mayor valor) está estructuralmente garantizada a quedar en silencio y NO ser re-cosechada por el scheduler, mientras el watchdog dispara CRITICAL para siempre sin posible auto-cura — viola el mandato "si uno falla ... se auto-repara".
- **Fix propuesto:** **Corrección al fix del finding** (su sugerencia de "añadir fila `autocasion_facet`" es ERRÓNEA: `autocasion_facet.py:88-90` importa `AC_SOURCE_KEY` de wholesale = `'autocasion_wholesale'` y escribe salud bajo esa key, así que una fila `autocasion_facet` quedaría permanentemente muda). Fix mínimo que pasa ambos tests: renombrar la key del REGISTRY de vuelta a `'autocasion_wholesale'` apuntando al módulo `pipeline.platform.autocasion_facet` (cambio de una línea). Alternativa: cambiar `AC_SOURCE_KEY` a `'autocasion_facet'` Y migrar las filas `source_health`/`harvest_run`/`source_breaker`.

---

## ALTOS (10)

### Dimensión A — datos (3)

#### A-junk-sentinel-prices
- **Título:** Precios centinela/basura pasan la validación (999999999, 123456789, 111111111, …) en coches disponibles.
- **Ubicación:** tabla `vehicle` (`price numeric(12,2)`); no existe CHECK de cota superior/centinela.
- **Evidencia:** Top disponible por precio: 999.999.999€ "Peugeot 206 2003", 699.251.419 "Seat 850", 123456789 ×2, 111111111 ×4. Placeholders de dígito-repetido: 99999=53, 11111=22, 12345=5, 111111111=5, 123456=3, 123456789=2, 999999999=1. Disponible >1M€ = 201 filas (drift de 182, crecimiento por ingesta diaria); >2M = 109. `numeric(12,2)` acepta hasta 9.999.999.999,99 sin CHECK ni cota en ingesta; el `price_trap` del gestionador es de un solo lado (solo bajo).
- **Por qué importa:** Valores tecleados por usuario, no lujo legítimo. Corrompen cualquier agregado/percentil/ranking de precio y se filtran al producto servido. Un Peugeot 206 a mil millones de euros es un fallo de parseo/validación obvio que debería cuarentenarse o rechazarse en ingesta.
- **Fix propuesto:** Rechazar/cuarentenar en el borde de ingesta el precio implausiblemente alto (cap segment-aware, p.ej. > tope por segmento) + CHECK opcional de cota superior; añadir rama de lado-alto al detector `price_trap` existente.

#### A-make-model-null-parse
- **Título:** 400.685 coches (23,5%) tienen make Y model NULL pese a títulos parseables.
- **Ubicación:** tabla `vehicle` (make,model NULL juntos).
- **Evidencia:** `count(*) FILTER (WHERE make IS NULL AND model IS NULL)`=400.685 (make_null_only=1.829, model_null_only=7.232). De 400.657 both-null CON título, 345.759 (86%) empiezan por token de marca reconocido; 148.708 siguen patrón limpio "Marca - Modelo"; solo 139 son ruido no-vehículo. Concentrado en compraventa (271.598 both-null) y particular (128.306) — clasificados, no el feed estructurado AS24 (1.295.222 filas SÍ tienen make+model). Causa-raíz en código: `pipeline/platform/milanuncios_wholesale.py:391-392` fija explícitamente `make=None, model=None` con comentario "milanuncios ads carry make only inside categories/title"; contrasta con `wallapop_wholesale.py:348-349` que extrae `make=ta.get('brand')`. No hay fallback de parseo de título (`ingest.py:81-85` guarda verbatim).
- **Por qué importa:** make/model son los ejes primarios de búsqueda/filtro; casi un cuarto del inventario es no-filtrable pese a una marca recuperable en el título. (Corrección: NO es señal de `recipe_version=NULL` — esa columna es NULL en 1.619.986 filas incl. ~894K que SÍ tienen make/model; el mecanismo real son los conectores de clasificados que saltan la extracción estructurada.)
- **Fix propuesto:** Backfill por parseo de título para títulos marca-líderes (~86% recuperable). Caveat: ~14% (~55K) son genuinamente difíciles (ruido, marcas inusuales, títulos no marca-líderes) y no los recupera un parseo simple.

#### A-cross-entity-dup-listings
- **Título:** 140.159 URLs de listado idénticas (deep_link) existen como filas vehicle separadas bajo entidades DISTINTAS — inventario duplicado por el split de resolución de entidad.
- **Ubicación:** tabla `vehicle`; constraint `vehicle_entity_ulid_deep_link_key` es per-(entity,deep_link), NO bloquea la misma URL bajo distintas entidades; vistas `v_canonical_vehicle`/`v_canonical`.
- **Evidencia:** 140.159 grupos dup, 140.302 filas extra, 280.461 filas en grupos dup, `groups_multi_entity=140159`, `groups_same_entity=0` (TODOS multi-entidad). total vehicle=1.704.968, distinct deep_link=1.564.666 → 140.302 fantasma. Anti-join cobertura: 278.219 en algún cluster, **2.242 en NINGÚN cluster**, 126.902 mapeados a canónico no-self. Ejemplos: milanuncios ...589714238.htm =3×/3 entidades, wallapop ...1271601828 =3×/3.
- **Por qué importa:** El mismo listado físico se cuenta como 2-3 vehículos porque su dealer se resolvió a múltiples `entity_ulid`. *Corrección al why_it_matters:* las métricas servidas SÍ deduplican vía `v_canonical_vehicle` (`ops.py:82-90` vehicles_unique_available=1.484.462; docstring `ops.py:59-60` documenta la exclusión de alias cross-entity) → la inflación de conteo-titular está sobreestimada. PERO la tabla `vehicle` cruda está físicamente inflada ~140K filas (cualquier consumidor que lea `vehicle` directo sobre-cuenta), los 2.242 sin cluster están fuera del colapso canónico, y la dedup está VAM-run-gated (revertiría a crudo si no hubiera run verificado).
- **Fix propuesto:** Constraint/evicción de dedup-verdadera a nivel `vehicle` (o un canónico a nivel deep_link); la vista de cluster mitiga rutas servidas pero no la tabla cruda ni el residuo sin clusterizar.

### Dimensión B — identidad (2)

#### B-particular-province-split
- **Título:** La provincia horneada en el prefijo del cdp_code parte un mismo vendedor humano en N identidades (703 aún partidos en la vista servida).
- **Ubicación:** `services/api/codes.py:45-48,73-82` ; tablas `entity`, `canonical_dedup`, vista `v_dealer_resolved`. Caller: `pipeline/platform/wallapop_wholesale.py:541-543` (y milanuncios:633-634, coches_net:457-458).
- **Evidencia:** `canonical_key` (45-48) devuelve `particular:{plat}:{sid}` SIN provincia; `cdp_code` (82) devuelve `CDP-ES-{province_code}-{_base32(digest)}` — provincia en el prefijo, hash sufijo sin provincia. Un humano en 2 provincias → 2 cdp_codes con el mismo sufijo 8-char. Split por kind: particular=843 grupos/1689 filas, compraventa=22, garaje=14, concesionario_oficial=5. Tras el resolver `v_dealer_resolved`: fully_remerged=139, partially=1, **still_fully_split=703**. Los merges cross-provincia en `canonical_dedup` son 100% deep-link-evidence-backed (0 sin evidencia). Ejemplo: CDP-ES-18-WKQT02KH 'Er ..' prov18 ↔ CDP-ES-08-WKQT02KH 'Er ..' prov08, evidencia wallapop. 1689 filas colapsan a solo 1549 identidades servidas distintas.
- **Por qué importa:** La promesa del producto es "código único por dealer". Para 703+ vendedores privados el mismo humano se expone como 2+ dealers canónicos en la API, fragmentando su inventario e inflando el conteo C2C. La provincia es atributo per-listing inyectado en una key de identidad cuyo `canonical_key` correctamente la excluye.
- **Fix propuesto:** El defecto es la provincia en el PREFIJO, no el sufijo hash (que ya la excluye) — NO alterar el input del hash. Ampliar el resolver servido sobre los 703 restantes usando la señal deep-link (que ya prueba la mismidad y captura 139/843).

#### B-beta-resolver-dormant
- **Título:** El resolver de fingerprint VAM-verificado (`entity-resolution-fingerprint-v1`, 38.555 dealers) no está cableado en la ruta de identidad servida.
- **Ubicación:** `services/api/deps.py:73-111` ; vistas `v_resolved_dealer` vs `v_dealer_resolved` ; tabla `entity_resolution`.
- **Evidencia:** `entity_resolution_run` `vam_verified=t`, `n_resolved_dealers=38555`, `n_merged=20951`. Solo alimenta `v_resolved_dealer` (única vista que referencia `entity_resolution`), que tiene CERO consumidores de código. `resolve_cluster()` usa `v_dealer_resolved` exclusivamente (construida de B1 `dealer-identity-det-v1` ∘ `canonical_dedup`, nunca une `entity_resolution`). Gap cuantificado: 388 pares colapsados por β pero separados en la vista servida. *Caveat:* el framing "40.016 / 38.555" está mal etiquetado — `v_dealer_resolved` abarca los 370.267 `resolved_cdp_code` (incluye particulares); la cifra dealer-only comparable es 38.391 (B1-dedup) vs 38.554 (β). Orden de migración: β=0025, `v_dealer_resolved`=0028 construida sobre linaje no-β → la vista servida ignoró deliberadamente la salida β.
- **Por qué importa:** Dos capas paralelas de identidad de dealer discrepan y la señal más fuerte (inventory-fingerprint, VAM-sellada) se computa, almacena y expone pero la sortean TODOS los endpoints de entidad. 388 unificaciones cross-canal que el negocio pagó por computar son invisibles. O `v_resolved_dealer` está muerta o `v_dealer_resolved` carece de la composición β — la identidad autoritativa es ambigua.
- **Fix propuesto:** Decidir la autoridad y componer β en la ruta servida: o reconstruir `v_dealer_resolved` para incluir `entity_resolution` (B1 ∘ dedup ∘ β), o repuntar `resolve_cluster()` a una vista que sí la una. Retirar la vista muerta.

### Dimensión C — conectores (2)

#### C-cochesnet-recipe-collision-capped-clobbers-facet
- **Título:** La receta canónica de coches.net (`_tier1/CDP-ES-00-TKRV45RP/recipe.yaml`) guarda la estrategia wholesale ACOTADA (`sortBy=relevance`), habiendo clobbered la receta facet completa — varios módulos `write_recipe()` al mismo cdp_code (last-writer-wins).
- **Ubicación:** `countries/ES/_tier1/CDP-ES-00-TKRV45RP/recipe.yaml` ; `pipeline/platform/coches_net_wholesale.py:313,1013` ; `coches_net_facet.py:409` ; `coches_net_segments.py:441` ; `autocasion_wholesale.py:887` (fix de referencia).
- **Evidencia:** El recipe.yaml tiene `scope: platform-wholesale` + `sortBy=relevance` (el comentario `coches_net_wholesale.py:313-314` prueba: "NO sortBy: 'relevance' silently caps the gateway result set at ~155k"), `segments:`=0, `platform-facet`=0. `recipe.py:54-62`: `write_recipe` escribe `countries/ES/recipes/<cdp_code>.yaml` last-writer-wins. **Colisión a TRES bandas**: wholesale:1013, facet:409, segments:441 — los tres resuelven al MISMO platform_code. `git log` del archivo: último toque `e6a7020` "test(harvest)... 2 engines proven" (una corrida wholesale). Contraste: `autocasion_wholesale.py:887` = `recipe_path = "(not written — autocasion_facet owns the canonical recipe)"` (FIXED); `wallapop_wholesale.py:1335` aún hace `write_recipe` (no propagado).
- **Por qué importa:** La receta es el activo que deja a Cardeep re-scrapear sin crudo. La receta canónica committeada enseña la estrategia relevance-capped ~155k, no la partición por provincia ~272k → cualquiera que la siga sub-cosecha ~40%.
- **Fix propuesto:** Replicar el fix autocasion — que `coches_net_wholesale`, `coches_net_segments` y `wallapop_wholesale` NO escriban la receta de plataforma; que el módulo facet la posea. **Además:** hay una DERIVA DE RUTA — `write_recipe` escribe a `countries/ES/recipes/<cdp>.yaml` pero el activo committeado vive en `_tier1/CDP-ES-00-TKRV45RP/recipe.yaml` (movido por el git-mv del reshape SU-E2, commit `dfb6c5b`). Reconciliar la ruta de escritura con la ubicación canónica reshapeada o el `_tier1` queda rancio sin importar qué módulo corra.

#### C-wallapop-recipe-stale-wrong-axis
- **Título:** La receta canónica de wallapop (`_tier1/CDP-ES-00-EMRH0TWQ`) describe una estrategia geo-centroide+keyword con "lat/long HONORED" que el conector facet prueba EXPLÍCITAMENTE como FALSA (geo ignorado en silencio; el eje real es seller_type×precio).
- **Ubicación:** `countries/ES/_tier1/CDP-ES-00-EMRH0TWQ/recipe.yaml` ; `pipeline/platform/wallapop_facet.py:20-23,452-465` ; `pipeline/recipe.py:54-62`.
- **Evidencia:** El recipe.yaml (verificado vía `git show HEAD:`): línea 17 "keyword sweep (~40 car brands) x ES geo-centroid grid (lat/long HONORED)", línea 14 `order_by=most_relevance`. El docstring live-verificado `wallapop_facet.py:20-23`: "Geo lat/long is NOT a real partition axis here: every centroid returns the SAME national pool ... distance/radius/max_distance are silently ignored — verified ... seller_type does shard." Contradicción directa. mtime 2026-06-14 06:46, más viejo que 12 de 14 recetas `_tier1` (artefacto pre-facet). No existe receta facet-shaped committeada en el árbol.
- **Por qué importa:** La receta guardada afirma un eje de partición (grid geo) que no shardea la API → seguirla re-deriva el pool flat tope-profundidad; "lat/long HONORED" contradice el hallazgo verificado del conector. Una receta que miente. *Nota de alcance:* la receta `_tier1/*/recipe.yaml` NO la lee ningún harvester en runtime (es activo de documentación/reusabilidad) → engaña a humanos/agentes que re-derivan, no mis-conduce un scrape vivo; severidad-como-integridad-del-conocimiento se sostiene, severidad-como-rotura-de-scrape no.
- **Fix propuesto:** **Corrección al fix del finding** (su "que facet escriba la receta canónica" YA está hecho: `wallapop_facet.py:452-465` sobrescribe la enumeración a "geo NOT a partition axis" + `facet_axes{seller_type,price,count_oracle}` y llama `write_recipe`). La causa-raíz real es DIVERGENCIA DE RUTA: ambos conectores escriben vía `write_recipe → recipes/<cdp>.yaml`, pero `dfb6c5b` git-mv'd las canónicas a `_tier1/<cdp>/recipe.yaml` SIN repuntar `write_recipe` → ninguno toca el archivo `_tier1`, congelado en su contenido pre-facet. Fix correcto: repuntar `write_recipe` (o añadir rama Tier-1) para emitir a `_tier1/<cdp>/recipe.yaml` y que la próxima corrida facet sobrescriba el artefacto geo-grid rancio.

### Dimensión D — verificación (2)

#### D-supersession-unwired
- **Título:** `superseded_by` nunca se escribe por ningún camino — la semántica "último veredicto activo" es no-fiable y los veredictos se acumulan sin cota por sujeto.
- **Ubicación:** `verification_verdict.superseded_by` ; `pipeline/ops/inquisition_schedule.py:48-68` ; `pipeline/evict.py:93,107` ; `migrations/0026_verification_deep.sql:139-141,177-178`.
- **Evidencia:** Las 4 referencias en `pipeline/` son filtros READ-side `superseded_by IS NULL`; cero INSERT/UPDATE lo escriben. Vivo: 1085 total / 1 poblado (la única es la corrección manual documentada 1112→1121). Acumulación: 199 sujetos con ≥2 veredictos `superseded_by IS NULL`; peor sujeto CDP-ES-00-TKRV45RP con 20 TRUSTWORTHY simultáneamente "activos". Patología viva: CDP-ES-00-XM91J1NZ tiene REFUTED y TRUSTWORTHY ambos activos sobre 2d19h, 9 eternos (`expires_at IS NULL`) + 1 TTL. `idx_verdict_latest` existe y `superseded_by` es self-FK, ambos sin poblar. Declarado como deuda (`docs/architecture/10-VERIFICATION-STACK.md:181-182`, `PROGRESO.md:554`) pero deferral-documentado no es mitigación.
- **Por qué importa:** Ambos consumidores que dependen de identificar el único veredicto más nuevo (gate de evicción; scheduler de Inquisición "excluir ya-superseded") ven cada veredicto histórico como activo. Un TRUSTWORTHY rancio de hace una semana y un REFUTED fresco coexisten como igualmente "activos". Los eternos (NULL `expires_at`) son inmunes al filtro TTL que de otro modo los ocultaría, volviendo el problema permanente en vez de auto-limpiable.
- **Fix propuesto:** Cablear la escritura de `superseded_by` en el cierre de re-verificación (paso post-RESOLVED): al emitir un veredicto nuevo para `(subject_type,subject_key,claim)`, UPDATE los previos activos `SET superseded_by=<nuevo_id>`. Backfill one-shot de los 199 sujetos con múltiples activos para dejar solo el más nuevo.

#### D-audit-chain-grandfather-gap
- **Título:** La cadena-hash de auditoría tamper-evident cubre solo 46 veredictos post-0026; los 1039 (incl. los 989 grandfathered TRUSTWORTHY) tienen cobertura CERO.
- **Ubicación:** `verdict_audit` (vivo) ; `migrations/0026_verification_deep.sql:220,236-239` (trigger AFTER INSERT, sin backfill).
- **Evidencia:** Anti-join (LEFT JOIN ... IS NULL): 1.039 sin auditar de 1085; 46 filas de audit. Split de los 1039: 989 TRUSTWORTHY + 50 REFUTED. Frontera limpia: rango auditado verdict_id 1111-1410, sin-auditar 1-1102; genesis es verdict_id 1111. La cadena interna es sólida (genesis prev_hash NULL, 0 broken_links, 0 bad_chain_hash) — el defecto es el ALCANCE. `trg_verdict_audit_append` es AFTER INSERT (forward-only) y 0026 no hizo backfill (grep de las 28 migraciones confirma cero inserts a verdict_audit fuera del trigger). Cobertura 46/1085 = 4,24%.
- **Por qué importa:** La propuesta de valor del ledger profundo es una cadena tamper-evident de CADA veredicto. La cadena protege el 4,2% y ninguno de los 989 TRUSTWORTHY que respaldan el producto → los sellos heredados podrían alterarse en silencio sin romper la cadena.
- **Fix propuesto:** Backfill one-shot que recorra los veredictos existentes en orden de id y anexe filas de audit hash-encadenadas (re-derivando `prev_hash` secuencialmente) antes del genesis actual, o reconstruir la cadena para incluirlos.

### Dimensión F — método/ops (1)

#### F-scheduler-never-deployed
- **Título:** El scheduler durable nunca ha corrido contra la DB viva — las garantías crash-safe/single-producer son solo-código, no probadas en producción.
- **Ubicación:** DB viva (`apscheduler_jobs` ausente) vs `pipeline/ops/scheduler.py:599-665` ; `pipeline/ops/health.py:76-126` ; `harvest_run` (245 filas, 36 en 24h).
- **Evidencia:** `to_regclass('public.apscheduler_jobs')` y `to_regclass('apscheduler_jobs')` ambos NULL → tabla ausente en todo schema; el `SQLAlchemyJobStore` (601-606) la crea en `scheduler.start()`, así que start() nunca corrió contra cardeep-pg. Sin embargo la cosecha está viva: `harvest_run`=245 total/36 en 24h/más reciente 2026-06-15 16:02. Esas filas las escribe `record_run` (`health.py:76-126`, "THE single writer") cuyo INSERT deja `started_at`=`finished_at`=now() → las 245/245 son instantáneas (0 duración), incompatible con el modelo launch-subprocess-and-time del scheduler ("una fuente 24h puede tardar ~2h"). Sin proceso scheduler corriendo (Win32_Process). `scheduler.py` committeado y limpio (`3a71ad8` B2.2, `9d953f3` SU-F1). La tabla jobstore NO la crea ninguna migración (APScheduler la crea en runtime), su ausencia es señal pura de never-started.
- **Por qué importa:** Cada garantía B2 (resume durable tras crash, serialización single-producer, due-selection breaker-aware, watchdog horario de silencio, cadencia 6h Inquisición) está sin probar en vivo. Las cosechas que aterrizan filas HOY sortean el scheduler vía invocación directa/manual, así que las protecciones breaker-skip y serialización NO están en la ruta productiva real. El primer arranque real es también la primera exposición del gap sin-cerrojo (`F-scheduler-no-singleton-lock`).
- **Fix propuesto:** Desplegar el scheduler como el productor único real (servicio supervisado), con el cerrojo advisory de `F-scheduler-no-singleton-lock` en su sitio, y retirar las invocaciones directas/manuales de cosecha de la ruta productiva. HIGH (no CRÍTICO) porque no hay corrupción ocurriendo — es una superficie de control inactiva/no-verificada.

---

## MEDIOS (11)

### Dimensión A — datos (3)

#### A-sourceless-entities
- **Título:** 10.899 entidades (10.645 compraventa, 250 desguace, 4 subasta) sin fila `entity_source`; 4 de ellas sirven 828 coches disponibles.
- **Ubicación:** tabla `entity` vs `entity_source` ; trigger `trg_entity_attest`. Causa-raíz: `scripts/overture_ingest.py` `_INSERT_SQL:384-407`.
- **Evidencia:** Anti-join LEFT JOIN: compraventa=10.645, desguace=250, subasta=4 (total 10.899). 4 entidades sourceless con 828 disponibles (las 4 `first_discovered_source='overture'`, `source_group='directory'`, unverified). `attest_count` de las 10.899 = exactamente 1 (el default) → unbacked, porque `trg_entity_attest` solo recomputa en INSERT a `entity_source`. `overture_ingest.py` escribe la entidad pero NUNCA inserta en `entity_source`, mientras `pipeline/ingest.py:64` siempre lo hace. De 10.913 entidades overture solo 14 (0,13%) tienen fila `entity_source`; no hay key 'overture' en `entity_source`. Todas creadas 2026-06-14.
- **Por qué importa:** Una entidad sin `entity_source` no se atribuye a fuente de descubrimiento/cosecha, pero `attest_count` ≥1 por defecto → la atestación no está respaldada por evidencia. *Corrección:* NO son "inauditables de procedencia" — 100% llevan `first_discovered_source='overture'` + `source_group='directory'` en la fila entity, el origen SÍ se rastrea; lo que falta es el ledger de atestación per-source + el `source_ref`/`source_dealer_id` de cosecha.
- **Fix propuesto:** Hacer que `overture_ingest.py` inserte la fila `entity_source` (key `'overture'`) que `ingest.py:64` ya escribe, y backfill de las 10.899 existentes para respaldar `attest_count`.

#### A-gone-listed-desync
- **Título:** 5 coches con `vehicle.status='gone'` cuyo `platform_listing` sigue `status='listed'` con `removed_at` NULL.
- **Ubicación:** `vehicle.status` vs `platform_listing.status`+`removed_at`. Productor: `pipeline/delta.py:84-89` (`_MARK_GONE`), `pipeline/ingest.py:123`, `pipeline/platform/generic_dealer_site.py:730`.
- **Evidencia:** Agregado: (gone,listed)=5, todos `removed_at=NULL`, mismos 5 ULIDs (01KTY76VHV..., 01KTY771P1..., etc.), last_seen=2026-06-12, mismo `platform_entity_ulid`. De 1.608.167 listed: 5 gone_but_listed / 0 sold_but_listed. Ninguno de los 3 caminos GONE escribe `platform_listing.status/removed_at`; no hay trigger DB (pg_trigger: 0). El FK `ON DELETE CASCADE` solo cubre el borrado duro de evict (que DELETEa, no pone gone), no la transición soft 'gone'. *Corrección:* el productor es el barrido GONE de delta/ingest, NO "eviction" (evict borra con cascade).
- **Por qué importa:** La evicción soft puso `vehicle.status='gone'` pero no propagó a `platform_listing` → una ruta de servicio keyed por plataforma aún los mostraría como listings vivos. Pequeño en volumen pero rotura real de coherencia de estado en la propagación.
- **Fix propuesto:** En los caminos de transición gone, también `UPDATE platform_listing SET status='removed', removed_at=now() WHERE vehicle_ulid=$1 AND status='listed'` (o un trigger AFTER UPDATE en vehicle), + backfill one-shot de las 5 filas.

#### A-zero-and-tiny-prices
- **Título:** 2.678 coches disponibles a precio 0 y 11.741 bajo 100€.
- **Ubicación:** `vehicle.price` (filas disponibles) ; `pipeline/gestionador/detect.py:745` (`detect_price_trap`, dormido).
- **Evidencia:** price_zero=2.678, price_lt_100=11.741, price_null disponible=9.416. Clusters: 50€=1.457, 1€=1.044, 10€=954, 20€=942, 30€=933. La vista servida `servable_vehicle` NO aplica filtro de precio (solo excluye cuarentena abierta) → `SELECT FROM servable_vehicle WHERE status='available'` devuelve los MISMOS 2.678/11.741/9.416: los precios malos fluyen al producto sin filtrar. El detector `detect_price_trap` (banda [49,999] como tarifas mensuales) ha producido CERO output: `gestion_item` vacío, verdicts price_trap=0 → mitigación dormida. Proporción: tiny+zero=0,85%, +NULL=1,40% de 1.697.247.
- **Por qué importa:** Precios 0/1/10/50€ son placeholder o depósito/reserva/cuota-financiación, no precio de venta real; con los 11.299 NULL, ~14K disponibles tienen señal de precio inutilizable, sesgando rankings "más barato" y analítica de distribución hacia falsos suelos.
- **Fix propuesto:** Activar/correr el `detect_price_trap` (y persistir `gestion_item`) con rama de lado-bajo que cuarentene placeholders/depósitos; o filtrar precio implausible en `servable_vehicle`.

### Dimensión B — identidad (1)

#### B-crosssource-dedup-ungated
- **Título:** La dedup cross-source OSM×digital (`cross-source-dedup-v1`) computada pero `vam_verified=FALSE` — merges cross-source genuinos quedan partidos.
- **Ubicación:** `entity_cluster_run` ; `pipeline/identity/cross_source_dedup.py:812` (FALSE en la escritura) ; vistas `v_canonical`/`v_dealer_resolved`.
- **Evidencia:** `cross-source-dedup-v1` `vam_verified=f` (n_merged=688); solo `dealer-identity-det-v1` es `vam_verified=t`. `v_canonical` filtra `WHERE vam_verified=true` → resuelve solo B1 (61.551 filas todas `dealer-identity-det-v1`). De los 688 merges, 13 son genuinos (anti-join vs B1); los 13 resuelven a `resolved_cdp_code` distintos en `v_dealer_resolved` (siguen partidos). Solo 526 entidades multi-source (11 con 3 fuentes, 515 con 2). Ejemplo: SEALCO MOTOR SA en autocasion/acevas vs Sealco Motor Volkswagen en osm, mismo muni 28007. *Correcciones:* el FALSE está en :812 (no :54); `v_dealer_resolved` no tiene columna 'unified' (se deriva comparando `resolved_cdp_code`).
- **Por qué importa:** El escenario exacto del brief (un dealer en coches.net + autocasion + su sitio colapsando a un canónico) NO se logra para los casos de señal ortogonal: 13 pares verificados quedan dos canónicos en la API. Pipeline correcto e idempotente pero aparcado esperando un gate VAM del Director; la completitud está bloqueada por el gate, no por código.
- **Fix propuesto:** Decisión del Director: VAM-verificar `cross-source-dedup-v1` (poner `vam_verified=true`) tras revisar los 13 (o N) merges, para que `v_canonical` los incluya. Es gate-blocked, no code-blocked.

### Dimensión C — conectores (3)

#### C-autocasion-scheduler-missing-segment-all
- **Título:** `autocasion_facet` programado con `["--makes","all"]` pero NO `--segment all` → solo el segmento vo (used) se refresca; vn (~5.946) y km0 (~5.994) nunca los cosecha el latido.
- **Ubicación:** `pipeline/ops/scheduler.py:126-127` ; `pipeline/platform/autocasion_facet.py:221-222`.
- **Evidencia:** `resolve_segments`: "if not selector or selector.lower()=='vo': return [SEG_VO], []" → omitir `--segment` = solo vo. DB viva (columna `platform_listing.segment` para CDP-ES-00-QY06GW0B): UNA fila used=111.905, cero new/km0. El CHECK `platform_listing_segment_chk` PERMITE new/km0/renting → la ausencia no es límite de schema, vn/km0 simplemente nunca se cosecharon. last_seen hoy → la cadencia corre pero refresca solo vo. La receta committeada `_tier1/CDP-ES-00-QY06GW0B/recipe.yaml` línea 5: `scope: platform-facet, segments=['vo']`. *Caveat:* los conteos vn/km0 son cifras site-declared del docstring, no re-medidas en vivo; el defecto estructural se confirma independiente de los tamaños.
- **Por qué importa:** El fix wholesale→facet corrigió el MÓDULO pero el scheduler omite `--segment all`, dejando ~11.940 coches new/km0 (~9% de autocasion) fuera de cadencia y fuera de la receta persistida.
- **Fix propuesto:** `extra_args = ["--segment","all","--makes","all"]` (invocación canónica documentada en el propio docstring :59-60).

#### C-as24-unscheduled-proof-only
- **Título:** `autoscout24_wholesale` (AS24, ~278k declarado) es un slice de prueba ~240-coches y NO está en el REGISTRY; su key `as24_wholesale` no tiene fila `source_health`, así que AS24 nunca cosecha en cadencia.
- **Ubicación:** `pipeline/platform/autoscout24_wholesale.py:15-18,61,69,342-343` ; `pipeline/ops/scheduler.py:256-258`.
- **Evidencia:** `source_health` para `%as24%`/`%autoscout%`/`as24` → 0 filas (de 47 total). `platform_listing` de AutoScout24 (CDP-ES-00-VMCZWW5N) = 268 edges, todos en ventana de 4,5 min el 2026-06-12 (corrida de prueba única, 68 dealers). `scheduler.py:256-258` reconoce "as24_wholesale ... NOT in source_health ... handled outside the scheduler". Grep `as24|autoscout` en scheduler → ausente del REGISTRY. **Corrección al finding (catch adversarial):** el sub-claim "no existe módulo cosechador completo / nunca se construyó" es FALSO — existe un cosechador per-dealer committeado en `pipeline/sources/autoscout24.py:278` (`harvest_dealer`) + `:247` (`collect_dealer_slugs`), conducido por `scripts/scale_as24.py` y `scripts/as24_harvest_batch.py` (commits f0ffb26, 69e6413), y HA CORRIDO (`first_discovered_source`: as24=511, as24_wholesale=54 = 565 dealers, muy por encima del slice 68/268); `data/as24_dealers.json` tiene 334.
- **Por qué importa:** AS24 es top-5 español sentado en 268 coches cageados con cero cosechador programado y cero auto-reparación — brecha de cobertura real y no mitigada en cadencia.
- **Fix propuesto:** **Corrección al fix del finding** (su "construir/portar un AS24 facet" está mal dirigido: el cosechador YA existe). REGISTRAR `as24` en `source_health` + REGISTRY del scheduler para que el dren per-dealer existente corra en cadencia con auto-reparación, y decidir si el caging de edges de plataforma (268) debe conducirse del mismo harvest per-dealer en vez del slice 12-páginas.

#### C-cochesnet-segments-unscheduled-no-cadence
- **Título:** Los segmentos new/km0/renting de coches.net (`coches_net_segments`, ~10.558) tienen conector funcional pero ninguna invocación programada y comparten `COCHES_SOURCE_KEY`, así que nunca refrescan ni pueden tener su propia cadencia sin colisionar.
- **Ubicación:** `pipeline/platform/coches_net_segments.py:53,445` ; `pipeline/ops/scheduler.py:120-249` (REGISTRY).
- **Evidencia:** `coches_net_segments.py:53` importa `COCHES_SOURCE_KEY` (=`'coches_net_wholesale'`, wholesale:78) y `:445` lo usa para `record_run` → escribe la key COMPARTIDA. Ausente del REGISTRY (grep). DB: `source_health` 'coches_net_segments' = 0 filas (solo existe `coches_net_wholesale`); el wholesale programado POSTea solo el body flat used-catalog (sin `offerTypeIds`) → el dren de segmentos NO está plegado. Counts vivos `platform_listing`: new=8.380, km0=3.107, renting=1.212 (~12,7k acumulados; el docstring 2026-06-13 capturó 6.151+3.105+1.302=10.558). *Imprecisión menor del finding:* el latido mapea la key al módulo wholesale (el dren used), un módulo distinto de segments; la sustancia (la colisión bloquea cadencia independiente) es correcta.
- **Por qué importa:** ~10,5k listings dealer-owned new/km0/renting de coches.net son cosechables y segment-stamped pero nunca refrescan; la key compartida bloquea darles agenda independiente → estructuralmente huérfanos.
- **Fix propuesto:** Asignar a `coches_net_segments` su propia `source_key` (p.ej. `coches_net_segments`) + fila `source_health`, o plegar el dren de segmentos (`offerTypeIds`) en la corrida coches.net facet programada.

### Dimensión D — verificación (1)

#### D-inquisition-never-ran
- **Título:** El motor Inquisición (0032) ha producido cero veredictos en la DB viva — sus invariantes son sólidos pero totalmente sin ejercer en producción.
- **Ubicación:** `inquisition_verdict` (vivo, vacío) ; `pipeline/inquisition/quorum.py:136-297` ; `pipeline/inquisition/independence.py:12-69` ; `pipeline/inquisition/prosecutor.py:21-29,46-49,418-421`.
- **Evidencia:** `pg_stat_user_tables`: `inquisition_verdict` n_tup_ins=71, n_tup_del=0, n_live_tup=0, n_dead_tup=9 — firma de transacciones rolled-back (inserts contados, nunca commiteados). Mismo patrón en inquisition_claim/skeptic/gestion_item/gestion_transition (ins>0, del=0, live=0) → el único ejercitador fue el test suite (patrón _Rollback/SAVEPOINT). CHECK `trustworthy_needs_independence` `convalidated='t'` (VALID, fuerte). `prosecute_pending/prosecute_claim` aparecen SOLO en `prosecutor.py` (sin caller vivo); `scheduler.py:439-461` corre solo `schedule_reverification`, nunca el prosecutor; `emit_claim_from_verdict` explícitamente "NOT auto-run". VAM-reliance: 1.044/1.085 (96,2%) con `expires_at IS NULL`, solo 38 con `quorum_n>=2`.
- **Por qué importa:** La capa de verificación más profunda (independencia escéptica, guard de falso-veto, lógica hard-refute) está construida y correcta sobre papel pero nunca ha adjudicado un claim vivo. La verificación real del producto descansa en la capa VAM count-quorum más débil — y para el 96,6% de los claims, en las filas grandfathered que sortean incluso esa. "Verificado a estándar Inquisición" es aspiracional hoy.
- **Fix propuesto:** Cablear un camino vivo que emita `inquisition_claim` (integración delta SU-A4) y que el scheduler llame `prosecute_pending` en cadencia. Es decisión de harvest-wiring, explícitamente diferida en el docstring del prosecutor; MEDIO porque no es riesgo de corrupción.

### Dimensión E — API (2)

#### E-geo-tree-province-only-kind-status-leak
- **Título:** `/geo/{province}/tree` `entities_province_only_no_municipality` cuenta TODOS los kinds incl. particular y todos los status, contradiciendo el contrato `kind<>particular` usado en el resto de la misma respuesta.
- **Ubicación:** `services/api/routers/geo.py:260-262`.
- **Evidencia:** El query es `SELECT count(*) FROM entity WHERE province_code=$1 AND municipality_code IS NULL` — sin filtro kind ni status. El resto del árbol (`geo.py:242`) filtra `e.kind <> 'particular'` y el endpoint hermano `/geo/{province}/entities` (`:129-130`) fuerza `status='active' AND kind <> 'particular'`. Madrid: all_kinds=4.563 vs nonpart=940 (delta 3.623 = 100% particulares) vs nonpart_active=932 (8 unverified dentro de los 940: 5 compraventa + 3 concesionario_oficial). Inflación 4.563/940 = 4,85×. *Caveats:* el delta +3.623 es 100% particulares (los unverified viven DENTRO del bucket no-particular); el "module docstring" no dice literalmente "active non-particular" — el contrato lo establecen docstrings de endpoint + el filtro del cuerpo.
- **Por qué importa:** El árbol geo es la vista de cobertura/estructura; uno de sus números resumen incluye en silencio particulares C2C (3.623) y filas unverified (8) que todos los demás campos de la misma respuesta excluyen. Rompe la coherencia numérica y el alcance documentado "solo dealers".
- **Fix propuesto:** Añadir `AND kind <> 'particular' AND status = 'active'` a las líneas 260-262 (daría nonpart_active=932 para Madrid, alineado con `/geo/{province}/entities`).

#### E-inventory-platforms-no-entity-status-filter
- **Título:** `/entities/{cdp}/inventory` y `/platforms/{cdp}/inventory` no tienen filtro de status de la entidad propietaria, exponiendo stock de entidades unverified que `/geo/*` excluye deliberadamente.
- **Ubicación:** `services/api/routers/entities.py:133` ; `services/api/routers/platforms.py:62-63`.
- **Evidencia:** Filtran solo `v.status='available'`/`pl.status='listed'`, nunca `e.status`. `/geo` fuerza `status='active' AND kind <> 'particular'`. DB: 21 entidades unverified poseen 3.195 disponibles (active=1.694.052, unverified=3.195); enum `entity_status`={active,closed,unverified,evicted}. Ejemplo: CDP-ES-28-YSW14N9G (compraventa, unverified, 450 disponibles) servido por `/entities/{cdp}/inventory` pero excluido de `/geo/28/entities`. `resolve_cluster` (deps.py:87-122) busca por cdp_code SIN filtro de status. *Corrección:* el claim secundario `/platforms/{cdp}/inventory` está SOBREESTIMADO — cierto en código pero CERO exposición viva hoy (0 listings bajo dealer unverified; las 18 plataformas son active). Divergencia no documentada (main.py:21-37 documenta el filtro geo y la dedup de inventory, pero no la asimetría de status).
- **Por qué importa:** Superficie de producto inconsistente: un dealer cuya entidad sigue 'unverified' se oculta de geo pero su inventario completo lo sirven los endpoints de inventory/platform. Hoy es una inconsistencia no documentada entre las dos mitades de la API.
- **Fix propuesto:** Gatear `/entities/inventory` (y platforms por coherencia) en `entity.status='active'`, O documentar la divergencia en "Sealed product surface" de `main.py`. El ancla es el endpoint de entidades (3.195 coches en 21 dealers); platforms es preocupación de coherencia forward sin ruta de datos actual.

### Dimensión F — método/ops (1)

#### F-0033-false-transaction-claim
- **Título:** El docstring de la migración 0033 hace una afirmación FALSA sobre el modelo transaccional de `migrate.py` (trampa latente de hard-fail en enum-add).
- **Ubicación:** `migrations/0033_evict.sql:10-12` (afirmación) vs `scripts/migrate.py:117-124` (transacción única por archivo).
- **Evidencia:** 0033 dice "migrate.py wraps each statement individually via split_statements() so this statement runs in its own transaction". FALSO: `migrate.py:118` es un ÚNICO `async with conn.transaction():` que envuelve todo el loop `for stmt in stmts` + el INSERT al ledger; `split_statements()` solo trocea texto, no abre transacciones. Regla PG: `ALTER TYPE ... ADD VALUE` puede correr en txn block (PG12+) pero el valor nuevo NO puede usarse en la MISMA transacción. Reproducido en vivo (PG16.14): `BEGIN; CREATE TYPE ...; ALTER TYPE ... ADD VALUE 'c'; SELECT 'c'::enum; ROLLBACK;` → `ERROR: unsafe use of new value "c"`. Hoy benigno: solo 0017/0033 usan `ADD VALUE` y ninguno usa el valor en-archivo (grep vacío). *Nota:* la frase falsa son las líneas 11-12; la línea 10 (ADD VALUE seguro en txn PG12+) es correcta.
- **Por qué importa:** Un futuro autor que confíe en el docstring y escriba `ALTER TYPE ... ADD VALUE 'x'` luego `INSERT ... = 'x'` en el mismo archivo tendrá un hard-fail en runtime con toda la migración rolled-back. El invariante falso engaña activamente y se sienta en la ruta recurrente de extensión de enums.
- **Fix propuesto:** Corregir el comentario para declarar el modelo real single-transaction-per-file, O mandatar dividir toda migración `ADD VALUE` que necesite usar el valor en dos archivos (add value → commit → use).

---

## BAJOS (6)

### Dimensión A — datos (1)

#### A-km-year-outliers
- **Título:** 1.305 coches disponibles con km > 1.000.000 (máx 5.000.000) y 4 con year > 2027 (máx 2098).
- **Ubicación:** `vehicle.km`, `vehicle.year` (filas disponibles).
- **Evidencia:** km>1M=1.305, max=5.000.000; banda 500k-1M=4.182. year>2027=4, max=2098, min(>0)=1900. 0 km negativo, 0 `last_seen<first_seen`. Prueba de artefacto: 'SEAT Ibiza 2098' (título literal '2098'), 'MERCEDES Clase GLC 2060' km=1, 'castillejo 8'5 2028' cuyo título reza '2018' (misalineación de campo). km=5.000.000 aparece 7× como valor redondo repetido en años 2002-2015 (firma de centinela/cap). No existe guard de validación de rango en ingesta.
- **Por qué importa:** 5M km y year 2098 son artefactos de parseo físicamente imposibles (concatenación de dígitos o misalineación de campo). Volumen bajo, pero distorsionan distribuciones de km/edad. Años viejos (1925-1940) son clásicos plausibles, excluidos del conteo.
- **Fix propuesto:** Clampar/rechazar km fuera de ~[0,500000] y year fuera de ~[1900, año_actual+1] en ingesta; marcar en vez de guardar en silencio. No urgente.

### Dimensión B — identidad (1)

#### B-canonical-key-column-empty
- **Título:** La columna `entity.canonical_key` es 100% NULL — la key de minteo nunca se persiste.
- **Ubicación:** `entity.canonical_key` ; `services/api/codes.py:73-82` ; `migrations/0006_entity_evolve.sql:54`.
- **Evidencia:** `count(canonical_key)`=0 de 391.944. `cdp_code()` liga `canonical_key(...)` a la local `key`, la hashea, y devuelve solo `'CDP-ES-{prov}-{base32}'`; `key` nunca se devuelve/persiste. Ningún INSERT incluye `canonical_key` (`ingest.py:55-61`, `discover.py:68-76`, `dedup_upsert.py:216-223`); grep de `canonical_key` como write/columna = cero matches. La columna se añadió en 0006:54 con comentario "the exact key cdp_code hashed (audit)".
- **Por qué importa:** La identidad solo es auditable por ingeniería-inversa del hash. Sin la `canonical_key` persistida es imposible verificar qué key (domain vs cif vs name+muni vs particular:seller) minteó un cdp_code, ni detectar colisión/drift futuro, ni re-clusterizar por key. La columna da falsa impresión de estar poblada. (Determinismo intacto: cdp_code es la key estable.)
- **Fix propuesto:** Escribir `canonical_key` en los caminos de INSERT/upsert de entidad + backfill one-shot recomputando `canonical_key()` por fila.

### Dimensión D — verificación (1)

#### D-gestion-resolved-proof-verified
- **Título:** El guard RESOLVED-proof (0036) y los triggers append-only/anti-TRUNCATE (0034/0035) están presentes y funcionalmente forzados — verificado en vivo. **(NOTA POSITIVA, no defecto.)**
- **Ubicación:** `migrations/0036_gestion_resolved_proof.sql:16-41` ; `pipeline/gestionador/route.py:229-248` ; `pg_trigger` (vivo). (El path real del 0035 es `0035_append_only_row_guards.sql`.)
- **Evidencia:** 4 vectores transaccionales (todos ROLLBACK, cero mutación): (A) RESOLVED+verdict_id=NULL → bloqueado SQLSTATE 23001; (B) RESOLVED+verdict_id fantasma 99999999 → bloqueado; (C) RESOLVED+TRUSTWORTHY grandfathered quorum<2 → bloqueado; (D) RESOLVED+prueba real (TRUSTWORTHY quorum_n=2, id=1112) → **ACEPTADO** (control anti-blanket: acepta prueba válida, rechaza solo no-pruebas). `route.py:243` espeja la lógica del trigger exacto. Secundario append-only: TRUNCATE vehicle_event bloqueado; UPDATE+DELETE de fila real en verdict_audit bloqueados (P0001).
- **Por qué importa:** Es la única capa donde la garantía dura DB y el espejo de aplicación coinciden y se probó que rechazan un cierre no-prueba. Trata correctamente los grandfathered quorum=0 como prueba inválida. Confirma que la maquinaria forward funciona; el gap es puramente el corpus heredado sin backfill, no la lógica del guard.
- **Fix propuesto:** Ninguno sobre el guard (funciona). El trabajo asociado es cerrar el corpus heredado (ver `D-grandfathered-trustworthy-no-quorum`). Mantener; no tocar la lógica.

### Dimensión E — API (2)

#### E-cache-key-omits-auth-dimension
- **Título:** La key del cache de respuesta es solo `METHOD:PATH?query` — sin dimensión API-key/tenant; seguro bajo el modelo de key única actual pero fuga multi-tenant latente.
- **Ubicación:** `services/api/cache.py:76-88` ; `deps.py:29-35`.
- **Evidencia:** `_cache_key` usa solo method+path+query params ordenados; sin header X-API-Key ni tenant. `require_api_key` es una sola `CARDEEP_API_KEY` compartida (sin map per-tenant; grep 'tenant'=0). Auth se fuerza antes del body (Depends resuelve antes de `try_cache_get`, `entities.py:98` vs `:114`) → un 401 se levanta antes de leer cache (sin bypass anónimo hoy). `_cache` es singleton compartido → keys per-tenant cross-servirían bodies.
- **Por qué importa:** Correcto para el deploy single-key actual, pero introducir API-keys per-tenant SIN añadir la key/tenant a la cache-key haría que el tenant A sirviera el body cacheado del tenant B. Guardrail, no defecto vivo.
- **Fix propuesto:** Documentar en `cache.py` (espejando su caveat existente de single-worker) que introducir keys per-tenant REQUIERE añadir la key/tenant-id a la cache-key. LOW — flag, no block.

#### E-ratelimit-cache-env-import-time
- **Título:** El flag de habilitación de rate-limit y los strings de límite se congelan en tiempo de import; togglear `CARDEEP_API_RATELIMIT_ENABLED` en runtime no tiene efecto (documentado, pero foot-gun).
- **Ubicación:** `services/api/ratelimit.py:68-83,94` ; `deps.py:31`.
- **Evidencia:** `_ENABLED = os.environ.get('CARDEEP_API_RATELIMIT_ENABLED','1') != '0'` y los `RATE_*` son constantes módulo-nivel evaluadas una vez en import; `Limiter.default_limits=[RATE_DEFAULT]` se hornea en construcción. Repro en vivo: tras `os.environ['...']='0'` en el proceso ya importado, los valores quedaron sin cambiar. Contraste: `require_api_key` lee `os.environ` per-request (dinámico, repro confirmado 401 al setear la key en caliente). Documentado en `main.py:43-44` y `docs/.../05-SERVE-API.md:90`, pero NO en el call-site. (Path real del test: `tests/test_api_ratelimit_cache.py:188-202`.)
- **Por qué importa:** Operadores que pongan `CARDEEP_API_RATELIMIT_ENABLED=0` (o cambien límites) en un proceso vivo no verán cambio y pueden concluir erróneamente que los límites están off. La asimetría con el check de auth per-request es confusión operativa latente.
- **Fix propuesto:** Documentar la semántica import-time en el call-site de `ratelimit.py` (o leer el env per-request para paridad con auth). LOW — el default (enabled) es el estado seguro.

### Dimensión F — método/ops (1)

#### F-spend-gated-repairs-stall
- **Título:** Las auto-reparaciones spend-gated quedan `succeeded=FALSE` para siempre sin dren de escalación — verificado en vivo.
- **Ubicación:** `pipeline/ops/health.py:346,377-408` ; `repair_attempt` (vivo) ; `pipeline/ops/scheduler.py:612-652` (sin job de dren).
- **Evidencia:** GROUP BY: refingerprint|f|2 (filas family_cms_wp, 2026-06-12/13, ahora 2d17h rancias), escalate_owner|t|16, quarantine|t|1. `_SPEND_GATED_ACTIONS`={refingerprint,escalate_tier,re_receta} se escriben `succeeded=FALSE` con marcador "P10-spend: effect deferred" y `auto_repair` retorna sin re-encolar. Schema de `repair_attempt`: SIN `updated_at`/`resolved_at` → FALSE es estructuralmente permanente. Grep de consumidores `WHERE succeeded=false` = CERO. Los 3 `add_job` (heartbeat/silence_watchdog/inquisition_cadence) no referencian `repair_attempt`.
- **Por qué importa:** El loop de clasificación+alerta+auditoría corre correctamente (honestamente scaffolded, no faked), pero una fuente cuya única reparación viable es spend-gated queda rota indefinidamente con un `succeeded=FALSE` permanente y una alerta abierta — sin mecanismo para reintentarla cuando el gate P10 abra. "Auto-repair" tope en los peldaños €0 (quarantine/escalate_owner) para cualquier fuente hard-walled.
- **Fix propuesto:** Aceptable mientras el spend es intencionalmente €0 (documentado en `SCOREBOARD.md:114`). Cuando P10 abra: añadir un camino de resolución de fila (write path a `repair_attempt`) Y un job periódico de dren/escalación (ninguno existe hoy). LOW — ceiling conocido a revisitar, no defecto.

---

## Notas de método

- **Re-verificación:** los 37 hallazgos se confirmaron por un segundo camino independiente del que los produjo (query con formulación distinta, lectura de fuente `file:line`, o prueba transaccional rolled-back). Las correcciones a los findings (etiquetas mal puestas, citas de línea, sub-claims sobreestimados) están anotadas inline y NO cambian los veredictos.
- **Relación con Fase 1 (`AUDIT_2026-06-15.md`):** Fase 1 selló B-1 (escritura de quórum) y las fugas geo/status servidas; varios de sus 🟢 €0-TODO se solapan con hallazgos de aquí pero a mayor profundidad (p.ej. `E-geo-tree` ≈ H-3, `A-gone-listed` ≈ H-5, `B-canonical-key`/codes.py ≈ nota MEDIO). Los CRÍTICOS de scheduler/conectores/evicción y el corpus grandfathered son NUEVOS de esta fase.
- **Orden de ataque sugerido (€0, reversible):**
  1. **API data-loss** (`E-inventory-innerjoin`, `E-entity-available-count`) — números servidos incorrectos AHORA, 1.329 dealers a stock 0; fix de 2 call-sites (LEFT JOIN + COALESCE).
  2. **Scheduler cadencia Tier-1** (los 4 CRÍTICOS C-* + `C-autocasion-segment`) — cambios de `extra_args`/módulo en `scheduler.py`; AS24 (`C-as24`) = registrar el cosechador existente.
  3. **Scheduler cerrojo + deploy** (`F-scheduler-no-singleton-lock` advisory lock 1-línea, `F-autocasion-orphaned` rename de key 1-línea que arregla los tests rojos, luego `F-scheduler-never-deployed` deploy supervisado).
  4. **Evicción Gate-1** (`D-evict-gate1` join key) — corregir antes de que la evicción se active.
  5. **Recetas** (`C-cochesnet-recipe`/`C-wallapop-recipe`) — reconciliar ruta `recipes/` vs `_tier1/` + supresión de write en wholesale.
  6. **Verificación heredada** (`D-grandfathered`, `D-audit-chain`, `D-supersession`) — re-formar arrays + VALIDATE + backfill cadena + cablear supersession (DATA-fix, API no los lee → no urgencia de servicio).
  7. Resto MEDIO/BAJO + decisiones de Director (`B-crosssource` VAM-gate) según prioridad.
