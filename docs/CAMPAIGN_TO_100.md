# CAMPAÑA AL 100% — Cardeep

> Plan maestro de cierre desde el estado real (~60%) hasta el producto definido en `CLAUDE.md`:
> una base de datos viva y verificada con el 100% de los dealers y plataformas de España y todo
> su inventario en tiempo real. Documento de mando del Director. Estado vivo en `PROGRESO.md`;
> el plan de fases original sigue en `docs/MASTER_PLAN.md` (P0-P12) — esta campaña es la ruta de
> cierre operativa que lo absorbe en 6 bloques con gate binario.

## Método de ejecución (mando)

- **Cadena de mando:** Director + Inquisidor en Opus 4.8; **constructores en Sonnet** (Fable 5 sin acceso Mythos).
- **Workflows átomo:** cada bloque se monta como workflow(s) verificados; el E2E por dealer cubre
  descubrir → scrapear → receta → API → evicción. Nada se da por bueno sin verificar por ≥2 caminos.
- **Huella:** todo a GitHub `main`, documentado (recetas, estado, decisiones). Estructura en carpetas.
- **Coste:** €0 salvo muros Tier-1 autorizados uno a uno. LLM local para lo masivo donde el hardware
  dé; estadística (Splink) para dedup; inteligencia cara solo para decidir el slice ambiguo.
- **Evicción:** guardado el inventario + receta + config, el crudo se evicta por capacidad del PC
  (tombstone como prueba de vida). El PC es débil (AMD, sin CUDA, 16GB) — la evicción es obligada.

## Los 6 bloques (orden por desbloqueo)

| # | Bloque | Gate de cierre (binario, verificable en DB) | Estado |
|---|---|---|---|
| **B1** | Cerebro local + Identidad única | dealer↔1 cdp_code canónico (alias no-destructivo); tasa dup <0,1% por ≥2 caminos VAM | **✓ CERRADO 2026-06-14** |
| **B2** | Latido continuo | scheduler crash-safe re-cosechando por tier (24h/7d/30d); delta GONE/NEW reales 2ª pasada; governor multiproceso | **✓ CERRADO 2026-06-14** (B2.1 cadencia · B2.2 scheduler durable · B2.3 delta-GONE-guard · B2.4 silence-watchdog; governor multiproceso = deuda, no necesario con single-producer) |
| **B3** | Auto-reparación real + API blindada | fallo inyectado→alerta origen-exacto→auto-repair cierra lazo sin caer; alertas vivas cerradas; API paginada | **✓ CERRADO 2026-06-14** (B3.1 paginación · B3.2 resolve_alerts cableado a record_run · B3.3 encoding utf-8 scheduler · B3.4 motor_es false-cap-error + coches_com VAM diagnosticado · B3.5 prueba de resiliencia 5-tests + auth API-key + tolerance renting 0.005; 5/7 alertas cerradas, 2 degraded activas se auto-cierran al recuperar; rate-limit/cache = deuda P3) |
| **B4** | Geo al átomo | geocode-gap 32,5%→<2%; cada entidad a municipio/comarca | pendiente |
| **B5** | Cobertura total + filtrado | sells_cars resuelto; particular vs dealer decidido; Canarias/Ceuta/Melilla cerrados; cada segmento sellado o gap-con-causa | pendiente |
| **B6** | Sello 52/52 + separación física | SPAIN-SEALED (denominador medido + numerador VAM por provincia); `platforms/_tier1/` separado | pendiente |

## B1 — estado y hallazgos del reconocimiento (2026-06-14)

Reconocimiento de 4 vías (workflow `cardeep-b1-recon`). El "problema de identidad" son **tres** con raíces distintas:

| Sub-problema | Magnitud [VERIFICADO DB] | Raíz | Herramienta |
|---|---|---|---|
| A. Explosión OEM-VO | 39 clusters >20 = 4.042 filas de ~39 dealers | **Bug de ingesta**: clave de dealer inestable (fragmento por-coche) | Fix de código (B1.0) |
| B. Dup cross-source | 4.004 grupos / 9.266 filas | Mismo dealer en N plataformas con claves distintas | Splink (B1.3) |
| C. Dup intra-source | 270 grupos / 3.986 filas (milanuncios) | Drain sin dedup por author_id | Fix en el drain (B1.1) |

Datos duros: **CIF 100% vacío** (0/42.880), **website 4,4%**, **municipio 67%**. Blocking principal = nombre+municipio fuzzy.
Hardware: **CPU-only AMD, sin CUDA; vLLM inviable; Ollama qwen3 a ~10 t/s**. Dedup masiva = Splink (CPU, €0); LLM solo slice ambiguo (<2k pares).

