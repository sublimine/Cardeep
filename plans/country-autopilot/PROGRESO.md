# PROGRESO — country-autopilot (auto-onboarding autónomo de país)
> Hands-off total (owner 2026-06-28). Rama `feature/country-autopilot` desde main `12e2499`.
> Doctrina: build staged + orquestar + persistir + puertas PENDIENTE-OWNER (no detienen) + nada de €.

## Fase 0 — RECON (EN VUELO)
4 agentes read-only aterrizando cada pieza en el código real:
- [ ] geo + denominador (auto-pack datos €0)            — agent af077bcfebe0a44d5
- [ ] fuentes + recetas (auto-pack descubrimiento €0)   — agent a16b1feef8c5fe309
- [ ] auditor automático multi-nivel (sobre VAM)        — agent af3da821da510cedb
- [ ] orquestador + supervisión + PUERTAS               — agent a8eb8cfdd8d7a4034

## Fase 1 — DISEÑO (tras recon)
- [ ] integrar los 4 recon → completar `00-DESIGN.md` con [VERIFICADO]
- [ ] decomponer en sub-proyectos buildables + orden + criterios de aceptación
- [ ] fijar la frontera: qué se construye+valida en DRY-RUN/sintético vs qué es PUERTA

## Fase 2 — BUILD STAGED (tras diseño, TDD + orquestado)
- [ ] (se decompone tras Fase 1)

## DÓNDE RETOMAR (si se corta el contexto)
- Rama `feature/country-autopilot`. `plans/country-autopilot/00-DESIGN.md` = esqueleto.
- Esperando los 4 recon; al aterrizar → integrar → completar diseño → build.
- :5433 producción NO se toca; validación en :5434/sintético. Backup ES en scratchpad/cardeep-5433-0064.dump.
