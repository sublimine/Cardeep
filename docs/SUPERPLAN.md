# SUPERPLAN A→Z — Sellado punto por punto de Cardeep

> **Documento de mando operativo del Director Soberano.** Convierte la auditoría de cobertura
> del prompt fundacional (puntos A·Producto → F·Método + gaps) en un backlog de **unidades de
> sellado (SU)** dependency-ordered, cada una con gate binario verificable en DB/test y su
> workflow de construcción+verificación.
>
> **No reemplaza** `docs/MISSION.md` (el /goal, el porqué), `docs/MASTER_PLAN.md` (P0-P12, el
> schema-spine) ni `docs/CAMPAIGN_TO_100.md` (B1-B6, log vivo). **Los absorbe en clave de
> "sellar A-F".** Donde haya conflicto de numeración, MASTER_PLAN §1 (contradicciones) gobierna.
>
> **Regla de hierro:** una SU no se cierra hasta estar **construida + verificada por ≥2 caminos
> ortogonales + testeada + commiteada a `main`**. NO se pasa a la siguiente SU sin sellar la
> anterior. Cada número se confirma por una vía distinta a la que lo produjo. Yo (Opus) soy el
> GATE de Inquisición; los constructores son Sonnet; Fable 5 sin acceso.
>
> **Clasificación viva en GitHub** (proyección filtrable de este §4):
> [Issues](https://github.com/sublimine/Cardeep/issues) — 1 issue por SU, etiquetada por
> letra/estado/gate/área y agrupada en 4 milestones (Fase 0 · €0-Config-A-Z · Fase-de-gasto ·
> Terminal). Cerrado = sellado, abierto = restante (todo spend/data/hardware-gated). Se
> regenera idempotente con `python scripts/github_classify.py` (fuente de verdad = este doc).

---

## 0. Doctrina de mando (cómo opero — HANDS OFF, autoridad total)

- **No paro la producción hasta terminar.** Supervisión + gestión activa de todo. Estado siempre
  a disco (este doc + `PROGRESO.md`) → sobrevive compactación; retomo por §9.
- **€0 hasta A→Z.** Sin gasto cloud/LLM-API hasta que TODO esté configurado, con recetas, runbook
  claro y la implementación completa documentada. Decisión de gasto = la última fase, solo entonces
  se presenta al Owner.
- **Sin frontend** (D2): `cardeep-web` archivado y eliminado. Foco 100% backend/datos.
- **Reversible → ejecuto; irreversible → confirmo.** Push no-force a `origin/main` autorizado
  permanente. Autoridad total sobre decisiones de negocio (D4).
- **Calidad máxima, sin prisa, a nivel átomo.** Nada de medio-hechos, placeholders, stubs.

## 1. Restricciones de hardware [VERIFICADO 2026-06-15]

`Ryzen 5 5500U 6c/12t @2.1GHz · 15,3GB RAM (≈2GB libres) · Radeon iGPU 0,5GB VRAM, sin CUDA ·
Disco C: 470GB / 20GB libres ⚠️ · Ollama qwen2.5:3b + qwen3:4b + qwen3:8b · Python 3.11.9 · Docker 29.2.1`

**Reglas derivadas (lente foundation-models-on-device + cost-aware):**
1. **Determinista-first** para todo lo masivo (dedup, clasificación regla-suficiente). LLM solo el slice ambiguo.
2. **Ollama single-stream, off-peak.** Default `qwen3:4b`; `qwen3:8b` solo lotes pequeños (RAM); `qwen2.5:3b` para trivial.
3. **Evicción agresiva + vigilancia de disco** (20GB libres = restricción binding). Crudo efímero, recipe durable.
4. **Sin paralelismo de procesos pesados** que reviente RAM. Workflows de agentes = orquestación de razonamiento, no N navegadores a la vez.
5. Evaluar liberar infra CARDEX predecesora (RAM/disco) tras verificar que está dormida.

## 2. Estado verificado [DB viva 2026-06-15]

| Métrica | Valor | Sello |
|---|--:|---|
| entity total | 390.621 | — |
| · particular (C2C) | 329.070 | fuera del modelo POS (→ listados) |
| · profesional (no-particular) | 61.551 | universo de B1/β |
| dealers canónicos (B1) | **42.259** | ✅ `dealer-identity-det-v1` vam_verified=TRUE |
| β resolved dealers | 52.156 | 🟡 vam_verified=FALSE (2 fixes) |
| vehicle (anuncios) | ~1.692.715 | — |
| vehicle_cluster (B7 únicos) | 1.443.563 | 🟡 vam_verified=FALSE (0km) |
| vehicle_event (delta) | ~1.707.058 | append-only |
| verification_verdict | 1.038 | light-VAM (0004) |
| migraciones aplicadas | 0001-0007,0009,0013,0016-0022 (16) | 🔴 falta 0014 deep + ledger drift 0023/24/25 |
| source_coverage (B9) | 4/47 fuentes | 2 TRUSTWORTHY, 2 REFUTED |

**6 hallazgos del audit** (ver §3 SU-0.x / SU-B.x): ledger drift · 0014 no construida · vam_verdict_id NULL · 4 cadena · β/B7 sin sellar · B9 4/47.

## 3. Doctrina de orquestación — el patrón "unidad de sellado"

Cada SU se monta como un **workflow** (`.wf/<su>.js`) con cuatro fases y un gate. Carpeta de
artefactos por SU. Todo a `main`.

```
WF-<SU>:
  1. RECON   — agentes Explore/Opus: auditan la raíz (código+DB+docs), mapean, NO asumen.
  2. BUILD   — agentes Sonnet (isolation: worktree si tocan ficheros en paralelo): implementan a nivel átomo.
  3. VERIFY  — yo (Opus) + agentes adversariales: corro los tests, verifico CADA número por ≥2 vías,
               intento REFUTAR. Default refutado si no reproducible.
  4. SEAL    — yo: commit + push main, actualizo PROGRESO.md, marco el gate verde, persisto verdict.
  GATE: no entra a SEAL sin VERIFY verde. No pasa al siguiente SU sin SEAL.
```

**Routing de modelos:** Sonnet construye · Opus (yo) dirige/verifica/sella · Ollama local para
clasificar/parsear/deduplicar masivo · Fable 5 sin acceso. **Skills/herramientas se declaran por SU.**

**Taxonomía de carpetas (organización masiva, todo a GitHub):**
```
.wf/<su>.js                         workflow de cada SU
docs/SUPERPLAN.md                   este doc (plan maestro de sellado)
docs/sealing/<SU>/                  RECON.md · BUILD.md · VERIFY.md · evidencia
docs/archive/                       material retirado (frontend spec, etc.)
migrations/                         spine reproducible (ledger reconciliado)
state/ [gitignored]                 run-state efímero
```

---

## 4. EL BACKLOG DE SELLADO (por letra A→F + gaps)

Leyenda gate: cada SU define un **predicado binario verificable en DB/test/filesystem**.
Estado: ⬜ pendiente · 🔵 en curso · ✅ sellado.

### FASE 0 — CIMIENTO (prerequisito de A-F: higiene, verdad, reproducibilidad) · €0
> Sobre cimiento sucio/no-verificado no se sella nada. Son los átomos de A·producto que todo lo demás necesita.

| SU | Definición | GATE binario | Estado |
|---|---|---|---|
| **SU-0.1** | Eliminar frontend (D2) | `cardeep-web` archivado en `docs/archive/frontend-spec/` + folder borrado + commit | ✅ `ff88fe4` |
| **SU-0.2** | Reconciliar ledger de migraciones | `schema_migrations` == schema vivo; 0023/24/25 registradas + .sql commiteados; rebuild en DB desechable reproduce el schema sin error | ✅ 19/19, rebuild 25t+4v OK (commit 0023 en SU-0.3) |
| **SU-0.3** | Commitear todo lo untracked | `git status` limpio salvo gitignored; B7(0023+cluster_vehicles.py+test)+538 recetas+code en `main`; scratch ruidoso → `.gitignore` | ✅ `15550f7` (3 commits, B7 test 37✓) |
| **SU-0.4** | Linkar verdicts de sellos | todo `*_run` con `vam_verified=TRUE` tiene `vam_verdict_id`→`verification_verdict` no-NULL; B1 apunta a verdict 640 | ✅ B1→640 linkado (único run sellado) |
| **SU-0.5** | Corregir ontología cadena | `SELECT count(*) FROM entity WHERE kind='cadena'` = 0 (reasignadas a organization) | ✅ 4 orgs, Flexicar rollup 23874. **⚠️ CORREGIDO 06-16: NO es "0 cadena" — queda 1 entity `kind='cadena'`** (el anchor nacional de Flexicar, role='chain', province NULL). Residual de la reasignación a organization. Provoca el recipe-coverage gap de §A5 (el CTE de `v_dealer_recipe` no reconoce kind='cadena'/role='chain'). |
| **SU-0.6** | Auditoría de disco + evicción | disco con ≥15% libre; política de evicción configurada + verificada; infra CARDEX evaluada | ✅* 21,4GB Docker reclamados; host 96%=datos ajenos+VHD WSL2 (Cardeep=307MB); evict.py=debt (data/ 161MB, baja urgencia); 15% infeasible sin acción Owner |

### A — EL PRODUCTO

| SU | Punto | Definición | GATE | Estado |
|---|---|---|---|---|
| **SU-A1** | Código único (B1) | confirmar átomo + mejorar | dup<0,1% por ≥2 vías sobre datos vivos; `v_canonical` íntegra; verdict linkado (SU-0.4) | ✅ 0 under-merge host+muni, 0 bosque roto, verdict 640 → **HALLAZGO cluster AS24** (kind mis-class, prov-bug Clicars, 147 cadena sin org-link) → SU-A2. **CAVEAT 06-15 (gate SU-A9)**: 42.259=TECHO; sobre-conteo ~2.300–6.876 por **geocoding-dup** (mismo dealer→muni distinto; **34.904 deep_links bajo >1 canónico**, 4.621 canónicos); real ~35.400–40.000. Clave nombre+muni LIMPIA (0 dup por la clave EXACTA del B-DEDUP; ⚠️ bajo `lower+trim` hay **75 under-merges** — ver RECALL GAP al final de esta celda). **SU-B-DEDUP SELLADO+SERVIDO** (0027+0028+script, verdict **1121** quorum 2/3/3 supersede 1112): dealer-count corregido **40.016** (B1 42.259 − merges deep_link; el 39.874 fue miscount cazado en el gate de integración). API/`/health` ya sirve 40.016 (suite 457✓). **RECALL GAP 2026-06-16 (auditoría coherencia): la clave del dedup B1 dejó 75 under-merges** — 75 grupos (nombre-normalizado + muni) con ≥2 canónicos del MISMO dealer (verificado: "Almoauto Motor Hyundai" muni 28049, "VISAUTO ALICANTE-VO" muni 03056 = nombres específicos, mismo muni/kind → mismo dealer no fusionado). Dealer-count inflado ~75 (0,19%, minor). **Corrige el claim de memoria "nombre+muni LIMPIA 0 dup" (es 75 bajo lower+trim).** Fix determinista (mismo nombre-específico+muni = mismo dealer) pero toca el core `v_dealer_resolved` (→ dealer-count + numerador del sello) → escalado a la **unidad de dedup-recall-hardening** junto al gap deep_link de coches (11.930): ambos añaden señales DETERMINISTAS (deep_link / nombre+muni) al dedup probabilístico B1/B7; no mutar core a profundidad. |
| **SU-A2** | Descubrir — denominador P | arco β→φ→Chao2 | β sellado (guarda cadenas + B1∘β, gate cero-sobre-fusión); φ con DIRCE; Chao2 ortogonal + cierre saturación; N̂(P) con CI membership-filtered | 🟡 **β SELLADO** (verdict 1093, S_obs **38.555**). **φ/Chao2 GATEADO**: Chao2 sobre 3 familias = **REFUTED** (verdict 1111; capturas disjuntas, Q1/Q2=43, N̂ 852k >techo 10×). Denominador del sello = **ancla oficial CNAE-451** (F8 94,3%). **DENOMINADOR PER-PROVINCIA PERSISTIDO 06-16** (`scripts/load_denominator_provincia.py`, €0): `denominator_estimate` ahora tiene **52 filas `segment='venta'`** (method `registral_ceiling`, `point_est = cnae45_locales × ratio_451/45 0,2605`, Σ=22.720 ≈ DIRCE-451 nacional 23.085; fuente VERIFICADA `data/official/denominador_cnae45_provincia_2024.csv`) + la fila nacional `P_all` floor 38.555 intacta → **A2 ya tiene denominador per-provincia, no solo el floor**. El SELLO per-provincia es computable desde DB (`calc_spain_sealed.py` tiene el método; el numerador debe ser el canónico-deduplicado `COUNT(DISTINCT COALESCE(canonical_ulid,entity_ulid))`, NO entity-level que sobre-cuenta). **Chao2 sellable DEFERIDO** (prereq: Overture→entity_source, fuente fiscal cross-cover, sells_cars, estratificar). |
| **SU-A3** | Scrapear TODO el stock | exhaustividad universal | B9 coverage gate corrido en **47/47** fuentes; cada drain `Σleaf==declared` o causa; AS24/milanuncios REFUTED resueltos | 🟡 RECON (`docs/recon/SUA3_EXHAUSTIVIDAD_RECON.md`): B9 gate EXISTE (`coverage_verify.py`, €0). **2/47 TRUSTWORTHY** (coches_net 100,8%, wallapop 90,3%), **2 REFUTED** (milanuncios=BUG `declared_total` 110k-de-1-shard vs 397k DB → probablemente inventario completo; as24=proof-slice 22%, drain real nunca corrió), **42 sin instrumentar**. **Plan**: ①€0-código (fix bug milanuncios=suma partition-totalHits + instrumentar 42+coches_com + discrepancia as24-no-en-source_health), ②drains paced (D1: PC 1,7GB RAM/34GB disco → 1 fuente baja-concurrencia + evicción). 585 cdp-recetas YAML. **FASE-1 €0 ✅**: 2 REFUTED→UNVERIFIED (AS24 gap-declarado proof-slice v1122; milanuncios scope-mismatch v1123), B9 v2 (over-cov→UNVERIFIED no REFUTED, tests 4✓), coches_com instrumentado, as24+source_health(48). **FASE-2 paced-D1**: re-probe milanuncios full-index + instrumentar 42 + drains AS24/autocasion/motor.es. **INSTRUMENTACIÓN €0 COMPLETADA (06-16)**: los **27 conectores con declared_full ahora pasan declared_total a record_run** (7+9+9 vía workflows de batches pequeños rate-limit-safe + bmw/wallapop_facet a mano; verificación adversarial PROPIA per-conector: AST+import+declared_total+bare-var-en-scope, 0 fails; commits `d56734b`/`cb9eec2`/`0297a69`/`f291dea`) → con los 7 ya-instrumentados = **~34 fuentes disparan el gate B9 en harvest**. **dasweltauto INSTRUMENTADO (06-16)**: verificado live que el SRP per-provincia declara `"numberOfResults"` (Madrid=1037, ≠ facet) → helper `_parse_declared_total` + acumulación per-provincia + `record_run(declared_total/captured_distinct/platform_ulid)` → **el gate B9 ya dispara en dasweltauto** (drain parcial→over-coverage→UNVERIFIED por el fix TEMA-3; 5 tests). Resta SOLO 8 family_* (agregados de sitios heterogéneos, sin total-fuente único = **N/A declarado, correcto**). El drain real (2ª pasada contando) sigue harvest-gated (spend). **Desbloquea A4-GONE** (`reconcile_gone` acoplable al gate de cobertura). |
| **SU-A4** | Delta uniforme | altas/bajas/Δprecio/Δfoto/historial en TODOS los conectores | cada conector wholesale emite NEW/GONE/PRICE/PHOTO/KM verificado en 2ª pasada; no solo AS24 | 🟡 RECON (`docs/recon/SUA4_DELTA_RECON.md`): solo AS24 emite los 5; **93% append-only (solo NEW)**; lógica completa en `ingest.py` pero solo AS24 la llama. **FASE-1 €0 ✅** (`pipeline/delta.py`, 75✓): `diff_vehicle` (helper PRICE/KM/PHOTO compartido) + `reconcile_gone` (baja por last_seen, source-scoped, idempotente) + 2 bugs `generic_dealer_site` (sold→gone, JSON). **Gate cazó fallo CATASTRÓFICO**: guarda `min_captured` no protegía corridas parciales (habría borrado ~99% inv) → **cap fracción-gone** (aborta si stale/avail >50%, inv≥20). **FASE-2**: cablear `diff_vehicle` en 43 conectores + `reconcile_gone` post-corrida + corridas espaciadas. **RECON FASE-2 (06-15): A4 ES €0-VERIFICABLE** — el landing de los conectores es SEPARABLE de la red (toma `items_by_page` en memoria, no fetch en vivo; verificado en coches_net `_land`) y YA tienen el split existing/new → cablear delta = añadir `diff_vehicle` en el touch-existing + `reconcile_gone`, unit-testeable con `items_by_page` sintético SIN correr scrape. **Plan impecable (NO todo de golpe): fásico top-volumen** — wallapop(588k)/milanuncios(397k)/coches_net(274k)/coches_com(93k)/motor_es(49k) cubren ~1,4M de ~1,5M delta-less; 1 conector→wire→test-sintético→verify→siguiente. Campaña-CORE de arranque enfocado (próxima fase de ejecución). **FASE-2 EJECUTADA (06-15) top-5 = ~95%**: helper compartido `pipeline.delta.emit_change_deltas` (DRY, agnóstico) + cableado en **coches.net(274k)+wallapop(588k)+milanuncios(397k)+coches.com(93k)+motor.es(49k)=~1,4M de ~1,5M** → emiten PRICE/KM/PHOTO_CHANGE en re-vistos + refrescan la fila servida (arregla bug stale-price). Verificado: 80+ tests, 2 live rolled-back del helper, 0 regresión (commits `9e36df9`/`68ee0e8`/`d980a68`/`4ecf25c`). **LONG-TAIL EJECUTADO (06-15) — A4 PRICE/KM/PHOTO COMPLETO en los 26 conectores con patrón** (de 1=AS24 a 26): los 21 long-tail cableados vía **workflow de 21 agentes** (1 por conector, wiring de 4 líneas + auto-verificación) + **mi verificación adversarial propia** (no confío en auto-reportes: 21/21 con import/call/existing_snap/SELECT-split-único correctos, AST+import limpios, 0 fails; 155 tests dirigidos + **SUITE COMPLETA 855 verde** (`e6f11fc`); 0 regresión; commits `b05f3f4`/`f0a22e9`. El gate de la suite cazó 2 tests brittle de Lens A [hardcodeaban conteo vivo prov-28 52668→52883 por crecimiento entity, NO regresión A4] → arreglados drift-proof). **Resta A4** (gated, no €0): (a) **GONE — CORE EJECUTADO (06-16)**: `reconcile_gone` ganó gate de cobertura `min_coverage` (aborta si coverage_pct<floor o verdict REFUTED → no retira en harvest incompleto; doble-seguro con el cap >50%) + **integración CENTRAL en `record_run`** (tras verify_coverage llama reconcile_gone con run_started_at; el emisor único de GONE/bajas, gated por 3 condiciones independientes). Provablemente backward-compat (run_started_at=None→saltado). **158+7 tests, 0 regresión.** Commits `1eef6ff`/`1ad9ea5`. **GONE COMPLETO (06-16) — mejora del método elimina la campaña de 27**: descubrí que `record_run` ya lee `source_health` FOR UPDATE → le añadí el `last_ok` PREVIO como **boundary fallback de run_started_at** (re-vistos: last_seen=now()>prior_last_ok; no-vistos desde la corrida anterior: last_seen<él). Así **GONE se auto-activa para las 34 fuentes con cobertura SIN wiring per-conector** (solo necesitan declared_total, ya hecho); 1ª-corrida (prior NULL)→skip. Probado **end-to-end** (vehículo stale retirado vía toda la cadena cobertura→boundary→reconcile→GONE) + **339 regresión, 0 fallos** (`81756d1`). **A4 "delta uniforme" FUNCIONALMENTE COMPLETO**: NEW(todos)+PRICE/KM/PHOTO(26)+GONE(auto 34). (b) 2ª-pasada en vivo verificando los deltas = harvest-gated (spend); (c) conectores fuera-de-patrón (as24/osm/family_*/acevas ya emiten; estructura distinta). |
| **SU-A5** | Receta guardada | formato bundle per-dealer | receta YAML v3 versionada por dealer en su path geo; 100% en `main`; reproducible | 🟡 RECON+€0 (`docs/recon/SUA5_RECETAS_RECON.md`): modelo 2-niveles — conector (35 YAML, cubre 98,4%) + per-dealer (550 AS24 stamps). **Cobertura PROBADA** por `v_dealer_recipe` (0029, MVCC-safe vista): **37.041 connector / 537 per_dealer / 75 none** (techo directorio). +YAML Autorola/BCA (extraídos del módulo, line-cited), ledger reconciliado (0029 hash↔archivo; 23 migs 0 malos). Gap real = **23.894 dealers sin inventario = recipe-hunting Fase-B (cosecha)**. **RECIPE-COVERAGE GAP 2026-06-16 (auditoría coherencia): `v_dealer_recipe` UNDER-reporta cobertura — 268 dealers con inventario servido marcados `recipe_kind='none'` PERO su source_key SÍ es conector** (Flexicar 186, family_* 65, rentacar_vo_* 5, aecs 7…). Root cause: el CTE `connector_source_keys` identifica conectores por anchor-nacional-heurístico que (a) **no reconoce kind='cadena'/role='chain'** (Flexicar) ni (b) los conectores SIN anchor nacional (family_*/rentacar_vo_*/aecs ~76). Fix robusto = REGISTRO de conectores (source_key→connector) en vez de la heurística + reconocer role='chain'. Vista de REPORTING (afecta G3-completion + evict-Gate2, no count/sello). **PARCIALMENTE SELLADO 06-16 (migración 0044): reconocer national `role='chain'` → 186 vo-chains (Flexicar) corregidos a 'connector'; none 268→82, connector +186, migrate verify 38/0.** Restante 82 (family_*/rentacar_vo_*/aecs SIN anchor nacional) = fix-registro-de-conectores, escalado. |
| **SU-A6** | Geo país/prov/ciudad | cerrar gap + jerarquía | gap municipio <2%; `/geo/tree` completo; comarca asignada; sin sentinel-drift | 🟡 RECON GATEADO (`docs/recon/SUA6_GEO_RECON.md`): **comarca 99,93% ✓, sentinel-drift 0 ✓, errores within-province 0 hard ✓** (FK+CHECK; 38 CP-CCAA mismatch=0,07% flagged). muni-gap servido 17,6% (6.619): **€0-resolvable solo ~131** (44 latlon + ~87 postcode); **6.601 SIN señal geo = DATA-BLOCKED** (gate<2% inalcanzable €0; necesita Overture/Geonames/API = Fase-B). 3/4 criterios GREEN; muni-gap = gap-declarado-data. **VERIFICADO 06-16: el §Deuda "backfill 131" NO es €0 — `backfill_municipality_geo.py` dry-run resuelve 0/136** (señal geo inconsistente con `province_code`: postcodes ambiguos/4-dígitos-malformados + coords a 600-700km de la provincia declarada; el gate self-verify rehúsa escribir = better-a-hole). Cierre real = corregir datos (DATA-gated Fase-B), no geocoding. €0-real ≈ 0. |
| **SU-A7** | Código único por dealer | (= SU-A1) cdp_code inmutable | átomo confirmado | 🟢 €0 CONFIRMADO (=SU-A1): cdp_code inmutable DB-enforced (`uq_entity_cdp_code` UNIQUE; minter determinista `services/api/codes.py`). Verificado vivo: **390.621 entities = 390.621 cdp distintos, 0 nulls** (1:1, cero colisión). Recetas (`_tier1`/`_platforms`/geo) + API sirven por cdp. |
| **SU-A8** | Falla→alerta→auto-repara→no cae | lazo €0 cerrado | fallo inyectado → 1 alerta origen-exacto → auto-repair €0 efectivo (refingerprint/re_receta) → API sigue; spend-gated declarado | ✅ **SELLADO** (`docs/recon/SUA8_AUTOREPAIR_RECON.md`): lazo €0 CERRADO (record_run→breaker→auto_repair→alert-origen-exacto-dedup→recovery resuelve; 5 ciclos empíricos). **Test de inyección `test_autorepair_loop.py` 8✓** (transitions, breaker@3, dedup, isolation A↛B, recovery resets+resolves) = verificación reproducible. Aislamiento real (is_open 44 scrapers → API no cae). Spend-actions `# P10-SCAFFOLD` declarado (no fakeado). +auto-resolución gone_guard (4 archivos, cierra ~28 alertas-ruido). **Auto-corrección**: insert as24_wholesale en source_health (SU-A3) era erróneo (excluido por diseño scheduler.py:243) → revertido, registry-test verde |
| **SU-A9** | API viva sirviendo | hardening + sirve canónico | sin hazard sin-LIMIT; envelope; auth; tests; sirve `v_canonical`/`v_resolved_dealer`/`v_canonical_vehicle` una vez sellados | ✅ **SELLADO** (suite **85✓**): API FastAPI sirve solo sellado. **Gate cazó 2 bugs del agente**: (1) `/health` dealers=61.551 filas-alias → `count(DISTINCT)`=42.259 (sello B1); (2) `/inventory` canonical-only GLOBAL dropeaba **102.449 coches cross-dealer** → dedup INTRA-cluster `DISTINCT ON canonical_vehicle_ulid` (verif 17.479 vs 17.453). +geo `active∧≠particular`, delta cluster-aware, +endpoints coche detalle/historial, municipio, alertas(31)/sources(47). §Deuda: investigado por muestra → **B7 NO sobre-fusiona** (coches idénticos: título+km-exacto+precio, 6/8 MISMO deep_link); raíz = **duplicación de entidades** (mismo dealer/listing como ≥2 entidades; B1/ingest no dedup) → cuestiona dealer-count 42.259 + 1 deep_link↔2 entidades. **Nuevo SU-B-DEDUP: re-gate B1/ingest entity-dedup.** No bloquea API. `/platforms` dedup sin revisar; `/health` JOIN 1.5M latencia |

### B — LA OBSESIÓN (verificar TODO)

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-B1** | Ledger de verificación profundo (0014 / V1-V6) | migración aplicada+registrada: CHECK `chk_trustworthy_needs_quorum (family_n≥2 AND origin_n≥2)` rechaza un INSERT inválido; rol `cardeep_inquisitor` read-only DB-rechaza escritura; `verdict_audit` hash-chain íntegro | ✅ **CORE** (migración **0026**, `39a9a2e`): quorum CHECK NOT-VALID (grandfather B1/β/B7), audit hash-chain append-only, `denominator_estimate`, rol inquisitor. CHECK rechaza no-quorum verificado; rebuild 0001→0026 OK; suite 416✓. **RE-VERIFICADO 06-16 (átomo, DB viva)**: hash-chain del `verdict_audit` ÍNTEGRA — **1.089 filas, 0 broken_links** (linkage `prev_hash[N]==chain_hash[N-1]`) + **0 bad_chain_hash** (recompute criptográfico `sha256(COALESCE(prev_hash,'GENESIS')||'\|'||payload_hash)`) + 1 génesis único → cero veredictos manipulados/insertados/borrados/reordenados; el sello tamper-evidence se sostiene. **Deferido**: `v_latest_verdict` materializada, gestionador, publish-gate views, V2/V3/V4. +migrate.py `split_statements` |
| **SU-B2** | Inquisición + completion (V2/V3/V4) | WF-INQUISITION en cadencia; detector V4 + state machine; entidad COMPLETED solo por 5 gates binarios | 🟢 €0-COMPLETO (resto harvest-gated declarado) (`docs/recon/SUB2_INQUISITION_RECON.md`): 5 gates = **G1-G5 de V2** (Identity/Inventory/Recipe/Served/Delta; COMPLETED⟺los-5+fresh). **Block α✓**: `0030 entity_completion` (22 cols V2-spec, trigger enforce, reproducible hash↔archivo) + `complete.py` G1-G4 (G5 stub) + **43 tests✓** + demo 20. **Decisión Director (MEJORA V2 — era inalcanzable para 97,5% connector)**: G1=province (no lat/lon=gap A6), G2=deep_link (no recipe_version=G3), G3=`v_dealer_recipe`≠none (no git-per-dealer). quorum NOT VALID. **β-refine✓** (G1=province/G2=deep_link/G3=v_dealer_recipe aplicados, 50 tests✓, demo realista — COMPLETED alcanzable, bloqueado solo por G5-corrida). **β-populate✓** (`scripts/populate_completion.py` set-based reproducible, **37.657 poblados**, idempotente 3✓, spot-check==complete.py; **37.271 COMPLETED-eligible** reales, bloqueados solo por G5-corrida; G2/G4=100%, G3=F 79 directorio). Gate corrigió mis-caract. del agente: G1=F 310 = **210 compraventa province_null (geo-gap)+97 subasta+2 plataforma+1 importador** (NO "sentinels"). **γ✓** (`0031 gestion` + `pipeline/gestionador/{detect,route}` 54✓): gestion_item/transition (V4, state machine + lanes), **7 detectores €0** (count_inflation/silent_cap/field_loss/staleness/fabrication/coverage_gap/price_trap) + 2 stubs (3.8/3.9 golden-set/scraping); demo **1.610 anomalías reales**. +fix migrate.py `strip_rollback` (bug recurrente rfind+guard, +test). **δ✓** (`verify_ttl` TTL por claim_kind + `verify.py` cableado backward-compat: veredictos nuevos llevan expires_at, grandfathered NULL=eternos; `inquisition_schedule` cadencia €0 find_expired→open_or_refresh idempotente; CLI no-op verificado expired=0/1044; 17✓): **el gate cazó un crash latente que shippeé en γ** (`str(timedelta)` como param INTERVAL revienta asyncpg en todo lane con SLA — el mockeo 100% lo ocultó; arreglado + 2 tests real-DB). **ε1✓** (`0032_inquisition`: claim/skeptic/verdict + **invariante DB `trustworthy_needs_independence`** [TRUSTWORTHY exige indep≥2∧assert≥2∧hard=0 — imposible escribir una mentira de-confianza] + FK `denom_estimate_id` auditable + cola PENDING; 26 migs; **9 tests real-DB✓**). **ε2✓** (`pipeline/inquisition/{models,independence,quorum}`, **58 tests puros✓**): gate D(s,P)≥2 + INDEP=min-pares-asserting + quórum §5.4 (6 pasos) + tolerancia EXACT/DRIFT (τ_rel=0.5%/τ_abs=50) + false-veto §5.5; **todos los ejemplos worked del spec reproducen** (§4, §5.2 AS24/coches.net, §5.6 coverage). Decisión Director: INDEP sobre-todos-asserts (lectura estricta) cuando el §4 es ambiguo — por Ley I solo puede sobre-refutar, nunca fabricar TRUSTWORTHY falso. **ε3✓** (`pipeline/inquisition/{lenses,_lens_a,_lens_d}`, **46 tests✓** [26 puros + 20 real-DB]): 5 lentes ortogonales — **A** re-query SQL (count/kind/coverage/inventory/denominator, €0 real, D=2), **D** cross-source (witnesses reales dgt_cat=1.292 desguace / wallapop / denominator P_all, €0), **E** batch-hash SHA256 (empty-delta→REFUTE_HARD determinista, €0); **B** raw-recount ABSTAIN honesto (sin raw store) + **C** live-refetch STUB cero-red (harvest-gated, D=4). Dispatcher §3.6; measured_value canónico (deuda ε2 cerrada). Gate verificó esquema real (entity_ulid/cdp_code/entity_source) + números (madrid=52.668, desguace=1.895) + corrigió matriz delta (A mandatorio, el agente lo había dropeado). **ε4✓** (`pipeline/inquisition/{prosecutor,router}` + 9 tests✓): prosecutor **ATÓMICO** (poll PENDING→lentes→decide()→persist skeptic/verdict→DECIDED, todo en 1 transacción) + manager router §7 (13 filas reason_code→lane, reusa γ `open_or_refresh` + tabla `alert`); CLI smoke real=0 PENDING. **Gate (Opus) cazó 3 defectos de raíz**: (1) prosecute_claim NO-atómico con docstring que mentía sobre SAVEPOINTs→envuelto en transacción real (en crash el claim revierte a PENDING, sin zombie PROSECUTING); (2) `regime_for` omitía entity_field/delta (2 de 7 subject_types válidos)→añadidos; (3) test_all_router_rows vacuo (1 de 13 filas por bug rollback-en-bucle)→savepoint por-fila + assert tested==13. **V3 Inquisición COMPLETA a techo €0** (ε1 schema+invariante DB / ε2 motores / ε3 lentes / ε4 prosecutor+router; **139 tests inquisition✓**). **B2 restante = harvest-gated**: G5 (2ª corrida), Lens C (live re-fetch + egress separado), emisión de claims sobre los 1.044 verdicts VAM. §Deuda: Lens A delta-handler, entity_field B/C/D, supersesión post-RESOLVED. §Deuda: **G1 national-entity + 2 plataforma CERRADO** (`check_g1` + `populate_completion` SQL: kinds nacionales subasta/plataforma/oem_vo_portal/importador con province NULL pasan G1 — el '00' vive solo en el cdp_code; **100 flipeadas g1 F→T, g1_false 310→210**; +2 tests); 210 compraventa sin-provincia = gap-geo SU-A6 genuino (sigue F, correcto); **price_trap floor-particulares EVALUADO sin-defecto** (releído `detect_price_trap`: la banda-mensual [49,999] NO marca sola — exige `AND ratio_outlier` <5% mediana = conservadora; el floor<300 captura precios mayormente simbólicos [€0-49=8.684 reales anomalías] y va a RESEARCH+quarantine NO-destructivo; tuning del floor = juicio harvest-review, no ciego — no se toca código tested sin defecto confirmado); supersesión post-RESOLVED + egress CHECK lente-C = harvest-gated |
| **SU-B3** | Confesar gaps | UNVERIFIED/REFUTED/QUARANTINED first-class servidos etiquetados o retenidos | ✅ doctrina (re-confirmar en VERIFY) |

### C — TIER-1 + ARSENAL

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-C1** | P0.5 anti-detección spike | re-prueba 5 OPEN + 2 walled targets; ClientHello byte-diff vs Chrome actual; Wallapop firma + Adevinta token resueltos → `state/tier1-blocked.json` | ⬜ |
| **SU-C2** | Cazar receta de cada Tier-1 | cada Tier-1: receta reproducible en `platforms/_tier1/<n>/` + 2-way count + field-VAM, O muro declarado | 🟢 **RECETAS HECHAS €0** (corrección 06-15: era ⬜ stale — workflow verificación A→F lo cazó): los 7 Tier-1 (spoticar/coches.net/autocasion/motor.es/coches.com/wallapop/milanuncios) tienen receta reproducible + 2-way count VERIFICADO **libre** (`docs/architecture/tier1_recipes/README.md` 06-12 + dossiers per-plataforma + 14 CDP en `countries/ES/_tier1/`). Ninguno es muro a €0. **Restante = harvest** (correr los conectores a escala = SU-A3 drains, spend-gated), no recipe-hunting. |
| **SU-C3** | Sellar B7 (dedup coches) | fix 0km; gate cero-sobre-fusión; `vehicle-identity-det-v1` vam_verified=TRUE; `v_canonical_vehicle` sirve | 🟢 **SERVIDO + sample/guard-verificado; verdict VAM UNVERIFIED** (corrección honesta 06-15 — workflow A→F cazó sobre-afirmación "SELLADO"): 4 guardas (km=0/VIN, photo K=12, firma non-null-price, firma cross-entity), Giants 89→9, **1.486.285 coches únicos** servidos vía `v_canonical_vehicle` (cluster_run vam_verified=TRUE). **PERO verdict 1102 = UNVERIFIED (quorum 0/0/0)**: B7 es dedup MONO-MÉTODO → no existe un 2º clustering independiente para un quórum-de-conteo → no puede ser TRUSTWORTHY sin fabricar evidencia (prohibido). Excepción DECLARADA, no defecto: servido pragmático + verificado-por-muestra; el sello-VAM-quórum es inalcanzable para un dedup de método único. Residuo 9 cross-entity (0,015%)+292 cross-province declarados. Suite 416✓. **HALLAZGO 2026-06-16 (auditoría coherencia servido): deep_link NO es señal de identidad en B7** → **11.930 listados (misma URL exacta) servidos como ≥2 coches canónicos distintos** (0,7% servido, customer-facing — verificado inequívoco: un MINI Cabrio misma-URL/km-148000/precio-€9000 → 2 canónicos; un Honda Civic misma-URL con Δprecio €7500→€7950 → 2 canónicos). De 139.708 grupos dup-deep_link, 127.778 (91,5%) SÍ colapsan; 11.930 NO. **Fix de dirección CLARA y determinista** (misma URL = mismo listado = mismo coche, no probabilístico): B7 debe tratar `deep_link` idéntico como arista hard-same-car (colapsar), O un override determinista sobre `v_canonical_vehicle` (vista). **NO hackeado a esta profundidad**: `v_canonical_vehicle` (vista core) sostiene conteo servido 1,486M + numerador del sello + API; reescribir su definición mal corromperia los tres (mentira mayor que el 0,7%). Escalado a unidad enfocada con regresión completa (Law I: corrección vence sobre velocidad). |

### D — COSTE / LLM (€0, hardware-bound)

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-D1** | LLM local para lo masivo | pipeline Ollama (qwen3:4b) clasifica/parsea/normaliza dentro del hardware sin ahogarlo; determinista donde regla basta; benchmark t/s registrado | 🟡 €0 EVALUADO (hardware-gated, declarado con causa): Ollama instalado + 3 modelos (qwen2.5:3b 1.9GB / qwen3:4b 2.5GB / qwen3:8b 5.2GB). **PERO solo 2.11GB RAM libre** (15.3GB total; ~13 en uso OS+Docker: cardex-pg 1.6GB [otro proyecto], cardeep-pg 0.2GB) y **sin CUDA** (Radeon iGPU → CPU-only). Correr incluso qwen2.5:3b (~2.5-3GB inferencia) EXCEDE la RAM libre → swap-thrash → **ahogaría el pipeline vivo** (viola "sin ahogarlo"). **Decisión Director**: LLM local DIFERIDO a ventanas pipeline-idle / fase harvest (modelo=qwen2.5:3b, el menor); a €0 clasificación/parseo/dedup las cubren los DETERMINISTAS ya construidos (7 detectores gestionador + regex + lentes Inquisición + kind-classifier) = "determinista donde regla basta". **NO se corrió benchmark**: riesgo de ahogar la DB viva > valor de un t/s para herramienta sin consumidor €0. |
| **SU-D2** | Eficiente y blindado | rate-limit + cache en API; pacing conductual para walled; governor verificado anti-cicatriz | 🟢 €0 SELLADO (gap de seguridad cerrado): API **rate-limit** (`services/api/ratelimit.py`, slowapi in-memory — SIN Redis: 120/min default, 30/min costosos, 300/min health; gate env `CARDEEP_API_RATELIMIT_ENABLED`; 429 con envelope `{ok,data,error,meta}`) + **cache TTL** (`services/api/cache.py`, cachetools 60s/512-LRU bounded; 6 endpoints estables [inventory×2 + geo completeness/entities/muni/tree], `meta.cache`=hit/miss; **NO cachea vivo**: delta/health/alerts/sources/vehicles/entity-agregado → cero stale). Gate Opus: diff **aditivo behavior-preserving** (+174/-17, no reescritura pese al wording del agente); caching correctamente scoped (verificado opt-in por handler); import muerto en ops.py eliminado. Governor anti-cicatriz ya battle-tested 25/25 (runbook §7.1). 13 tests + 103 sweep api✓. |

### E — HUELLA + ORGANIZACIÓN

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-E1** | Todo a `main` documentado | (post SU-0.3) árbol limpio; recetas/estado/decisiones commiteados; runbook A-Z | 🟢 €0 (árbol LIMPIO, todo en main): **verification stack documentado A-Z** (`docs/architecture/10-VERIFICATION-STACK.md`: L1 VAM 0004→L2 deep ledger 0026→L3 gestionador 0031→L4 Inquisición V3 0032; lazo claim→lentes→quórum→router; frontera €0/harvest + deuda) + RUNBOOK de-staled (§7.4 VAM=L1+puntero, §7.7 0019→0032). Harvest-runbook (45 unidades) vigente 2026-06-13. La pieza que faltaba (maquinaria de verificación) ya documentada. |
| **SU-E2** | Separación física Tier-1 + reshape geo (B6.1) | `git mv` a `countries/ES/<prov>/<comarca>/<city>/dealers/<cdp>/` + `platforms/_tier1/`; count(after)==count(before); CI estructural verde | 🟢 €0 SELLADO: `scripts/reshape_recipes_geo.py` (DB-driven, count-preserving, idempotente) movió **580 recetas CDP** vía `git mv` (historia preservada) → `countries/ES/<prov>/<comarca-slug>/<muni-slug>/dealers/<cdp>/recipe.yaml` (543 dealers geo) + `_tier1/<cdp>/` (**14 defensa-dura**: 7 marketplaces incl. AS24 + 7 OEM t1_soft) + `_platforms/<group>/<cdp>/` (23 nacionales por grupo). **count(after)==count(before)=580** (+7 family templates intactos = 587); **G3 loader `complete.py` glob-based geo-reorg-stable** (legacy fallback, git-committed check preservado); **31+81 tests✓**, loader resuelve recetas reales en árbol nuevo (verificado vivo). Mejora Director validada: Tier-1=`is_tier1` (defensas duras, no source_group-puro). Módulos Python NO tocados (sellados). §Deuda: 18 geo-dealers `_sin-comarca`; 7 family templates en `recipes/`. |

### F — MÉTODO (los poderes)

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-F1** | Workflows de OPS continua | orquestación scheduler-driven del E2E per-dealer (no solo build); idempotente; XAUTOCLAIM recovery | 🟢 €0 SELLADO (recovery por método superior a XAUTOCLAIM): scheduler durable YA existía (`pipeline/ops/scheduler.py` B2.2 — APScheduler + SQLAlchemyJobStore en cardeep-pg = **crash-safe sobrevive-muerte-proceso+reanuda**; single-producer breaker-aware + silence_watchdog B2.4). cardeep **NO usa Redis** → recovery vía jobstore-PG, no XAUTOCLAIM (sin infra Redis; objetivo logrado por mejor vía). **Incremento €0**: cableé la cadencia δ como job recurrente del scheduler (`inquisition_cadence_job`, cada 6h, max_instances=1/coalesce, `_ASYNCPG_DSN` dedicado) → re-verificación de veredictos CONTINUA junto a heartbeat(15min)+watchdog(1h). Verificado: import OK + job end-to-end (expired=0, sin raise) + **46 tests ops✓**. Orquestación E2E-harvest (correr conectores) queda harvest-gated. |
| **SU-F2** | Integrar herramientas (free+viable) | instalar las specified-not-installed que rinden en este hardware (selectolax, libpostal, extruct…); descartar las que exigen GPU/gasto, declarado | 🟢 €0 EVALUADO (anti-YAGNI, descartado con causa): parsing actual = **lxml+bs4** (instalados, suficientes, usados por ~15 conectores). **selectolax** (perf) DIFERIDO — el bottleneck a €0 es governor/red, no parsing; adoptar solo si se mide. **extruct** (JSON-LD/microdata) EARMARKED para activación de Lens B (raw-recount, harvest-gated) — instalar cuando exista raw store, no antes. **libpostal/postal** DESCARTADO en Windows (sin wheel; exige build C+CMake+MSVC + ~2GB datos; marginal a €0). Ninguna paga su coste de mantenimiento sin consumidor vivo → cero instalado por diseño. |
| **SU-F3** | Agotar alternativas | ceilings solo tras probar, declarados con causa | ✅ doctrina (re-confirmar) |

### GAPS ROJOS — DESARROLLAR

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-R1** | Desguace E2E (numerador) | workflow E2E desguace (1.292 CATs, Opisto/own-site); inventario >0 con VAM; ≥1 provincia sellada en desguace | ⬜ RECON: 1.895 desguaces (1.292 DGT+603), 283 con web, **0 inventario**. Greenfield (sin receta). Fuente=Opisto/own-sites. NOTA Director: inventario desguace=despiece/scrap (valor consumidor < venta); rendimiento limitado por techo schema.org ~1,5%. Frontera del numerador €0. |
| **SU-R2** | Concesionario harvest | cosecha FACONAUTO más allá de OEM-VO; servido sube de 11,6% con VAM | ⬜ |
| **SU-R3** | Filtrado sells_cars (sin ruido) | `sells_cars` resuelto en 100% de `kind=garaje`; ruido fuera; particular/POS coherente | 🟡 **€0-sliver hecho** (06-15): 6 garajes CON inventario → `sells_cars=true` determinista (verificado 0-sin-inventario). Los **7.195 sin inventario = ambiguos DATA-gated** (necesitan labels externos/plataforma; "mejor hueco que mentira" — no se marcan a ciegas). 100%-resuelto inalcanzable a €0. |
| **SU-R4** | Cobertura 100% + cierre | cada segmento sellado o gap-con-causa; Canarias/Ceuta/Melilla cerrados | 🟡 **DISCOVERY VERIFICADO 06-16, SELLO data-gated**: los segmentos NO están vacíos — Las Palmas (35) **791 dealers/27.007 coches**, Tenerife (38) **757/22.363**, Ceuta (51) **28/359**, Melilla (52) **17/1.020** (medido en DB viva; Canarias robusta, Ceuta/Melilla coherentes con su tamaño diminuto). El **discovery está hecho**; lo que falta es el SELLO (denominador medido por provincia): `denominator_estimate` tiene **solo 1 fila** (floor nacional 38.555), sin breakdown CNAE-451 per-provincia. Cerrar R4 = cargar el denominador fiscal per-provincia (DIRCE/INE) = la **misma data-task diferida de A2-φ**; hacerla mal = denominador falso (mejor-hueco-que-mentira) → fresh-context. No es "⬜ sin tratar": discovery medido, gate preciso identificado. |

### TERMINAL

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-SEAL** | SPAIN-SEALED 52/52 (B6) | por provincia: denominador medido + numerador VAM-estable + vehicle-recall; Ceuta/Melilla direct-census; residuales itemizados; API sirve solo TRUSTWORTHY | 🟡 **ASSESS (gate Director)**: F8 VÁLIDO (DB fresca, overlays+AS24 incorporados). **Sello=DEDUP** (raw 50/52=artefacto cross-portal; honesto **19/52 ≥85% + 88% nacional**). **CAPA A firmable €0** (gap-irreducible): venta 88% nac + desguace discovery 52/52 LIMPIO + conc 11,6% (FACONAUTO inflado) + desguace-inv=GAP-ESTRUCTURAL + C2C fuera-modelo. **CAPA B=roadmap deferido** (NO sellar-alrededor): Overture E2E ~2-3sem, OEM ~sem/marca, Ceuta/Melilla censo. **52/52-PLENO no €0 hoy.** **SELLO PERSISTIDO LIVE 06-16** (migración **0042** `v_province_seal`): denominador per-provincia (52 filas `denominator_estimate segment='venta'`) + numerador canónico vivo (`COUNT(DISTINCT COALESCE(v_dealer_resolved.resolved_ulid,entity_ulid))`, kinds venta con inventario) → cobertura → SELLADO≥85/PARCIAL/GAP, **siempre current sin snapshot stale**. Distribución viva: **13 SELLADO / 30 PARCIAL / 9 GAP, cob nac 79,4%** (servida-canónica; la verificación cazó que entity-level sobre-cuenta 165%). 6 tests. **DESGUACE añadido 06-16** (migración **0043**, UNION multi-segmento): sello DISCOVERY (hallados/censo-DGT; numerador todos los desguaces, denominador `source_key='dgt_cat'`; SELLADO si hallados≥censo) = **52/52 SELLADO** (validado exacto vs snapshot: Madrid 48/98, Barcelona 76/116; nac 1.895/1.292). **API la sirve** (`GET /geo/seal`, migración API, devuelve `{segments:{venta,desguace}}`, 4 endpoint-tests). **CONCESIONARIO evaluado-y-NO-añadido** (juicio Director): su denominador FACONAUTO×población es estimado-proxy crudo (vs CNAE-451 riguroso de venta) Y los concesionarios YA están en el numerador venta → añadir sello denominador-débil junto a uno riguroso induce a error; se omite por honestidad. **Mecanismo €0 del sello (venta+desguace) COMPLETO + SERVIDO**; subir SELLADO-venta = numerador↑ harvest (gated) + Capa-B (Overture/OEM, data/spend). |

---

## 5. Orden de ejecución (DAG — respeta dependencias)

```
FASE 0 (cimiento)  SU-0.1 → SU-0.2 → SU-0.3 → SU-0.4 → SU-0.5 → SU-0.6
   │  (árbol limpio, ledger reproducible, sellos linkados, ontología sana, disco con margen)
   ▼
SU-B1 (deep verification 0014)   ← se construye PRONTO: todo sella honestamente a través de él
   ▼
A: SU-A1 → SU-A2(β→φ→Chao2) → SU-A3 → SU-A4 → SU-A5 → SU-A6 → SU-A8 → SU-A9
   │  (∥ donde tocan hosts/ficheros distintos)
   ├─ C: SU-C1 → SU-C2 → SU-C3
   ├─ D: SU-D1 → SU-D2
   ├─ R: SU-R1 → SU-R2 → SU-R3 → SU-R4
   ▼
B: SU-B2   ·   E: SU-E1 → SU-E2   ·   F: SU-F1 → SU-F2
   ▼
SU-SEAL (52/52)  ← scoreboard rodante: cada provincia sella cuando sus celdas pasan
```

**Concurrencia:** donde dos SU tocan hosts/ficheros distintos corren en paralelo (ley de rate-limit).
En este hardware débil, la concurrencia es de **razonamiento de agentes**, no de procesos pesados.

## 6. Doctrina de verificación (VAM por SU)

- Cada número por **≥2 caminos ortogonales**, uno = conteo aterrizado en DB.
- El que produce un número es sospechoso → lo confirma OTRO por vía distinta.
- Sello (`vam_verified=TRUE`) **solo tras gate manual de muestra** (yo, Opus) + verdict linkado.
- Sobre-cobertura también REFUTED. Default refutado si no reproducible.
- "Sellado" ⇒ denominador (legal donde exista, estimado-declarado donde no) + numerador VAM-estable + cada gap confesado con causa.

## 7. Skills / agentes / herramientas por tipo de SU (stocktake)

| Tipo de trabajo | Agentes | Skills | Herramientas |
|---|---|---|---|
| Migración/schema | database-reviewer, go/py builders | postgres-patterns, database-migrations | psql, migrate.py |
| Identidad/dedup | python-reviewer, code builders | regex-vs-llm-structured-text | union-find determinista, RapidFuzz, Ollama (slice) |
| Scraping/Tier-1 | cardex-scraper | python-scraper, search-first | curl_cffi, camoufox, browserforge, selectolax |
| Verificación | code-reviewer, silent-failure-hunter, adversarial | systematic-debugging, verification-loop | VAM, pytest |
| Geo | database-reviewer | postgres-patterns | Nominatim, Shapely, H3, cube+earthdistance |
| Orquestación/OPS | architect | autonomous-loops | APScheduler, Redis Streams |
| LLM local | — | foundation-models-on-device, cost-aware-llm-pipeline | Ollama qwen3:4b |

## 8. Riesgos vivos (gestión activa)

- **Disco 20GB** → evicción + vigilancia continua. Bloquea ingesta masiva si no se gestiona.
- **RAM 2GB libres** → no apilar procesos; preferir qwen3:4b; liberar CARDEX si dormido.
- **Untracked load-bearing** (B7) → SU-0.3 lo cierra antes de construir encima.
- **Deep verification ausente** (0014) → SU-B1 lo construye antes de sellar masivamente.

## 9. Protocolo de no-parada / retoma (HANDS OFF)

Al retomar (sesión nueva / contexto compactado):
1. Leer `docs/SUPERPLAN.md` (este) + `docs/PROGRESO.md` (log vivo) + `git log -12` + counts DB.
2. Identificar la SU activa (primer ⬜/🔵 del DAG §5).
3. Ejecutar su WF: RECON → BUILD → VERIFY → SEAL. Actualizar el estado de la SU aquí + PROGRESO.
4. **Nunca parar** con una SU a medias sin bloqueo real declarado. No pasar a la siguiente sin SEAL.

> **Estado [reconciliado 2026-06-15, cont.]:** este puntero §9 se había quedado stale; **`docs/PROGRESO.md` es el log vivo más actual** (avanzó más allá de este tracker). Reconciliación verificada por git log + `migrate verify` (migraciones aplicadas hasta **0040**, 34 match / 0 drift):
> - **FASE 0 + identidad + deep-ledger SELLADOS**: SU-B1 (ledger de verificación profundo) se construyó como **migración 0026** (`verification_deep` — verdict_audit hash-chain + quorum CHECK), NO como 0014. La nota de deuda de abajo que decía "0014 NO construido" quedó OBSOLETA.
> - **Auditoría P2 (workflow 48 agentes, 37 findings)**: 24 sellados (10 CRÍT + 6 ALTO + 4 MED + 4 LOW) + 3 ALTO-identidad decididos vía **ADR 11** (`docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md`).
> - **Campaign de 4 features vetados** (workflow 9 agentes → `docs/architecture/feature-designs/`): scheduler_source_expansion, canonical_key (cdp_pair + backfill auto-verificante + **forward-coverage como job de cadencia**), inquisition_wiring (prosecutor cableado), price_trap v2 (cohort robust-z, QUARANTINE-only, 347 HIGH / 18.808 LOW validados, migración 0040). Todos construidos + verificados + commiteados + INERTES-hasta-deploy.
> - **Deploy-readiness**: `docs/RUNBOOK.md` actualizado A-Z (los 6 jobs del scheduler, price_trap con gate dry-run + work_mem, prosecución, forward-coverage, flujo de migraciones).
> - **Frontera €0-autónoma agotada.** Restante = (a) certificación de merges de identidad (3 ALTO, ADR 11 — alto riesgo, exige review per-merge riguroso); (b) **harvest/spend/hardware-gated** (la fase que el Owner abre tras validar config A-Z). Siguiente paso real cae en el gate de spend/deploy.
>
> ## Deuda declarada + hallazgos de auditoría (tracked, no bloqueante)
> - **evict.py / evicción de crudo**: diseñada (MISSION §6, MASTER_PLAN) pero no construida. data/ = 161MB hoy (baja urgencia). Owner: compactar VHD WSL2 en ventana de mantenimiento (~21GB host).
> - **AS24 kind mis-class [SU-A1] — ✅ HECHO** (commit `aa68fc7`): root-cause `ingest.py` default `concesionario_oficial`→`compraventa`+`kind_source='platform_label'`; backfill 469 (`scripts/reclassify_as24_kind.py`, idempotente). Segmento concesionario 2.058→**1.589**, oem_* intactos (1.525), AS24-concesionario=**0**. ~10% posibles oficiales genuinos marcados low-conf → el clasificador/OEM-locator los re-eleva (under-claim → re-certificar).
> - **Geocoding sucio del scraper [SU-A2/A6]**: `municipality_code` erróneo en algunas fuentes (ej AutosMadrid Alcorcón con muni de Leganés). Corrompe constraints geo. Causa del residuo multimuni de β. → SU-A6.
> - **1.629 clusters β same-muni multi-nombre**: clase ambigua (multi-marca / nombres históricos / wholesaler relistando). Decisión arquitectural pendiente del Director.
> - **Cadena abreviada sin org_id [β residuo micro]**: OcasionPlus «A./P./S.» (ciudad abreviada no-INE-matchable, sin domain) escapa los guards. Fix: extender org-link por patrón de nombre.
> - **Deep verification ledger (SU-B1) — ✅ CONSTRUIDO como migración 0026** (`verification_deep`, no 0014): verdict_audit hash-chain (`cdp_audit_append`), `chk_trustworthy_needs_quorum` CHECK (VALIDATED este turno) + columnas GENERATED `quorum_n`/`family_n`/`origin_n`. Esta sesión: 1.039 filas de cadena backfilled (`backfill_audit_chain.py`, 0 bad_chain) + 987 verdicts grandfathered reformados a array/quorum (`reform_grandfathered_verdicts.py`, 994 TRUSTWORTHY 0-sin-quorum). `denominator_estimate` (F3 Chao2) vive aquí. [nota original "0014 NO construido" era stale.]
