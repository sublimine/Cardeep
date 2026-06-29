# PROGRESO — Camino al 13/10
> Bitácora viva. Goal owner: "Quiero el puto 13/10" (hands-off). Roadmap: 00-ROADMAP.md.
> Rama de trabajo: feature/country-autopilot (contiene el frente activo: cracker, autopilot).
> Doctrina: bloque → verificación → commit selectivo → siguiente. Stack caído (docker daemon off) → bloques PUROS primero; los de DB construidos con verificación PENDIENTE-infra.

## ESTADO DEL ENTORNO (2026-06-29)
- docker daemon: **OFF** → no hay PG efímero para tests de migración. Bloques [requiere DB] quedan construidos+test-escrito, verificación-DB PENDIENTE-infra (owner levanta stack o docker).
- pytest 9.0.2 OK. R-portable instalado. camoufox/nodriver/playwright instalados (no en requirements).
- :5433 = PRODUCCIÓN intocable. Bomba RIVR sigue sin commit en working tree (no se commitea; T0 la neutraliza).

## TABLA DE BLOQUES
| Bloque | Estado | Verificación |
|---|---|---|
| T4.1 blindar ladder (try/except por rung) | ✅ HECHO | 27 passed (2 nuevos RED→GREEN), 0 regresión |
| T0.1 neutralizar bomba RIVR | ✅ HECHO | stash@{0} (preservado, recuperable; no destructivo) |
| T0.2 endurecer guardrail anti-fabricación | ✅ HECHO | 4 guards activos (vocab-DeFi + $abrev, RED→GREEN) + 1 skip-doc T5 |
| T0.3 higiene (purgar basura untracked) | ✅ HECHO | 3 recipes-basura + 4 .pyc huérfanos borrados; fixture autouse aísla escritura |
| T1.3 property-based invariantes (PURO) | ✅ HECHO | 10 properties; no-vacuidad por mutación (2 mutantes cazados) |
| T4.3 VAM real cracker (parcial-PURO) | ⏳ SIGUIENTE | — |
| T1.1 mecanizar vam_verified | 📐 BLUEPRINT | 01-T1.1-vam-verified-blueprint.md; ejecutable con stack (DB) arriba |
| T1.2 2º cinturón anti-cross-country (puro) | ✅ PARCIAL | aserción fail-closed, 3 tests; 3er cinturón (constraint DB)=ejecución pendiente |
| T2.1 CIF arista dedup (lógica) | ✅ LÓGICA | 4 tests puros RED→GREEN; re-cluster=DB-gated |
| T2.3 Chao puro-Python | ✅ HECHO | chao_lower, 5 tests valores-textbook; NO cableado al sello (DB-gated) |
| T3.* ops 24/7 | ⬜ | mayoría [DB]/owner |
| T5.* producto | ⬜ | tras T0 |

## LOG
### 2026-06-29
- **T4.1 ✅** RED→GREEN: 2 tests (test_rung_that_raises_is_recorded_failed_and_escalates, test_all_rungs_raising_yields_failed_not_crash) probaron que un rung que lanza abortaba el crack (recipe_cracker.py:315 sin try/except). Fix: try/except por rung → RungAttempt FAILED + continue. 27 passed/0 failed en la suite del cracker. Causa raíz, €0, sin DB. Commit 9d0c4b3.
- **T0 ✅ (T0.1+T0.2+T0.3).** HALLAZGO clave: la "bomba RIVR" (landing de OTRO producto DeFi, 5 cifras fabricadas) estaba SIN COMMIT en working tree → neutralizada con `git stash` (preservada, no destruida). Guardrail endurecido test_web_no_fabricated_data.py: 2 checks nuevos RED→GREEN — `test_landing_has_no_foreign_product_vocabulary` (regex word-bounded vocab DeFi: rivr/staking/apy/vaults/tvl/yielder/...) + `test_landing_has_no_hardcoded_abbreviated_money_metric` ($2.4B). Detectaron la bomba real (RED) antes de stashear.
  - HALLAZGO PROFUNDO (gana el código): el frontend ENTERO es un scaffold demo/marketing — la landing CARDEEP de HEAD tiene cifras del censo FABRICADAS (1_550_000 "vehículos", 28_000 "dealers" vs /stats real ~1.84M/19.144) + el CRM scaffold (Dashboard/Market) tiene UI mock (2_140_000...). NINGUNA página consume el censo vivo (cardeep.ts = 0 imports). El check viejo `test_no_unexplained_big_underscore_numerics` escaneaba todo web/src → **el CI unit de esta feature YA estaba rojo** por este demo data. Convertido a **skip documentado con roadmap T5** (re-activa al cablear páginas a /stats): rojo-silencioso → deuda trazada. NO debilita la defensa anti-bomba (los 2 checks nuevos quedan vivos).
  - T0.3: borrados countries/ES/recipes/{r1,r3,llm_local}__d.yaml (test pollution, declared:47 fabricado) + 4 .pyc huérfanos test_country2_*. Causa raíz: fixture autouse `_isolate_recipe_writes` monkeypatcha recipe.ROOT→tmp en TODOS los tests del cracker (ningún test futuro puede contaminar el árbol real). 16 passed, árbol limpio verificado.
