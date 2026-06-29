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
| T0.2 endurecer guardrail anti-fabricación | ⏳ EN CURSO | — |
| T0.3 higiene (purgar basura untracked) | ⬜ | — |
| T1.3 property-based invariantes (PURO) | ⬜ | — |
| T4.3 VAM real cracker (parcial-PURO) | ⬜ | — |
| T1.1 mecanizar vam_verified | ⬜ [DB] | construir+test, verif PENDIENTE-infra |
| T1.2 country-proof constraint | ⬜ [DB] | idem |
| T2.1 CIF arista dedup | ⬜ [DB] | idem |
| T2.3 activar R §2.3 + Chao | ⬜ | Chao puro ya; R-crosscheck flag |
| T3.* ops 24/7 | ⬜ | mayoría [DB]/owner |
| T5.* producto | ⬜ | tras T0 |

## LOG
### 2026-06-29
- **T4.1 ✅** RED→GREEN: 2 tests (test_rung_that_raises_is_recorded_failed_and_escalates, test_all_rungs_raising_yields_failed_not_crash) probaron que un rung que lanza abortaba el crack (recipe_cracker.py:315 sin try/except). Fix: try/except por rung → RungAttempt FAILED + continue. 27 passed/0 failed en la suite del cracker. Causa raíz, €0, sin DB.
