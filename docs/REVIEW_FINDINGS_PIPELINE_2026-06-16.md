# Green-review de la capa pipeline — triage verificado (2026-06-16)

Segundo barrido adversarial (workflow `wyvlo4ikx`, 7 revisores especialistas) sobre la capa
compartida: ingest / complete / recipe / geo / discover / price_sanity / harvest_dealer.
**19 hallazgos: 2 CRITICAL, 12 HIGH, 5 MEDIUM.** Mucho más productivo que el del núcleo (este
con evidencia de DB viva). Cada uno se verifica a mano antes de tocar.

## CRITICAL (2)

| # | Ubicación | Veredicto | Estado |
|---|---|---|---|
| P1 | `ingest.py:105` + `delta.py:279` NULL→valid price/km descartado | **REAL — confirmado código + DB viva** (12.128 available price NULL, 53.729 km NULL, 2.712 con NEW.price pero DB NULL). El guard `row["price"] is not None` corta la promoción → precio/km **nunca se rellena**. SISTÉMICO: ingest.py (AS24/own-site) Y diff_vehicle (26 wholesale). | ✅ FIJADO (guard `(row is None OR …)` en ambos + old_value null-safe) + tests |
| P2 | `harvest_dealer.py:30` scrape exception → sin record DB | **REAL probable** (silent failure: excepción no capturada → sin harvest_run/health/alert). Mismo class que H7. | ⏳ PENDIENTE (verificar wiring + try/except + record_run) |

## HIGH (12)

| # | Ubicación | Veredicto | Estado |
|---|---|---|---|
| Q1 | `ingest.py:106-120` múltiples UPDATEs/vehículo (churn MVCC) | **REAL** — 3 UPDATE separados + last_seen unconditional = varias tuplas muertas (statements separados sobre la misma fila — NO el falso positivo del núcleo). | ✅ FIJADO (UN UPDATE fusionado, live: `UPDATE 1`) |
| Q2 | `ingest.py:105` junk→keep-old silencioso | **JUICIO** — mantener el último precio válido ante junk transitorio es defendible (set-NULL borraría buen dato). No bug claro. | tracked (diseño conservador) |
| Q3 | `complete.py:418` check_g4 INNER vs LEFT JOIN | **REAL probable** — INNER JOIN da served_count=0 para 184 entities servidas fuera del cluster vam; `populate_completion.py` usa LEFT+COALESCE (correcto) → G4 corrupto. | ⏳ PENDIENTE (verificar + LEFT JOIN) |
| Q4 | `recipe.py:36` `_yaml_dump` YAML inválido con `': '` | **REAL probable** (agente reprodujo con yaml.safe_load; 3 recetas facet rotas). | ⏳ PENDIENTE (verificar + `yaml.dump`) |
| Q5 | `geo.py:141` `_index_prov` sin guarda min-length | **REAL probable** — provincia loader guarda artículos ('la','las','a') como keys ('Rioja, La'→'la'='26'); el muni loader SÍ tiene la guarda (asimetría). Consecuencia irreversible (cdp_code). | ⏳ PENDIENTE (verificar + guarda `len>=4`) |
| Q6 | `discover.py:78` fetch entity_ulid no-atómico (carrera) | **REAL probable** — INSERT…RETURNING (xmax=0) + SELECT separado → None → NOT NULL violation → aborta el resto. Fix limpio: `RETURNING entity_ulid`. | ⏳ PENDIENTE (verificar + fix) |
| Q7 | `discover.py:109` in_db acumulativo (VAM quorum) | **REAL probable** — cuenta todo entity_source histórico, no este run → enmascara drops → TRUSTWORTHY falso. | ⏳ PENDIENTE (verificar + scope `seen_at>=run_start`) |
| Q8 | `delta.py:391` emit_change_deltas sin sanitize_price | **REAL** (mi código) — junk price podría escribirse (no hay junk hoy; path sin sanitización). | ⏳ PENDIENTE (sanitizar antes de diff) |
| Q9 | `harvest_dealer.py:49` ingest-error print-only | **REAL** (silent failure, mismo cluster que P2). | ⏳ PENDIENTE (con P2) |
| Q10 | `autoscout24.py:257` collect_dealer_slugs traga excepciones | **REAL probable** — `except: break` trunca discovery silenciosamente. | ⏳ PENDIENTE (verificar + log/raise) |

## MEDIUM (5)

| # | Ubicación | Veredicto | Estado |
|---|---|---|---|
| R1 | `ingest.py:67` / `discover.py:79` source_ref no actualizado en conflict | **REAL** (ID externo congelado) | ⏳ PENDIENTE (`source_ref=EXCLUDED.source_ref`) |
| R2 | `recipe.py:54` write_recipe sin validación | **REAL** (gap — receta malformada pasa G3) | ⏳ PENDIENTE (con Q4) |
| R3 | `recipe.py:59` write_recipe last-writer-wins clobber | **REAL** (incidente documentado coches.net) | ⏳ PENDIENTE (guard de contenido) |
| R4 | `discover.py:104` skipped entities sin traza per-entity | **REAL** (observabilidad) | ⏳ PENDIENTE (log estructurado) |

## Orden de ejecución — PROGRESO

**FIJADOS + TESTEADOS + PUSHEADOS (7 hallazgos, 3 commits, cada uno verificado a mano + live):**
- `9818a9b` **P1 + Q1** (ingest+delta): NULL→valid price/km fill en AMBOS write-paths + UPDATE
  fusionado (1 tupla). Live: 12.128/53.729 NULL candidatos; merged UPDATE = `UPDATE 1`.
- `3440423` **Q5 + Q6 + R1** (geo+discover): guarda de artículos (live: la/a/las→None, reales OK) +
  `RETURNING entity_ulid` atómico (mata la carrera) + source_ref COALESCE.
- `ed9d57d` **Q3** (complete): G4 `LEFT JOIN + COALESCE` (live: entity 0→278; 184 entities des-corruptas).

**PENDIENTES (contexto fresco — necesitan trabajo cuidadoso):** P2+Q9+Q10 (cluster silent-failure
harvest_dealer/scale_as24/autoscout24 — wiring try/except + record_run) → Q4+R2+R3 (recipe: migrar a
`yaml.dump` + validación de schema + guard anti-clobber) → Q8 (sanitize en emit_change_deltas — mi
código, defensivo, cuidado con tests de junk) → Q7 (discover in_db acumulativo → scope `seen_at>=run_start`)
→ R4 (discover skipped: log estructurado). Q2 = juicio (keep-old defendible), tracked.
Cada uno: verificar a mano → fix → test → commit.