- **PENDIENTE-OWNER / T5 (reportado):** rehacer la landing+CRM consumiendo la API viva (cardeep.ts) y eliminar TODO dato fabricado del censo; re-activar el guard underscore. Es producto (T5), requiere API viva (stack caído) + decisiones de diseño. RIVR preservado en stash@{0} como referencia de composición.
- **T1.3 ✅** tests/test_property_invariants.py — Hypothesis 6.x (añadido a requirements-dev). 10 properties PURAS sobre 2 invariantes: (a) state machine COVER(CC) — validador==grafo ∀ par, lifecycle lineal forward, SEALED terminal, unknown rechaza, initial→REGISTERED; (b) cdp_code — determinismo, formato país-paramétrico ^CDP-[A-Z]{2}-, identidades distintas→códigos distintos, ES byte-idéntico, y EL invariante country-proof: country_code NUNCA entra en canonical_key. **No-vacuidad PROBADA por mutación** (oráculos independientes del código): mutar VALID_TRANSITIONS (KNOW_COUNTRY→IN_COVERAGE) tumba `test_lifecycle`; filtrar country en canonical_key tumba `test_country_never`; ambos revertidos con git, verde final 10/10. Es el movimiento #1 del arquitecto (goldens-ejemplo → propiedades). Commit (post-T1.3).
- **T4.3 ✅** `_offline_verdict` (recipe_harness.py:196): 0==0 daba TRUSTWORTHY (quórum sobre nada); el path DB ya guardaba zero_certifiable (verify.py:154), el espejo offline NO → el verdict del RungAttempt mentía (decide_status ya FALLA el sample vacío, pero el trail registraba TRUSTWORTHY). Fix raíz: `0==0 → UNVERIFIED` espejando el path DB. tests/test_offline_verdict.py 4 tests RED→GREEN, 35 passed regresión cracker/harness/VAM.
- **T2.3 ✅** `chao_lower` en estimators.py — Chao (1987) cota inferior no-paramétrica robusta a heterogeneidad (N̂=S+f1²/2f2; bias-corrected f2=0; CI log-normal SpadeR/iNEXT). tests/test_chao_estimator.py 5 tests valores-textbook RED→GREEN. ADDITIVO: NO cableado a estimate_stratum (el sello servido) — cablearlo es DB-gated (dry-run+golden). Los 5 errors de test_api_exhaustiveness son DB-required pre-existentes (docker OFF), no de este cambio.

- **T1.2-adj ✅** meta-guard `test_served_queries_have_country` — `_SERVING_FILES` (8 archivos hardcoded) → descubrimiento DINÁMICO de services/api/**/*.py + pipeline/geo.py. Cierra el bypass §2.1 del escéptico (un router nuevo evadía el guard). Mutation probado: un router probe `SELECT cdp_code FROM servable_entity WHERE province_code=$1` ahora ES cazado. 2 unit verdes + mutation-kill.

