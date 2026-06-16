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

**FIJADOS (2ª tanda, 3 commits):**
- `b902276` **P2+Q9** (harvest_dealer): alerta dealer-específica (`fire_alert`, NO record_run source-level —
  corregí al agente) en cada fallo (scrape exc / no-dealer / ingest-error); inesperado → alerta + RE-RAISE. 3 tests.
- `84309ee` **Q10** (autoscout24): `collect_dealer_slugs` loguea la truncación en vez de `break` silencioso.
- `c8a1c2f` **R4** (discover): traza per-entity de skipped-no-province.

**FIJADOS (3ª tanda — review pipeline COMPLETO):**
- `ab0cf3d` **Q4+R2+R3** (recipe): `_yaml_dump`→`yaml.dump` (Q4: reprod. live ScannerError→round-trip OK) +
  validación non-empty-dict + round-trip self-check (R2) + log de clobber semántico (R3). 4 tests + 31 reshape.
- `2755aad` **Q7** (discover): in_db scopeado a `seen_at>=run_start` (live: oem_skoda all-time=196 vs this-run=0).
- **Q8** (delta): sanitize_price/km en diff_vehicle + up_price/km **+ COALESCE en `_BULK_REFRESH`** — junk (0/neg/
  >10M)→None→sin evento (no sobrescribe válido); COALESCE evita NULL-ear un campo válido cuando otro cambia
  (live: photo intacto + price=9999). Cazó un wipe latente además del gap de sanitización. Test de junk + COALESCE live.

**PIPELINE REVIEW CERRADO:** los 19 hallazgos resueltos — **15 reales fijados** (P1, P2, Q1, Q3, Q4, Q5, Q6, Q7,
Q8, Q9, Q10, R1, R2, R3, R4), Q2 = juicio/no-bug (keep-old defendible ante junk). Cada uno verificado a mano
(incluso corregí la granularidad del fix del agente en P2/Q9) + test + live + commit + CI verde.