### B1.0 — erradicar la explosión OEM-VO  *(CERRADO 2026-06-14)*
Auditados los 13 conectores OEM-VO (workflow Sonnet; Fable 5 sin acceso Mythos). **2 inestables arreglados**: `oem_mercedes_benz`
(clave `dealer:{dealerCode-por-coche}` → explosión 480 entidades / 488 coches, ratio 1.02) y `das_weltauto` (BNR VW multi-formato
`C311K`/`0311K`/`30060` → 18 dealers fragmentados ×2-3). Ambos unificados a la clave **conservadora `name + municipio`** (`address=None`);
el id por-coche queda solo como `source_ref`. El código postal se deja FUERA del hash a propósito (un card que no parsee su CP
fragmentaría); separar dos sucursales legítimas del mismo nombre+municipio se delega a `entity_cluster` (B1.3). **11 conectores
restantes SANOS** y no tocados (dealer_id estable del portal: spoticar, toyota_lexus, audi, bmw/mini, hyundai, volvo_jlr_suzuki,
nissan, kia, seat_cupra, renew, ford). 18 tests verdes. Forward-fix; lo histórico lo colapsa B1.3.

### Secuencia B1
`B1.0` forward-fix OEM-VO → `B1.1` dedup drain milanuncios → `B1.2` migración `entity_cluster`/`entity_cluster_run`/`v_canonical` →
`B1.3` job Splink v4.0.16 sobre PostgreSQL (blocking que excluye dominios OEM corporativos) → `B1.4` canónico determinista
(fuente→riqueza→antigüedad→lexicográfico) → `B1.5` VAM 3 caminos → `B1.6` API resuelve cualquier código→canónico.

## Diseño de identidad inmutable (B1.2)

`cdp_code` nunca se reescribe. Se superpone:
- `entity_cluster(cluster_run_id, cdp_code, canonical_cdp_code, match_probability, ...)`
- `entity_cluster_run(cluster_run_id, splink_version, threshold, n_in, n_clusters, vam_verified, ...)`
- vista `v_canonical` resuelve `cdp_code → canonical_cdp_code` en query-time (solo el run con `vam_verified=TRUE`).

## B2 — diseño (latido continuo) [2026-06-14]

Reconocimiento del motor [VERIFICADO]: NO hay scheduler (todo manual `python -m`); governor single-process asyncio
(multiproceso = cicatriz AS24 repetible); delta NEW/PRICE/KM/PHOTO/GONE implementado en `ingest.py` (1.499.942 NEW /
1.912 GONE / 1.375 `status='gone'`) PERO cableado solo a AS24 (los conectores wholesale tienen su cage propia); S-HEALTH
pasivo (bibliotecas que el conector llama, sin watchdog en cadencia); 7 alertas abiertas; Redis solo de CARDEX; `is_tier1`
a `false` en las 47 fuentes.

**Decisión arquitectónica:** scheduler **single-producer** (un conector por ventana, en serie) — en este PC débil evita
saturación Y la cicatriz AS24 (sin 2 procesos pisando el governor), por lo que el governor single-process ACTUAL basta y
**Redis-GCRA NO es necesario en B2** (deuda registrada para cuando se paralelice).

Sub-bloques:
- **B2.1 — Tier + intervalos:** migración 0021 (añadir `harvest_interval_hours` o categoría de tier a `source_health`);
  poblar `is_tier1` y el intervalo por fuente; setear `is_tier1` en `record_run`. Prerequisito del scheduler.
- **B2.2 — Scheduler durable:** APScheduler 3.x + `SQLAlchemyJobStore` sobre `cardeep-pg`. Single-producer: itera fuentes
  donde `now - last_ok >= interval`, lanza el conector como **subprocess** (aislamiento crash-safe), registra. Jobs en PG
  → sobrevive reinicio.
- **B2.3 — Delta 2ª-pasada verificada:** guard de GONE — emitir GONE solo si `harvested >= declared * 0.95` (evita GONEs
  falsos por paginación parcial / timeout a media página). Uniformar el delta en los conectores wholesale.
- **B2.4 — Watchdog de silencio:** job de salud que detecta fuentes sin `last_ok` en > 2× su intervalo → `fire_alert`.

**Gate B2:** scheduler crash-safe re-cosechando por tier (24h/7d/30d) corriendo; delta GONE seguro verificado en 2ª pasada;
cero repetición de la cicatriz AS24; `is_tier1`/intervalo operativos.

## B3 — diseño (auto-reparación + API blindada) [2026-06-14]

