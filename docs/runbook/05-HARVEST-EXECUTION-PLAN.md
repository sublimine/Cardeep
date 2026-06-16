# 05 — PLAN DE EJECUCIÓN DE LA FASE GATED (el "cómo del A al Z" para terminar A→F)

> **Propósito.** El €0-config A→Z está construido, verificado y servido (deploy reproducible, CI,
> runbooks, stack de verificación de 4 capas, API, delta, identidad, recetas, **sello venta+desguace
> servido por `/geo/seal`**). Lo que queda de A→F NO es código €0 — es **alimentar la maquinaria con
> la cosecha** (harvest), datos externos y hardware. Este documento descompone esa fase gated en
> micro-tareas atómicas, en orden de dependencia, con su comando real, su agente/skill/herramienta,
> su gate de verificación, su presupuesto de recursos y su criterio de éxito. **Es el prerequisito
> que el Owner puso para abrir gasto** ("hasta que no esté todo… con absolutamente toda la
> implementación y el cómo… del A al Z"). Verificado contra el estado real de la DB y el código a
> 2026-06-16; cada módulo citado existe.

---

## 0. Envelope de recursos (restricción D1 — "haz lo que puedas sin ahogar el PC")

| Recurso | Medido | Implicación de ejecución |
|---|---|---|
| CPU | Ryzen 5 5500U (6c/12t) | concurrencia de drain = `DEFAULT_CONCURRENCY` baja (1 fuente a la vez) |
| RAM libre | ~1,7–2,1 GB (16 GB; ~13 en OS+Docker, cardex-pg ajeno 1,6 GB) | **NO** correr 2 drains a la vez ni LLM ≥3B simultáneo al pipeline |
| GPU | Radeon iGPU, **sin CUDA** | LLM local = CPU-only → D1 diferido a ventanas idle |
| Disco | ~34 GB libre (Docker 44 GB) | **evict-by-capacity OBLIGATORIO** (`pipeline/evict.py`, `--apply` autorizado por dealer-muerto) |

**Regla de oro de la fase**: 1 fuente baja-concurrencia → su verificación → evict del raw → siguiente.
Nunca abrir un segundo frente de harvest sin cerrar+evictar el anterior (igual que el orden de batalla
de bloques). El governor (`pipeline/engine/governor.py`, battle-tested 25/25) pacea por host.

---

## 1. DAG de ejecución (orden de dependencia de lo gated)

```
A3-drains (cosecha real, 34 fuentes instrumentadas B9)
   │  └─ por cada fuente: scrape → coverage_verify dispara → reconcile_gone (bajas) → evict
   ▼
A4-2da-pasada (verifica deltas PRICE/KM/PHOTO/GONE en la 2ª corrida)   ← depende de ≥2 corridas
   │
   ├─► SU-SEAL-venta numerador↑ (más dealers con inventario → más SELLADO en v_province_seal)
   │
   ▼
A5-recipe-hunt (23.894 dealers sin inventario → cazar su receta own-site)   ← paralelo a A3 por dealer
   │
   ▼
A2-Chao2 / denominador-refine (Overture→entity_source + fuente fiscal cross-cover)  ← DATA externa
   │
   ▼
C1/C2-Tier-1 a escala (correr los 7 Tier-1 con su receta ya cazada)   ← anti-detección spike primero
   │
   ▼
B2-lentes B/C (raw-store para Lens B recount + live-refetch para Lens C)   ← egress separado
   │
   ▼
R1 desguace-inventario · R2 concesionario-harvest · R3 sells_cars-labels   ← numerador rojo
```

---

## 2. Micro-tareas atómicas por punto gated

> Columna **gate** = el predicado binario que cierra la micro-tarea (no se pasa a la siguiente sin él).
> Columna **arsenal** = agente/skill/herramienta que conduce la tarea.

### A3 — Drains reales (el corazón de la cosecha)

| # | Micro-tarea | Comando / módulo real | Arsenal | Gate de verificación | Presupuesto |
|---|---|---|---|---|---|
| A3.1 | Anti-detección spike (C1) ANTES de cualquier Tier-1 | `pipeline/engine/fetch.py` + Camoufox; re-probar 5 OPEN + 2 walled | cardex-scraper agent · curl_cffi/Camoufox | `state/tier1-blocked.json` escrito; ClientHello byte-diff vs Chrome OK | red, 1 sesión |
| A3.2 | Drain 1 fuente top-volumen (coches_net 274k) baja-concurrencia | `python -m pipeline.platform.coches_net_wholesale` | cardex-scraper · governor | `record_run` dispara `verify_coverage`; `v_province_seal` numerador↑; sin ban | RAM<2GB, paced |
| A3.3 | `reconcile_gone` confirma bajas en esa fuente | central en `record_run` (coverage→boundary→reconcile) | — (automático) | `source_coverage.verdict` ≠ REFUTED ∧ bajas emitidas en `vehicle_event` | €0 tras drain |
| A3.4 | **Evict del raw de la fuente** | `python -m pipeline.evict --cdp … --apply` | refactor-cleaner · evict.py | `capacity_ledger` fila + disco recuperado; tombstone no DELETE | €0 |
| A3.5 | Repetir A3.2-A3.4 por las 34 fuentes instrumentadas | idem, 1 a 1 | cardex-scraper | las 34 con `source_coverage` no-NULL + verdict sano | semanas, paced |

**Éxito A3**: B9 corrido en 34/34 fuentes con `Σleaf==declared` o causa declarada; AS24/milanuncios
full-index re-probados. (dasweltauto ya instrumentado 06-16; 8 family_* = N/A-declarado correcto.)

### A4 — Delta verificado en 2ª pasada

| # | Micro-tarea | Módulo | Arsenal | Gate |
|---|---|---|---|---|
| A4.1 | 2ª corrida de cada fuente top-5 | conectores | cardex-scraper | `emit_change_deltas` emite PRICE/KM/PHOTO en re-vistos (ya cableado en 26) |
| A4.2 | Confirmar GONE en vivo | `reconcile_gone` boundary-fallback | — | un vehículo retirado real → `vehicle_event` GONE (probado end-to-end 06-16) |

### A5 — Recipe-hunt de los 23.894 sin inventario

| # | Micro-tarea | Módulo | Arsenal | Gate |
|---|---|---|---|---|
| A5.1 | Clasificar los 23.894 por plataforma vs own-site | `v_dealer_recipe` (recipe_kind) | python-reviewer · SQL | lista own-site aislada |
| A5.2 | Cazar receta own-site (JSON-LD/sitemap) por dealer | `pipeline/discover.py` + `recipe.py` | cardex-scraper · Context7 (schema.org) | `recipe.yaml` per-dealer commiteado en árbol geo |
| A5.3 | Stamp receta + 1er scrape | `harvest_dealer.py run(slug)` | cardex-scraper | inventario>0 servido + VAM |

### A2 — Denominador Chao2 (DATA externa)

| # | Micro-tarea | Fuente | Arsenal | Gate |
|---|---|---|---|---|
| A2.1 | Cargar Overture Places → `entity_source` (2ª captura ortogonal) | Overture Maps (público) | database-reviewer · DuckDB/Parquet | familias de captura ≥3 homogéneas |
| A2.2 | Cross-cover con fuente fiscal (DIRCE 451 si INE publica per-provincia) | INE | python-reviewer | `denominator_estimate` Chao2 con CI membership-filtered |
| A2.3 | Re-juzgar Chao2 (hoy REFUTED por capturas disjuntas) | `pipeline/verify.py` | Opus-gate (Inquisición) | verdict ≠ REFUTED o causa declarada |

### C1/C2 — Tier-1 a escala · B2 — lentes B/C · D1 — LLM · R1-R3

| Punto | Micro-tarea núcleo | Gate de cierre | Recurso |
|---|---|---|---|
| C2 | Correr los 7 Tier-1 con receta ya cazada (`countries/ES/_tier1/`) | 2-way count + field-VAM por plataforma | harvest (post-C1) |
| B2-LensB | Construir raw-store (S3/disco) → `extruct` activa el recount | Lens B deja de ABSTAIN; D=2 real | disco/egress |
| B2-LensC | Live-refetch con egress separado | Lens C deja de STUB; D=4 | egress premium |
| D1 | Ollama qwen2.5:3b en ventana idle (clasificar/normalizar masivo) | benchmark t/s registrado, sin ahogar pipeline | RAM idle / hardware↑ |
| R1 | Desguace inventario (Opisto/own-site) | inventario>0 con VAM en ≥1 provincia (techo schema.org ~1,5%) | harvest |
| R2 | Concesionario harvest (FACONAUTO más allá OEM-VO) | servido CO sube de 11,6% con VAM | harvest |
| R3 | sells_cars labels (7.195 ambiguos) | labels externos/plataforma → 100% `kind=garaje` resuelto | DATA externa |

---

## 3. Lazo E2E per-dealer (ya documentado — referencia)

Cada dealer recorre el grafo de estados de `docs/workflows/e2e/` (DESCUBRIR→SCRAPEAR→RECETA→INGEST→
SERVE-API→DELTA→**BORRAR**). El scheduler durable (`pipeline/ops/scheduler.py`, APScheduler+PG jobstore,
crash-safe) orquesta; la cadencia δ (`inquisition_cadence_job`, 6h) re-verifica. **El módulo BORRAR
(`evict.py`) es lo que hace sostenible la fase en este hardware** (guardar config + evict por capacidad).

## 4. Cadencia de verificación durante la fase (NO confiamos en ningún resultado)

Cada corrida pasa por las 4 capas (`docs/architecture/10-VERIFICATION-STACK.md`): **L1 VAM** (quórum de
conteo post-ingest) → **L2 deep-ledger** (0026, quórum DB + hash-chain, re-verificado íntegro 06-16) →
**L3 gestionador** (0031, 7 detectores de anomalía: count_inflation/silent_cap/field_loss/staleness/…) →
**L4 Inquisición V3** (0032, 5 lentes adversariales). Una anomalía → alerta origen-exacto → auto_repair
€0 → si falla, gestion_item con SLA. El sello (`v_province_seal`) refleja el progreso en vivo sin snapshot.

## 5. Go / No-Go por fase (criterio de avance)

1. **No abrir A3** sin C1 (anti-detección) verde para las fuentes walled.
2. **No pasar de una fuente a la siguiente** sin su `source_coverage` sano + raw evictado (envelope D1).
3. **No declarar SEAL-pleno** sin denominador Chao2 no-REFUTED (A2) — hoy el sello honesto es venta
   13/30/9 + desguace 52/52 sobre el ancla registral, servido y correcto.
4. **No correr D1-LLM** mientras el pipeline esté activo (ahogaría la RAM) — solo ventana idle.

---

**Estado de este plan**: el €0 está hecho y servido; este documento es el mapa de la fase de gasto que
el Owner difirió (D1). Cuando se autorice presupuesto, se ejecuta A3.1→A3.5 por fuente, paced, con su
verificación y evict, y el sello sube solo (numerador↑ en `v_province_seal`). Cada micro-tarea tiene su
gate binario: no se pasa a la siguiente sin cerrarla.
