# PROGRESO — country-autopilot (auto-onboarding autónomo de país)
> Hands-off total (owner 2026-06-28). Rama `feature/country-autopilot` desde main `12e2499`.
> Doctrina: build staged + orquestar + persistir + puertas PENDIENTE-OWNER (no detienen) + nada de €.

## Fase 0 — RECON
4 agentes read-only aterrizando cada pieza en el código real:
- [x] geo + denominador (auto-pack datos €0)            — esquema/seams YA país-genéricos; falta el EXTRACTOR (GeoNames CC-BY + Eurostat-LAU cross-walk para geo; Eurostat-SBS-G45 + GLEIF para denominador); PUERTA NONE (descargas públicas); checkpoint = cross-walk a código oficial + split por segmento.
- [x] fuentes + recetas (auto-pack descubrimiento €0)   — spine (harness sample-verify-delete+VAM, dealerprobe puro schema.org country-agnóstico, taxonomía buckets, plumbing 0053/paths/complete/seal) YA construido. FALTA: (a) auto-source-finder (clasificar fuentes país→buckets), (b) peldaños auto-receta css/llm_local (extruct+crawl4ai+Ollama, elegidos no construidos). overture/osm/AS24/oem_* re-param por bbox/TLD/locale = AUTO.
- [ ] auditor automático multi-nivel (sobre VAM)        — agent af3da821da510cedb (en vuelo)
- [x] orquestador + supervisión + PUERTAS               — orquestación (stage 09: scheduler/discover_schedule/health/silence_watchdog) = 100% country-blind = EL TARGET. FALTA: cover(CC) state machine + tabla country_campaign + módulo `pipeline/ops/autopilot.py` + split registry motor↔pack (`get_harvest_registry(country)`/`active_countries()`) + country_code en source_health/harvest_run/scheduler_lease (cierra O2/O3/O5 zombie-silence) + supervisor salud per-país. PUERTAS [VERIFICADO]: GASTO=`requires_env`/`_gated` (primitivo existe, 0 rutas €>0 hoy) · PROD=`config_guard.py` fail-closed CARDEEP_ENV=prod (existe+robusto, wired 3 seams) · LEGAL=doctrina (KNOW_COUNTRY dossier, sin primitivo código). El patrón dry-run/apply/verify/revert de `scripts/pilot_country.py` = el molde del loop.
- [ ] auditor automático multi-nivel (sobre VAM)        — agent af3da821da510cedb (en vuelo, último)

## SECUENCIACIÓN (decisión de diseño)
El de-cegado del SPINE (P0 discover/ingest/harvest/complete, P1 MSE 0065, P2 product_stats 0066/canonical/phone, P3) vive en `feature/country-2-readiness` (212/212, NO mergeada a main por la coordinación de deploy de 0066). El AUTOPILOT necesita ese spine para validar onboarding end-to-end → **rebasar `feature/country-autopilot` sobre `feature/country-2-readiness`** (no sobre main). main (desplegado) se queda sin el spine (ES byte-idéntico, correcto). El de-cegado restante (OI-2 31 platform mints, OI-7 numerador, OI-8 pHash, OI-10 orquestación namespace) = precondición a cerrar dentro del autopilot.

## HALLAZGO MADRE (reordena el diseño)
La BIBLIA ya diseñó esto a fondo en `docs/generic-engine-bible/`:
- `COUNTRY-PACK-CONTRACT.md` — 8 piezas transversales + forma física `countries/<CC>/` (country.toml, geo/, locale.yaml, identity.toml, recipes/, census/, taxonomy.yaml) + **§5 compuerta `cover(CC)` = checklist de PREDICADOS VERIFICABLES (query/assert)** = el núcleo del AUDITOR automático ya especificado + invariante byte-identidad ES.
- `COVER-NEW-COUNTRY.md` — máquina de estados REGISTERED→KNOW_COUNTRY→BOOTSTRAPPED→IN_COVERAGE→SEALED (el orquestador).
- `COUNTRY-PROOF-INVARIANT.md` — el guard mecánico (COUNT(DISTINCT country_code)=1/cluster) = **YA construido+desplegado esta sesión**.
- Los 11 OPEN ITEMS (de-cegado del motor, OI-1..11): **CERRADOS esta sesión** OI-1(G1)/OI-3(geo)/OI-4(discover)/OI-5(provincia)/OI-6(MSE 0065)/OI-9(servable 0058)/OI-11(DSN); a verificar OI-2(31 platform mints)/OI-7(numerador canónico)/OI-8(pHash)/OI-10(orquestación namespace+silence zombie).
⇒ El AUTOPILOT NO es from-scratch: = ejecutar el contrato (generador `countries/<CC>/` + 2 extractores auto-pack + auto-source-finder + peldaños receta) + wirear §5 como AUDITOR + el orquestador cover(CC) sobre la máquina de estados. Gran parte EXISTE o está DISEÑADO.

