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
| **SU-0.5** | Corregir ontología cadena | `SELECT count(*) FROM entity WHERE kind='cadena'` = 0 (reasignadas a organization) | ✅ 0 cadena, 4 orgs, Flexicar rollup 23874 |
| **SU-0.6** | Auditoría de disco + evicción | disco con ≥15% libre; política de evicción configurada + verificada; infra CARDEX evaluada | ✅* 21,4GB Docker reclamados; host 96%=datos ajenos+VHD WSL2 (Cardeep=307MB); evict.py=debt (data/ 161MB, baja urgencia); 15% infeasible sin acción Owner |

### A — EL PRODUCTO

| SU | Punto | Definición | GATE | Estado |
|---|---|---|---|---|
| **SU-A1** | Código único (B1) | confirmar átomo + mejorar | dup<0,1% por ≥2 vías sobre datos vivos; `v_canonical` íntegra; verdict linkado (SU-0.4) | ⬜ |
| **SU-A2** | Descubrir — denominador P | arco β→φ→Chao2 | β sellado (guarda cadenas + B1∘β, gate cero-sobre-fusión); φ con DIRCE; Chao2 ortogonal + cierre saturación; N̂(P) con CI membership-filtered | ⬜ |
| **SU-A3** | Scrapear TODO el stock | exhaustividad universal | B9 coverage gate corrido en **47/47** fuentes; cada drain `Σleaf==declared` o causa; AS24/milanuncios REFUTED resueltos | ⬜ |
| **SU-A4** | Delta uniforme | altas/bajas/Δprecio/Δfoto/historial en TODOS los conectores | cada conector wholesale emite NEW/GONE/PRICE/PHOTO/KM verificado en 2ª pasada; no solo AS24 | ⬜ |
| **SU-A5** | Receta guardada | formato bundle per-dealer | receta YAML v3 versionada por dealer en su path geo; 100% en `main`; reproducible | ⬜ |
| **SU-A6** | Geo país/prov/ciudad | cerrar gap + jerarquía | gap municipio <2%; `/geo/tree` completo; comarca asignada; sin sentinel-drift | ⬜ |
| **SU-A7** | Código único por dealer | (= SU-A1) cdp_code inmutable | átomo confirmado | ⬜ |
| **SU-A8** | Falla→alerta→auto-repara→no cae | lazo €0 cerrado | fallo inyectado → 1 alerta origen-exacto → auto-repair €0 efectivo (refingerprint/re_receta) → API sigue; spend-gated declarado | ⬜ |
| **SU-A9** | API viva sirviendo | hardening + sirve canónico | sin hazard sin-LIMIT; envelope; auth; tests; sirve `v_canonical`/`v_resolved_dealer`/`v_canonical_vehicle` una vez sellados | ⬜ |

### B — LA OBSESIÓN (verificar TODO)

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-B1** | Ledger de verificación profundo (0014 / V1-V6) | migración 0014 aplicada+registrada: CHECK `chk_trustworthy_needs_quorum (family_n≥2 AND origin_n≥2)` rechaza un INSERT inválido; rol `cardeep_inquisitor` read-only DB-rechaza escritura; `verdict_audit` hash-chain íntegro; `v_latest_verdict` materializada | ⬜ |
| **SU-B2** | Inquisición + completion (V2/V3/V4) | WF-INQUISITION en cadencia; detector V4 + state machine; entidad COMPLETED solo por 5 gates binarios | ⬜ |
| **SU-B3** | Confesar gaps | UNVERIFIED/REFUTED/QUARANTINED first-class servidos etiquetados o retenidos | ✅ doctrina (re-confirmar en VERIFY) |

### C — TIER-1 + ARSENAL

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-C1** | P0.5 anti-detección spike | re-prueba 5 OPEN + 2 walled targets; ClientHello byte-diff vs Chrome actual; Wallapop firma + Adevinta token resueltos → `state/tier1-blocked.json` | ⬜ |
| **SU-C2** | Cazar receta de cada Tier-1 | cada Tier-1: receta reproducible en `platforms/_tier1/<n>/` + 2-way count + field-VAM, O muro declarado | ⬜ |
| **SU-C3** | Sellar B7 (dedup coches) | fix 0km; gate cero-sobre-fusión; `vehicle-identity-det-v1` vam_verified=TRUE; `v_canonical_vehicle` sirve | ⬜ |

### D — COSTE / LLM (€0, hardware-bound)

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-D1** | LLM local para lo masivo | pipeline Ollama (qwen3:4b) clasifica/parsea/normaliza dentro del hardware sin ahogarlo; determinista donde regla basta; benchmark t/s registrado | ⬜ |
| **SU-D2** | Eficiente y blindado | rate-limit + cache en API; pacing conductual para walled; governor verificado anti-cicatriz | ⬜ |

### E — HUELLA + ORGANIZACIÓN

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-E1** | Todo a `main` documentado | (post SU-0.3) árbol limpio; recetas/estado/decisiones commiteados; runbook A-Z | ⬜ |
| **SU-E2** | Separación física Tier-1 + reshape geo (B6.1) | `git mv` a `countries/ES/<prov>/<comarca>/<city>/dealers/<cdp>/` + `platforms/_tier1/`; count(after)==count(before); CI estructural verde | ⬜ |

### F — MÉTODO (los poderes)

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-F1** | Workflows de OPS continua | orquestación scheduler-driven del E2E per-dealer (no solo build); idempotente; XAUTOCLAIM recovery | ⬜ |
| **SU-F2** | Integrar herramientas (free+viable) | instalar las specified-not-installed que rinden en este hardware (selectolax, libpostal, extruct…); descartar las que exigen GPU/gasto, declarado | ⬜ |
| **SU-F3** | Agotar alternativas | ceilings solo tras probar, declarados con causa | ✅ doctrina (re-confirmar) |

### GAPS ROJOS — DESARROLLAR

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-R1** | Desguace E2E (numerador) | workflow E2E desguace (1.292 CATs, Opisto/own-site); inventario >0 con VAM; ≥1 provincia sellada en desguace | ⬜ |
| **SU-R2** | Concesionario harvest | cosecha FACONAUTO más allá de OEM-VO; servido sube de 11,6% con VAM | ⬜ |
| **SU-R3** | Filtrado sells_cars (sin ruido) | `sells_cars` resuelto en 100% de `kind=garaje`; ruido fuera; particular/POS coherente | ⬜ |
| **SU-R4** | Cobertura 100% + cierre | cada segmento sellado o gap-con-causa; Canarias/Ceuta/Melilla cerrados | ⬜ |

### TERMINAL

| SU | Definición | GATE | Estado |
|---|---|---|---|
| **SU-SEAL** | SPAIN-SEALED 52/52 (B6) | por provincia: denominador medido + numerador VAM-estable + vehicle-recall; Ceuta/Melilla direct-census; residuales itemizados; API sirve solo TRUSTWORTHY | ⬜ |

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

> Estado: **2026-06-15. FASE 0 SELLADA** (SU-0.1..0.6 ✅; residual de disco confesado, *=con causa). Árbol limpio salvo este tracker. Siguiente: **FASE 1** (confirmar puntos verdes a nivel átomo) → **SU-B1** (ledger de verificación profundo, migración 0014).
>
> ## Deuda declarada (tracked, no bloqueante)
> - **evict.py / evicción de crudo**: diseñada (MISSION §6, MASTER_PLAN) pero no construida. data/ = 161MB hoy (baja urgencia). Construir cuando el harvest escale. Owner: compactar VHD WSL2 en ventana de mantenimiento para recuperar ~21GB de host.