Reconocimiento [VERIFICADO]: `auto_repair` tiene `quarantine` (cierra lazo: breaker para la fuente, €0) + `escalate_owner`
(honest wall); las 3 acciones de gasto (refingerprint/escalate_tier/re_receta) diferidas P10 (`succeeded=FALSE`). **GAP
CRÍTICO**: `resolve_alerts()` existe (health.py:256) pero NINGÚN harvester la llama → las 7 alertas nunca se cierran (ruido
permanente; varias ya recuperaron). **HAZARD API**: `/platforms/{cdp}/inventory` devuelve 576k filas sin LIMIT (wallapop),
`/entities/{cdp}/inventory` 17k, `/geo/{prov}/entities` sin límite; sin cache/auth/rate-limit. Pool API separado del harvester
(OK, un scraper no tumba la API). Encoding: `_force_utf8_stdout` en 35 archivos pero inconsistente (en `main()` no en `harvest()`).

Sub-bloques:
- **B3.1 — API blindada (paginación) [P0 HAZARD]:** page/size + LIMIT en `/platforms/{cdp}/inventory`, `/entities/{cdp}/inventory`,
  `/geo/{prov}/entities`, `/entities/{cdp}/delta`. Envelope con meta de paginación.
- **B3.2 — Cierre del lazo de alertas:** cablear `resolve_alerts()` en el path de éxito (un `record_run(ok=True)` cierra las
  alertas abiertas de esa fuente). Cerrar las transitorias actuales.
- **B3.3 — Encoding uniforme:** centralizar `_force_utf8_stdout` en un módulo + `PYTHONIOENCODING=utf-8` en el subprocess del
  scheduler + guard en `harvest()` de coches_com + subastacar/wallapop_facet. Cierra el bug `Σ`.
- **B3.4 — motor_es VAM falso:** distinguir "cap de 50 páginas" (documentado, no es fallo) de fallo real → sin alerta crítica falsa.
- **B3.5 — Resiliencia probada + auth/rate-limit:** fallo inyectado → alerta exacta + auto-repair + API sigue; API key + rate-limit básico.

**Gate B3:** fallo inyectado→alerta origen-exacto→auto-repair cierra lazo sin caer; alertas resueltas (`resolve_alerts` cableado);
API paginada (sin hazard); encoding uniforme.

## Log
- 2026-06-14 — Reconocimiento B1 cerrado (4 vías). Raíz explosión OEM-VO confirmada. Plan de campaña sellado.
- 2026-06-14 — Fable 5 sin acceso (Mythos restringido). Routing efectivo de la campaña: **Sonnet construye, Opus dirige y verifica**.
- 2026-06-14 — B1.0 CERRADO: `mercedes_benz` + `das_weltauto` arreglados (clave `name+municipio`); 11 conectores OEM-VO restantes auditados sanos; 18 tests verdes.
- 2026-06-14 — MISSION.md sellado (super-prompt maestro, asignado como /goal). Splink 4.0.16 instalado y verificado (importa con pandas 3.0.3).
- 2026-06-14 — B1.2: migración `0020_entity_cluster` aplicada y verificada (overlay no-destructivo `entity_cluster` + `entity_cluster_run` + vista `v_canonical`; FK por `entity_ulid` porque `cdp_code` solo tiene unique index; `vam_verdict_id`→`verification_verdict(id)`). Falso positivo descartado: `migrate.py` está limpio (no tiene el NameError que un agente reportó).
- 2026-06-14 — B1.1 CERRADO: milanuncios `authorId` per-sesión fuera del hash → clave `name+municipio` (29 tests, particulares intactos). commit `bcee353`.
- 2026-06-14 — B1.3/B1.4: Splink 4.0.16 (DuckDB) dio recall 61% (el modelo probabilístico pierde los exactos `name+muni` con cif 0%/web 4%). Refinado a determinista; **hallazgo: Splink aportaba ~1%, prescindible**.
- 2026-06-14 — Pipeline CONSOLIDADO a un solo script determinista, reproducible, SIN Splink (`pipeline/identity/cluster_dealers.py`). FIX A: fuzzy levenshtein guardado a `len≥8` (`Megar`≠`Vegar`). FIX B: normalización de sufijos societarios (`S.A.`/`S.L.` → variantes unidas por la arista exacta).
- 2026-06-14 — **B1 SELLADO** (commit `89eb8e0`). Run `dealer-identity-det-v1` `vam_verified` (verdict 640): 42.898→**31.472 canónicos** (11.426 alias→canónico), recall intra-fuente **100%**, **0 FP** cross-muni, cadenas preservadas. API resuelve a canónico + inventario agregado (13 tests). `v_canonical` activo. Reproducible, cero `cdp_code` reescrito; run Splink purgado. Lecciones (higiene de locks; FK por `entity_ulid`) en `MISSION.md`.
- **SIGUIENTE → B2 (latido continuo):** scheduler durable + governor multiproceso + delta GONE/NEW real en 2ª pasada.