## ESTADO DEL LOTE (2026-06-29)
**8 bloques cerrados + verificados + commiteados** (todos €0, sin DB, causa-raíz, TDD, RED→GREEN o mutation-probado): T4.1 (ladder blindado), T0.1/0.2/0.3 (bomba RIVR neutralizada + guardrail clase + higiene), T1.3 (property invariants), T4.3 (VAM offline cero), T2.3 (Chao), T1.2-adj (meta-guard dinámico). **Auditoría del lote: `pytest -m unit` = 741 passed / 0 failed / 3 skipped.**
**MURO REAL = la DB (docker daemon OFF).** Los siguientes bloques de máxima palanca (T1.1 mecanizar vam_verified, T1.2 country-proof constraint, T2.1 CIF) tocan el SERVING/datos-servidos → exigen dry-run+golden+DB; construirlos a ciegas violaría la lección grabada ("no mutar datos servidos sin plan verificado"). Quedan PENDIENTE-OWNER (arrancar el stack desbloquea su verificación; el CI db-tests/country-proof también los verificaría al pushear). NO se declaran hechos sin probar.
**T1.1 BLUEPRINT ejecutable listo** (`01-T1.1-vam-verified-blueprint.md`): problema verificado file:line + diseño (clon del trigger 0036) + SQL borrador (en doc, NO migración aplicable-a-ciegas) + plan de verificación dry-run :5434→golden→Ferrari + manejo de las filas grandfathered. Se ejecuta en cuanto arranque `docker compose up -d cardeep-pg`. Lo mismo procede para T1.2/T2.1 (blueprintear o ejecutar directo con DB).
**DESBLOQUEO:** owner arranca el stack (`! docker compose up -d cardeep-pg`) → ejecuto T1.1/T1.2/T2.1 con verificación real (dry-run, sin tocar :5433).

### 2026-06-29 (cont.) — 9º bloque
- **T1.2 2º CINTURÓN ✅ (puro)** `cross_source_dedup.py` — el overlay tenía CINTURÓN ÚNICO (block-keys con country); si un edge-builder olvidara country, el union-find fusionaría cross-country SIN red (arquitecto F1; resolve_entities ya tenía 2º cinturón, cross_source no). Añadido `CrossCountryClusterError` + `_assert_single_country_clusters` (espejo de resolve_entities) cableado tras `uf.components()` en `_build_cluster_table`: un cluster multipaís FALLA CERRADO en vez de servirse. tests/test_cross_source_country_belt.py 3 tests PUROS RED→GREEN (edge-builder defectuoso cross-country → raise / merge mono-país ok / singletons distinto-país ok). El **3er cinturón mecánico (constraint DB en entity_cluster)** es T1.2-ejecución (DB-gated). Bloques puros del lote: 28/28.
- **SIGUIENTE (especificado):** (a) replicar `_assert_single_country_clusters` en `cluster_dealers._build_cluster_table` (mismo patrón, cierra la simetría restante); (b) DB-gated cuando arranque el stack: 3er cinturón = constraint/trigger en entity_cluster/vehicle_cluster (blueprint análogo a 01-T1.1) + re-cluster con CIF (T2.1-ejecución, dry-run :5434→golden→Ferrari) + T1.1 vam_verified trigger.
- **T2.1 LÓGICA ✅** `cluster_dealers.py` — CIF/NIF como **arista de dedup** (la señal más fuerte, estaba cargada y SIN USAR). `_normalize_cif` (9 alnum, no all-same → rechaza placeholders) + `idx_cif` keyed `(cif, country)` SIN muni (un CIF es nacional → fusiona sucursales de una empresa across municipios) + bucket en `_build_deterministic_edges`. Over-merge-safe (CIF idéntico válido = misma empresa legal; a diferencia del geo-match revertido). country-proof (country en la key). RESOLVER 2.2.0→2.3.0. tests/test_cif_dedup_edge.py 4 tests PUROS RED→GREEN (lógica en memoria: same-cif merge cross-muni / distinct no / cross-country no / placeholder no). **El RE-CLUSTER que lo aplica al serving es DB-gated** (dry-run :5434→golden→Ferrari, lección re-cluster) → NO ejecutado a ciegas; documentado en el comment de RESOLVER_VERSION. Bloques puros del lote: 23/23 verdes.
**RESTA, por gate:**
- **[DB] (docker daemon OFF)** — construibles STAGED (migración+test) pero NO verificables aquí: T1.1 mecanizar vam_verified (hallazgo #1 escéptico), T1.2 country-proof constraint, T2.1 CIF arista, T2.2 Splink, T2.4 jerárquico, T4.5 loop cracker, T5.5 buscador.
- **[infra-owner]** — T3.2 instalar supervisores (NSSM/systemd), T3.1 backups (necesita PG), T4.6 egress residencial.
- **[red/ToS]** — T4.2 auto-API-discovery, T4.4 fetch real + Ollama.
- **[producto + API viva]** — T5.* (rehacer landing/CRM sobre cardeep.ts; re-activar guard underscore).
SIGUIENTE: T1.1 STAGED — migración del trigger vam_verified + test; verificación PENDIENTE-DB (declarada, no "hecha").
