# CARDEEP — Auditoría COMPLETA del tablero de referencias del owner

> Tablero: `es.pinterest.com/ekarrouch0089/cardex/` · **107 pines** (105 únicos auditados;
> 28 "Más ideas" recomendados por Pinterest excluidos por no ser curación del owner).
> **Auditado foto-a-foto 2026-06-23 con navegador REAL** (Playwright, hoja de contacto local).
> Supersede la pasada de 2026-06-16 (que solo extrajo 66/107 — incompleta; de ahí el "audita
> CADA foto" del owner). Hoja de contacto reproducible: `scratchpad/contact_sheet.html`.
> LECCIÓN PERMANENTE: el WebFetch de Pinterest solo da el título; el tablero exige navegador real.

## Familias dominantes (con índices de pin reales del tablero)

1. **Dashboards / command-centers premium — EL GRUESO (~40 pines).** Claros y oscuros.
   Financieros (#5, **#68 Orizon "Dynamic Financial Dashboard" de Kristy**, #76, #86, **#88 forex**),
   admin/SaaS (#2 "Hi Blah!", **#6 "Make Things Simple"** glass+montañas, #16, #24/#26 "Good morning Mike",
   #31 "Ongoing 8 Projects", #35 info-board amarillo, #40 quick-project, **#79 "Make history. Don't just
   report on it."**), bento/overview (#55 "several dashboards"). KPI tiles, charts reales, paneles glass
   con borde interior, densidad que respira. **NO cards planas genéricas.**

2. **Automoción — MASIVO (~30 pines), el alma del producto.**
   - *Configuradores / dashboards de coche (oscuros, Cine-4D):* **#7 Volvo EX30** (specs 20/10:25),
     **#32 "800 km"** eléctrico, **#38 fleet + mapa/red azul** (telematics command-center), #43,
     **#80 car dashboard en iPad**, **#90 "garage" car-selling**, **#104 coche de lujo + controles**.
   - *Marketplace de coches:* **#33 "Choose your cars"** (grid oscuro de coches), #58 multi-pantalla,
     #62 app móvil coches+personas.
   - *Web de marca automotriz (cinematográfica):* **#37 Audi**, **#74 Ford coche azul**, **#100 Aito-M5**,
     **#101 RonDesignLab (coche amarillo)**, #36 coche B/N, **#75 "Next-Generation Car Journey"**,
     **#95 "Luxury and Speed / Modern Travel"**.
   - *Sales dashboards:* #89, #97 (púrpura), #103 "sales & advertising".
   - *EV + carga + mapa:* **#27 "find & qualify charging sites"**, #8 mapa charging.

3. **Mapas / geo command-center (~5) — CONFIRMA EL HÉROE 3D.** **#11 "Our Global Presence"**
   (mapa con pines naranjas + stats 255+/3.135+), #8 charging map, #38 fleet map. (Recomendados afines:
   transporte por clusters, world-map+stats — refuerzan, no son del owner.)

4. **Marketplaces de listing / real-estate (~6) — patrón directo para "explorar".**
   **#49 search page + mapa**, #50/**#52 "Find Your Perfect Property"** (foto arquitectónica + listing),
   **#84 "Real estate for living and investments"** ("Latest in your area"), #29 app de casas (cards),
   #102. → split **mapa + lista**, filtros premium, ficha rica.

5. **Heroes de producto AI / Cine-4D (~4).** **#0 "Inference at the Edge"** (oscuro, glow naranja,
   agency: redliodesigns/zajno/awsmd/slabdsgn), **#30 "Meeting Assistant"** (gradiente violeta),
   **#63 QClay "AI-Powered Medicine" de Matthew Galt (Cine-4D)**, #4 "Empower Your Workflow with AI".
   → 3D cinematográfico, bloom/glow, ribbon, profundidad.

6. **Fotografía emocional de automoción (~8) — aspiracional, humana.** #54 familia+coche atardecer,
   #61 camping con pickup, #65 manos+coche atardecer, **#67 padre+hijo+globos (entrega de coche)**,
   #92 clásico naranja, #93 SUV en montaña. → cero stock plano; momento real.

7. **Editorial / tipografía con carácter (~5).** #22 "Find Your Street Ballers", #72 "growth",
   #78 "botanical", #73 "Work Anywhere" (B/N), #95.

8. **3D espacial / configurador de espacio (~4).** **#97/#98 "Elevate Your Living Experience"**,
   #57 car showroom 3D, #9 isométrico.

9. **Auth/onboarding (~2).** **#51 "Create new account"** (oscuro + foto al atardecer), #52.

10. **Home/IoT command-center (~2).** **#99 home dashboard con casa + coche + clima 23°**, #25 smart home.

**Ruido off-theme (minoría, el owner pina amplio):** #14 uñas, #15 panadería, #19 "Cool Cats", #69 perro.
No dirigen el diseño.

## Dirección extraída (de las 105, no inventada)
**"Command-center de inteligencia de mercado automotriz, grado agencia (Orizon/QClay), con 3D Cine-4D
y alma editorial/emocional."** Tres pilares, coherentes en todo el tablero:
- **Base oscura command-center** (la mayoría de los dashboards y toda la automoción premium son dark):
  superficies glass con borde interior/refracción, charts reales, KPIs en mono que respiran, profundidad
  por capas y sombra de contacto, glow/bloom semántico (no decorativo). Acentos fríos (azul/violeta) +
  un cálido de señal (naranja/ámbar de #0/#11).
- **3D cinematográfico** como héroe: el **mapa 3D de España** (= #11 "Our Global Presence" llevado a
  three.js, ya en `SpainMap.tsx`) con postproceso, emisión por cobertura, fog, entrada de cámara; y la
  **ficha de vehículo** con tratamiento de estudio (#57/#75/#100).
- **Marketplace = mapa + lista** (#49/#52/#84): explorar con el mapa vivo al lado de resultados ricos;
  ficha de coche cinematográfica; momento emocional en los vacíos (#54/#67).

## Anti-patrones (mataron la v1 "nivel canva" — PROHIBIDOS)
Grids de 3 cards iguales · cards genéricas con sombra plana · todo plano sin profundidad ·
hero centrado sin tensión · tipografía sin carácter · "parece plantilla". (Coincide con `web/design-quality.md`.)

## Aplicación por superficie de CARDEEP
| Superficie | Referencia del tablero | Qué construir |
|---|---|---|
| Landing / hero | #11, #0, #63, #68 | Mapa 3D de España (cobertura por veredicto) como command-center + panel glass de cobertura nacional + stats que respiran |
| Explore | #49, #52, #84, #33 | Split **mapa + lista**: provincias→dealers con barra de cobertura real, filtros premium (kind/Tier-1), NO grid de cards planas |
| Dealer | #80, #90, #38 | Panel de entidad estilo dashboard de gestión + inventario en superficie glass + actividad/delta |
| Vehículo | #7, #57, #75, #100, #104 | Ficha cinematográfica: foto a sangre con viñeta de estudio + specs como panel + deep-link + plataformas + (futuro) badge de valoración |
| Inteligencia (futuro) | #5, #68, #76, #86 | Capa de valoración/mercado (Indicata/GANVAM): dashboards financieros reales sobre el censo |

## Estado actual del front (a contrastar contra esta dirección)
`web/` (Vite+React19+R3F) tiene P0–P4 + re-nivelado R1–R5 (`537107a→77f3a0c`) ya orientado a
"command-center + Cine-4D" — alineado con el tablero. Pendientes: motion/choreography de entrada,
**split mapa+lista en explore** (lo pide #49/#52/#84), price-rating badge, Lighthouse/a11y/E2E.
Ver `docs/frontend/00-PLAN.md`.
