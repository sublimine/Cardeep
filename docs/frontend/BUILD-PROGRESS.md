# CARDEEP front — BUILD PROGRESS (loop state, resumible)

> Loop autónomo del owner: *"ejecuta lo de arriba. Déjate de mapas 3D todo el rato y aplica cosas
> que vendan de verdad."* Construir superficie a superficie en `web/`, dato REAL, verificando cada
> una (render vivo + `npm run build` verde). Plan maestro: `00-PLATFORM-BLUEPRINT-E2E.md`.

## Directiva permanente
- **NO mapa 3D en todas partes.** Vive SOLO en `/explore` (selector geo) y `/cobertura`. Fuera del hero.
- **Cosas que venden:** fotos reales de coches (2,2M), precio, confianza/verificación, CTAs claros,
  cobertura como autoridad. Marca fiel: cobalt `#3B82F6` / charcoal / Outfit (tokens ya correctos).
- Sin código sin verificar; sin mocks; sin AI-slop. `npm run build` debe quedar verde cada iteración.

## Restricciones de la API (verificadas)
API = geo→entidad→inventario (`/stats`, `/geo/seal`, `/geo/{prov}/entities`, `/entities/{cdp}`,
`/entities/{cdp}/inventory|delta`, `/vehicles/{ulid}|/history|/platforms`). **NO hay búsqueda global
de vehículos ni endpoint de deals/price-rating** → eso es NEAR (nuevos endpoints), no se finge.
Coches reales para showcase = inventario de un dealer foto-rico (ej. Flexicar Madrid `CDP-ES-28-FX1FAD1S`).
Fotos hotlinked → `referrerPolicy="no-referrer"` en `<img>`.

## Hecho
- **[✓] Iteración 1 — Landing** (`routes/Landing.tsx` + `Landing.css`): hero valor+search+stats reales
  (sin 3D), showcase de 8 coches reales, banda de confianza, cobertura plana 80,5% (enlaza a /explore),
  CTA dealer. Reveal-on-scroll IO (reduced-motion ok). `referrerPolicy` en VehicleCard. Nav "Mapa"→"Inicio".
  **Verificado: render vivo + `npm run build` verde (0 type errors).**
- **[✓] Iteración 2 — Hero cinematográfico WebGL** (`three/HeroScene.tsx` + integrado en `Landing` vía
  `hero__bg`/`hero__scrim`): escena R3F en tiempo real (suelo reflectante MeshReflectorMaterial + barras
  de luz cobalt emisivas + Sparkles + Bloom/Vignette + parallax al ratón, reduced-motion safe). Sin mapa.
  Stack motion instalado (gsap+lenis+@gsap/react). `npm run build` verde (chunk Three.js lazy ~256KB gzip).
- **[✓] Iteración 2b — `/stats` arreglado de RAÍZ**: el proceso uvicorn vivo (PID 34640) corría código
  VIEJO → live-compute 5min + dealers inflado. Reiniciado con `CARDEEP_API_RATELIMIT_ENABLED=0 python -m
  uvicorn services.api.main:app --port 8090` (CORS default cubre :5173, modo dev). Ahora `/stats`=0,31s,
  source=precomputed (`product_stats`), cifras honestas: dealers **19.144** / coches **1.841.679** /
  eventos **2.741.085** / 52 prov. La franja del hero ya muestra números reales. **Deuda:** asegurar que
  el scheduler refresca `product_stats` en cadencia (fila actual 12:33; se calienta con
  `python -m scripts.refresh_product_stats`).
- **[✓] Iteración 3 — Landing coherente end-to-end**: smooth scroll **Lenis** wireado en `Layout`
  (reduced-motion safe), **stagger** de reveal por fila (showcase/features) + **hover cobalt** en feature
  cards. Landing completa: hero WebGL → showcase coches reales → confianza → cobertura → CTA dealer, stats
  honestos vivos. `npm run build` verde, 0 errores de consola, scroll OK.

## Cola (orden) — ACTUALIZADO
1. **[→] /explore — marketplace** (siguiente superficie visible; hogar legítimo del mapa 3D como selector
   geo): provincia→dealers→inventario, cards de coche reales, filtros (kind/Tier-1), hit-count.
2. /vehicle/:ulid — ficha cinematográfica. 3. /dealer/:cdp — command-center entidad. 4. /cobertura — mapa 3D.
   Cada una al nivel del hero (motion + composición), verificada (build verde + render).

## Cola (orden)
1. **[→] /explore — marketplace mapa+lista** (el #1 que vende; hogar del mapa 3D). Provincia→dealers→
   inventario, filtros (kind/Tier-1), hit-count, cards de coche reales.
2. /vehicle/:ulid — ficha cinematográfica (foto a sangre, specs panel, historial Δ, deep-link, platforms).
3. /dealer/:cdp — command-center de entidad + inventario + actividad/delta.
4. /cobertura — el mapa 3D scroll-scrubbing (su showcase).
5. Pulido transversal: motion de entrada, a11y, Lighthouse, diversificar el showcase multi-dealer.
NEAR (requiere backend): búsqueda global, price-rating real, deals; auth/dashboard dealer; etc.

## Cómo verificar una iteración
`cd web && npm run build` (verde) + dev `npm run dev` (:5173) contra API viva
(`CARDEEP_API_RATELIMIT_ENABLED=0 uvicorn services.api.main:app --port 8090`, DB cardeep-pg:5433).