## Fase 1 — DISEÑO (tras recon)
- [ ] integrar los 4 recon → completar `00-DESIGN.md` con [VERIFICADO]
- [ ] decomponer en sub-proyectos buildables + orden + criterios de aceptación
- [ ] fijar la frontera: qué se construye+valida en DRY-RUN/sintético vs qué es PUERTA

## Fase 2 — BUILD STAGED (TDD + orquestado, dry-run :5434, ES byte-idéntico)
- [x] **B · fundación** — `1d20ba4` VERIFICADO: split registry motor↔pack (`pipeline/ops/registry/{__init__,es}.py`, `get_harvest_registry`/`active_countries`==['ES'], byte-idéntico 50 entradas) + `CountryProfile`/`country.toml` (`pipeline/country_profile.py` + `countries/ES/country.toml`). 34+114 passed.
- [x] **C · extractores** — geo `2120cbd` (13/13; GeoNames+cross-walk; divergió a provincia←ADM2 por verdad-código ES) + denominador `93e1421` (12/12; cifra nacional [MEDIDO]; split-segmento=CHECKPOINT, NO fabricado). Ambos €0, fixtures, ES intacto. **Pendiente C**: auto-source-finder + peldaños receta css/llm_local.
- [x] **D · auto-auditor** `f984d1e` (35/35) — `pipeline/autopilot/auditor.py` N0-N4 sobre Inquisición/seal; **2 ejes** (decision build APRUEBA + `live_gate` N2 SIEMPRE ESCALA); MIN weakest-link. Council N2 = stub declarado. **Ola C+D verificada combinada 94 passed, :5433 0064 intacta.**
- [x] **E1 · espina orquestador** `b358c7c` (36/36): state machine cover(CC) + `country_campaign` (mig **0067**) + gate registry GASTO/PROD/LEGAL (aparca sin lanzar, probado vs config_guard).
- [x] **A · OI-2 platform mints** `980eea9` (95 passed): OI-2 estaba ABIERTO — **31 connectors** enrutados por `mint_code(country_code=…)`, byte-idéntico ES por-connector + costura DE. Residual: 32º mint en `scripts/cage_autorola…` (fuera del contrato OI-2, owner-triage).
- [x] **E2 · loop + E2E DEMOSTRADO** `7787d58` (13/13): `pipeline/ops/autopilot.py` `run_campaign('XX')` recorre REGISTERED→…→SEALED, mintea `CDP-XX-`, **violations=0**, puertas vivas APARCAN PENDIENTE-OWNER (`dry_run=False`→parkea en BOOTSTRAPPED, jamás auto-go-live), revierte limpio. **Verificado entero: 206 goldens + 60 no-regresión.**

### RESTA (queued, dry-run €0, no bloquea el loop demostrado)
- [x] **C source-finder** `6a7e25b` (12/12) — `pipeline/autopilot/source_finder.py` clasifica fuentes→7 buckets, `needs_audit=True` siempre + `CONFIDENCE_CAP=0.9<1.0` (incapaz de certificar) + contenido-vence-origen. Auto-pack COMPLETO (geo+denom+fuentes).
- [x] **A OI-10** `57466ab` (63 passed) — zombie silence O5 ARREGLADO RAÍZ (`resolve_recovered_silence_alerts`) + country_code en source_health/harvest_run/scheduler_lease (mig **0068**) + scope per-país. Aplicar 0068 a :5433 = gate OPERACIONAL owner.
- [ ] **A** · OI-7 (numerador único v_servable_dealer), OI-8 (pHash write-path, egress-gated), 32º mint residual `cage_autorola`.
- [ ] **C** · peldaños receta css/llm_local (extruct+Ollama local).
- [ ] **D** · council N2 adversarial (hoy stub) + persistencia `country_pack_audit_verdict`.
- [ ] **E3** · supervisor salud per-país (lee 0057/0058/0060/0064) + wiring al scheduler real.
- [ ] **MERGE** `feature/country-2-readiness` (spine de-cegado) → para cosecha REAL E2E (resolver detect.py).
- [ ] **PUERTAS OWNER** (no código): datos/scraping/legal de país real.
- [ ] **E2E** — onboard país sintético "XX" en :5434 por el loop completo; golden country-proof-invariant verde + byte-identidad ES.

## DÓNDE RETOMAR (si se corta el contexto)
- Rama `feature/country-autopilot`. `plans/country-autopilot/00-DESIGN.md` = esqueleto.
- Esperando los 4 recon; al aterrizar → integrar → completar diseño → build.
- :5433 producción NO se toca; validación en :5434/sintético. Backup ES en scratchpad/cardeep-5433-0064.dump.
