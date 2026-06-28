# Country-Autopilot — auto-onboarding AUTÓNOMO de país (diseño)
> Owner 2026-06-28, hands-off total: el sistema mismo auto-genera lo personalizado de un país
> y lo audita SOLO (auditor que no es el owner), antes de arrancar, y supervisa. "País nuevo =
> otra ejecución" de verdad autónoma. Estado: recon orquestado en vuelo; diseño se completa al aterrizar.

## El loop (arquitectura objetivo)
```
RESEARCH → PROPONER(pack país + PLAN) → AUDITOR multi-nivel(automático) → [PUERTA] → EJECUTAR → SUPERVISAR → SELLAR
                                              │ aprueba c/confianza → ejecuta
                                              │ baja confianza / puerta → PENDIENTE-OWNER (aparca, NO detiene el loop)
```
- **PACK PAÍS** = 🗺️ geo · 📇 fuentes ortogonales · 🧩 recetas · 📊 denominador.
- **PLAN país** = qué fuentes, cadencia, cobertura esperada, riesgos — el artefacto que el auditor revisa.
- **AUDITOR** = council adversarial multi-nivel sobre la doctrina VAM (cero-confianza, quórum ≥2 vías ortogonales);
  veredicto APRUEBA / RECHAZA / ESCALA, con score de confianza. NO el owner.

## Componentes (sub-proyectos — cada uno spec→TDD→verificado)
1. **AUTO-PACK · datos** — geo (OSM/Overture/GADM €0) + denominador (Eurostat/institutos €0) auto-extraídos.
2. **AUTO-PACK · descubrimiento** — auto-discover fuentes del país + auto-recetas (RecipeHarness).
3. **AUDITOR multi-nivel** — council adversarial sobre VAM/inquisición; gate automático.
4. **ORQUESTADOR + supervisión** — el loop country-autopilot + PLAN país + supervisión por-país + las puertas.

## Las PUERTAS (PENDIENTE-OWNER — aparcan, NO detienen; doctrina never-stop + €0)
- **GASTO**: €0 inviolable. Vía que pida dinero → aparcada, agotar la gratis primero.
- **PROD**: escribir el censo de un país real vivo → owner (como el cutover ES).
- **LEGAL/ToS**: scrapear un país real → owner.
→ El meta-sistema se CONSTRUYE y VALIDA en dry-run/sintético (un país ficticio "XX" o DE sintético);
  la ejecución viva sobre un país real es la puerta. Prohibido declarar 100% con residual gated.

## Orden de construcción
(se fija tras el recon; provisional: 1+2 auto-pack en paralelo → 3 auditor → 4 orquestador que los une)

## Recon en vuelo
4 agentes read-only mapean cada pieza en el código real → este diseño se completa con [VERIFICADO].
