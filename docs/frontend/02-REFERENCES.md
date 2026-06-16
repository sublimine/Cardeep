# CARDEEP — Síntesis de las referencias del owner (Pinterest "Cardex", 106 pines)

> Leído de verdad 2026-06-16 con navegador real (no WebFetch). 66 pines extraídos.
> Veredicto del owner sobre la v1: "nivel canva/html de mi hermano pequeño" — porque
> explore/dealer/vehículo eran grids de cards planas. Esto corrige la dirección.

## Lo que el owner pinó (familias dominantes)
1. **Dashboards de élite (el grueso).** Orizon (Dynamic Financial Dashboard de Kristy),
   QClay (AI Medicine de Matthew Galt, "Cine 4d"), Fireart, SkillSet, forex/trading,
   traffic monitoring, management overview, project menus. → Data-viz rica, paneles que
   respiran, glass con refracción, profundidad real, densidad controlada. NO cards genéricas.
2. **3D automoción cinematográfico.** Showroom de coches, web de Ford (coche azul),
   coche blanco al atardecer entre molinos, vista cenital "find quality charging sites",
   3 pantallas de coches. → Presentación de coche dramática, iluminación de estudio, "Cine 4d".
3. **Mapas interactivos.** "Our global presence" con pines, monitores con mapa. → confirma
   el mapa 3D como héroe, pero integrado como command-center, no decorativo.
4. **UIs de listing/búsqueda (real estate).** Search page, mapa+lista, app de casas. →
   patrón directo para el marketplace de coches: split mapa+resultados, filtros premium.
5. **Lifestyle aspiracional.** Familias con su coche al atardecer, pickup en la montaña.
   → fotografía emocional, no stock plano.

## Dirección CARDEEP (extraída, no inventada)
**"Command-center de inteligencia de mercado, grado agencia (Orizon/QClay), con 3D Cine-4D".**
- **Superficies = dashboard premium**, no cards: paneles glass con borde interior (refracción),
  separación por líneas/negativo, métricas en mono que respiran, charts reales. Matar el grid de cards.
- **3D cinematográfico**: el mapa de España con postproceso (bloom/glow tipo neón de los refs),
  materiales con emisión por cobertura, sombras de contacto, atmósfera (fog), entrada de cámara.
  Es el "otro nivel three.js" que el owner exige.
- **Marketplace = mapa + lista** (patrón real-estate): explorar con el mapa vivo al lado de los resultados.
- **Vehículo = ficha cinematográfica**: foto a sangre con tratamiento de estudio, tilt 3D, specs como panel.
- **Motion con intención**: entradas con ease-out-expo, micro-interacciones, nada lineal.
- **Imagen**: aspiracional donde haya hueco; cero relleno plano.

## Anti-patrones (lo que mató la v1 — prohibidos)
Grids de 3 cards iguales · cards genéricas con sombra plana · todo plano sin profundidad ·
hero centrado · tipografía sin carácter · "parece una plantilla". (Coincide con `web/design-quality.md`.)

## Plan de re-nivelado (sobre lo ya funcional P0–P4) — commits 537107a→77f3a0c
- **R1 ✅ 3D cinematográfico** — bloom + materiales emisivos + ContactShadows + fog. `537107a`.
- **R2 ✅ command-center landing** — Panel glass "cobertura nacional · venta" (% real + barra
  segmentada por veredicto) + stats que respiran; kit `ui/Panel` reutilizable. `8b481ce`.
- **R3 ✅ explore = dashboard de cobertura** — barra de cobertura real por provincia + superficie
  glass; mata el grid de cards planas. `722c7df`. (El split mapa+lista queda como mejora futura.)
- **R4 ✅ vehículo cinematográfico** — viñeta de estudio + glow de precio + specs/plataformas glass.
  `07b787c`. **R5(dealer) ✅** — inventario en cards glass + actividad en panel. `77f3a0c`.
- **Pendiente:** motion/choreography de entrada (GSAP/stagger), split mapa+lista en explore,
  visor 3D por ficha si el owner pide "WebGL agresivo", Lighthouse/a11y/E2E.
Estado vivo en `00-PLAN.md`.
