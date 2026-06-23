# CARDEEP — Dirección de Arte Cinematográfica (Build de Élite)

> **Director de Arte Jefe · 2026-06-23.** Síntesis de 10 dossiers de investigación + anclaje a
> `00-PLATFORM-BLUEPRINT-E2E.md` (estructura: qué va dónde, las 16 superficies, sitemap, fases) y
> `04-COMPETITIVE-UX-AUDIT.md` (patrones del sector ES + 6 técnicas GTA VI/motionsites).
> Este documento DIRIGE el build visual. No reabre la marca (sellada: cobalt `#3B82F6` · charcoal
> `#0A0E17`/`#111B27` · white · Outfit display · Geist/Geist Mono datos). Reparte: cada superficie
> hereda lo mejor de una fuente distinta, declarada con su técnica/librería y su origen de media.
>
> Doctrina heredada del blueprint: el dato real ES el media · cada botón con lógica · €0 por defecto
> (shaders R3F + CSS + SVG; el gasto Higgsfield se difiere a luz verde del owner) · motion deliberado
> (GTA VI: si quitas la animación y el significado no cambia, no existe) · solo
> `transform`/`opacity`/`clip-path`/`filter` · `prefers-reduced-motion` siempre respetado.

---

## 1 · CONCEPTO RECTOR

**"El censo respira en la oscuridad: España como un organismo de datos vivo, iluminado en cobalt,
que el usuario dirige como una cámara de cine."**

La sensación: entrar en una **sala de mando cinematográfica** (command-center dark-luxury), no en un
marketplace. El negro profundo (`#0A0E17`) no es ausencia de color: es el escenario que deja brillar
el único protagonista — el dato verificado. El cobalt `#3B82F6` es la **señal de vida**: pulsa en lo
sellado, late en el delta, guía la acción. Todo lo demás (UI, chrome, decoración) se retira al
silencio. El movimiento es **confiado y lento** (easing `cubic-bezier(0.16,1,0.3,1)`), nunca
frenético: dirige la atención hacia la cifra, la foto real, la provincia que se enciende. La
experiencia es **automovilística** sin caer en stock de coches: el lenguaje es de motor de juego
(GTA VI), de terminal Bloomberg (densidad sin fealdad) y de showroom nocturno (chiaroscuro cobalt).

**El foso visual:** todos los competidores son blancos, planos, formularios. CARDEEP es lo contrario
por construcción — oscuro, tridimensional, en movimiento dirigido, con el censo del 100% como
espectáculo. La diferencia no es decorar mejor: es que el dato que solo CARDEEP posee se presenta
como cine.

---

## 2 · DIRECCIÓN POR SUPERFICIE (mezcla explícita de fuentes)

> Formato: **[superficie]** — qué se hereda, de qué fuente, vía qué técnica/librería, con qué media.
> Anclado a la sección correspondiente del blueprint (`§3.x`).

### 2.1 LANDING `/` (§3.1) — la pieza faro

**HERO (split 55/45: copy izq · mapa 3D der).**
- **Composición y jerarquía** como **GTA VI** (vía técnica 4+6 del audit: jerarquía confiada, tipografía
  oversized con carácter, fondo casi-negro que deja brillar el sujeto) — `via` layout CSS grid +
  `--text-display clamp(3.5rem,2rem+8vw,8.5rem)` en Outfit ExtraBold.
- **Mapa 3D protagonista** como **AVATR Vision** (`vision.avatr.com`, WebGL en tiempo real, sin video
  pregrabado, capas que se "pelan") + **Lamborghini Huracán 360** (`lamborghini.com/3d`, canvas
  fullscreen orbitable) — `via` `SpainMap.tsx` (R3F existente) + `@react-three/postprocessing`
  (Bloom selectivo threshold 0.85 strength 0.3 en provincias SELLADO, Vignette perimetral, leve
  ChromaticAberration en transición de cámara) + FogExp2 density 0.08. **Media:** 3D R3F sobre dato
  vivo `/geo/seal` (extrusión por cobertura, color rampa GAP `#F0556B`→PARCIAL `#F5B33C`→SELLADO
  `#3B82F6`). Cero generado.
- **Atmósfera de fondo** como **Codrops "Distortion & Grain on Scroll"** (`tympanus.net` jul-2024) +
  **partículas cinéticas de Codrops nov-2025** — `via` shader GLSL propio (`vite-plugin-glsl`):
  partículas como bokeh de faros/polvo de carretera (`THREE.Points`, momentum*decay) + grano Simplex
  8-12% opacidad encima del canvas. **Media:** shader €0.
- **Headline kinético** como **Lando Norris (Awwwards SOTY 2025)** + **Codrops cinematic text reveal**
  — `via` GSAP SplitText: `'EL MERCADO DE COCHES DE ESPAÑA, VIVO'` en 3 líneas, line-mask reveal
  (`yPercent 110→0`, `ease expo.out`, stagger 0.10s), disparado on-load; la palabra `'VIVO'` con
  cylinder rotation 3D (transformOrigin `-100px`) como firma. **Media:** tipografía, €0.
- **KPIs vivos** (2,35M coches · 436k entidades · 52 provincias · cobertura %) como **Carvago/Coches.net
  contador-como-CTA** + **Exat Typeface kinetic** — `via` GSAP word-by-word scroll-scrub (cada dígito
  se revela al ritmo del scroll) + countUp; el número en cobalt, el label en white 60%. **Media:**
  dataviz, €0.

**SECCIONES (scroll narrativo bajo el hero):**
- **Scroll-storytelling del censo** como **PORSCHEvolution** (`porschevolution.com`, capítulos por scroll,
  sin clicks) + **GTA VI pinned/scrubbing** (audit técnica 1+2+3) — `via` GSAP ScrollTrigger pin +
  ScrollSmoother (`smooth:4`) + Lenis: el mapa se enciende provincia a provincia mientras un titular
  SplitText cuenta el QUÉ. **Media:** mapa R3F vivo.
- **Command strip de cobertura + 3 pilares + delta feed** como **artificial-garage** (`artificial-garage.com`,
  editorial layering, parallax fotográfico, microinteracciones) — `via` GSAP parallax multi-capa +
  reveal stagger. **Media:** dataviz + foto real del delta.
- **Code block API** como patrón **typewriter** sobre código real del `API_CONTRACT.md` — `via` CSS
  typewriter + cursor cobalt. **Media:** texto real, €0.

### 2.2 MARKETPLACE `/explore` (§3.2)

- **Layout split mapa↔lista** (el diferenciador, ningún competidor lo tiene funcional) como
  **mobile.de (vista mapa) superada** + **3D Product Grid de Codrops feb-2026**
  (`shoe-finder-wine.vercel.app`, arquitectura DOM-filtros + Canvas R3F + tile layer, estado a 60fps
  en `rigState` mutable fuera de React) — `via` ese patrón `rigState`: filtrar por provincia actualiza
  mapa 3D Y grid sin re-render de React del canvas. **Media:** mapa R3F como selector geo + foto real.
- **Filtrado del grid** como **GSAP FLIP de Codrops ene-2026** (`Flip.getState()` → filtro → `Flip.from`
  con stagger random + blur/brightness de tránsito) — `via` GSAP Flip plugin: cards reposicionan
  fluido, las excluidas hacen fade+scale(0.8) in place sin desmontar (evita re-fetch). **Media:** N/A.
- **Hover preview de card** como **Codrops "Animated Product Grid" may-2025** (puzzle clip-path L/R,
  debounce 100ms) — `via` GSAP + CSS clip-path, sin WebGL: hover revela foto extra + precio + km +
  VAM badge flotando sobre el grid, la card NO se expande (0 layout shift). **Media:** foto real.
- **Card→ficha shared element** como **Codrops "Scroll-Revealed WebGL Gallery + Barba" feb-2026** /
  **Motion layoutId** — `via` `motion` (`<motion.div layoutId={'car-'+id}>`) o Flip+Barba: la imagen
  "vuela" del grid al hero del detalle. **Media:** foto real.

### 2.3 FICHA DE VEHÍCULO `/vehicle/:ulid` (§3.3)

- **Hero galería a sangre + rail sticky** como **SilverDrive** (`silverdrive.nl/fleet`, luxury single
  product dark, GSAP+WebGL, tipografía dominante, info densa jerarquizada) + **mobile.de/cars.com
  CTA sticky** — `via` CSS sticky rail + glass overlay (precio oversized en Geist Mono extra-bold).
  **Media:** foto real del anuncio (la galería multi-foto es el activo).
- **Carrusel de fotos** como **Codrops "WebGL Shaders ripple/reveal/blur" oct-2025** (`uMixFactor` GSAP
  blend exterior↔interior, ripple desde click, blur Kawase en planes fuera de foco) — `via` R3F
  ShaderMaterial + GSAP `quickTo`; degradación a CSS transform+crossfade en los primeros resultados.
  **Media:** fotos reales.
- **Timeline de historial (el moat)** como dataviz propia estilo **Carfax dado gratis** + **TradingView**
  — `via` SVG/d3-shape: dots semánticos (NEW→PRICE_CHANGE→PHOTO_CHANGE→KM_CHANGE→GONE) + old→new + Δ.
  **Media:** dato `/vehicles/{ulid}/history`, €0.
- **Reveal de detalle premium (coches alta gama)** como **Higgsfield Exploded View / Bullet Time** —
  `via` clip de Higgsfield Identity-Lock desde la foto real, sincronizado fin-de-clip con aparición de
  specs (GSAP timeline). **Media:** VIDEO generado (FUTURE, spend-gated; solo coches >30k€).

### 2.4 DEALER `/dealer/:cdp` + GARAJE 3D `/dealer/:cdp/garage` (§3.9)

- **Garaje como showroom R3F** como **Otherlife Virtual Car Showroom**
  (`labs.otherlife.xyz/virtual-car-showroom`, cinematic transitions, HDR day→night, car-paint
  interaction) + **Iridescent PBR dual-HDRI** (Three.js forum mar-2026, Inferno/Glacier switch,
  UnrealBloom) — `via` R3F SceneStage: `MeshReflectorMaterial` (suelo espejo) + luz 3 puntos + podium
  emissive + `@react-three/postprocessing` (Bloom/CA/Vignette) + dual-HDRI cobalt-cálido/frío con
  toggle. La foto real del inventario se trata como objeto premium (CarProxy photo-card). **Media:**
  foto real como textura now; GLB real (`generate_3d`) future.
- **Identidad de dealer humanizada** como **Aramisauto** (manager visible, estado abierto/cerrado,
  servicios iconificados) — `via` componente EntityCard + monograma procedural (color hash del nombre).
  **Media:** generada procedural (SVG), logo real si existe; €0.
- **Hover de dealer card** como **Codrops flowmap cursor distortion** — `via` R3F ShaderMaterial
  (iridescence sutil) en desktop; fallback CSS text-shadow cobalt. **Media:** €0.

### 2.5 TERMINAL `/terminal` + INTEL `/intel` (§3.5, §3.4)

- **Densidad Bloomberg sin fealdad** como **GTA VI motion restringido** + **TradingView** — `via`
  dataviz 2D (recharts/D3 con tokens CARDEEP), **NO 3D pesado** (regla §5.4: 3D solo donde demuestra;
  el trabajo repetitivo es 2D). ChartPanel OHLC = delta agregado en buckets. **Media:** dataviz, €0.
- **Heat-map de arbitraje (intel)** como **Indicata más profundo** + bento — `via` bento cards con foto
  real + descuento vs P50 + treemap D3. **Media:** dato + foto real.
- **Hero particle field del delta (intel)** como **Codrops cinematic particles nov-2025** — `via` shader
  R3F (eventos `/delta` → posición/color). **Media:** shader €0.

### 2.6 COBERTURA `/cobertura` (§3.15) — la segunda pieza faro

- **Hero scroll-scrubbing** como **GTA VI opening-map** (audit técnica 2) + **Cinematic 3D Scroll de
  Codrops nov-2025** (ScrollSmoother smooth:4, custom ease `cinematicSilk`, camera path con lookAt
  separado) — `via` GSAP ScrollTrigger pin + scrub:1 sobre `camera.position` del SpainMap: narra la
  construcción del censo provincia a provincia. **Media:** mapa R3F vivo + dato `/geo/seal`.
- **Mapa Europa (expansión)** como **shader radar** — `via` LineSegments GeoJSON Natural Earth + radar
  scan GLSL, ES en cobalt. **Media:** shader €0 (NEAR).

### 2.7 NOTICIAS `/noticias` (§3.13) + NOTIFICACIONES `/notificaciones` (§3.14)

- **Hero editorial + ticker** como **artificial-garage editorial** + marquee cinético — `via` GSAP
  infinite marquee (linear ease, 60px/s, pausa en hover) sobre dato vivo del delta. **Media:** dataviz.
- **Feed SSE con flash de borde cobalt** (notif) como patrón **command-center** — `via` CSS `@property`
  + keyframe de borde. **Media:** €0.

### 2.8 API MARKETPLACE `/pro/api` (§3.12)

- **Hero DataFlow** como **Codrops grain+distortion** — `via` shader R3F (grafo de España + partículas
  de eventos). Tabla pricing anclada 100% al `API_CONTRACT.md` real. **Media:** shader €0 + texto real.

### 2.9 FOOTER (global, en PublicLayout) — pieza de cierre de otro nivel

> El blueprint no le dedica superficie propia; aquí se define como **firma de cierre** coherente.

- **Estructura sticky-reveal** como **Aquerone** (`aquerone.com`, footer enterrado que emerge al
  levantarse el contenido) + **tutorial Oliver Larose sticky-footer** (`blog.olivierlarose.com`,
  método 2: `position:sticky` + `calc(100vh - footerH)`, zero deps) — `via` CSS clip-path/sticky: el
  footer "emerge" debajo del último grid de vehículos = metáfora de descubrir el mercado completo.
  **Media:** €0.
- **Tipografía ancla** como **Antinomy Studio** (`antinomy.studio`, una palabra Helvetica masiva a 15vw,
  cero ornamento) + **Vide Infra** (`videinfra.com`, full-screen + marquee masivo) — `via` `'CARDEEP'`
  en Outfit ExtraBold 12-14vw, hover letra-a-letra fill→stroke cobalt (GSAP SplitText + CSS var
  `--char`). Debajo tagline data-driven (`2.35M ANUNCIOS · 52 PROVINCIAS · ACTUALIZADO HOY`) en mono.
  **Media:** tipografía, €0.
- **Marquee de cobertura** como **Vide Infra marquee** — `via` GSAP ticker loop con datos vivos de la
  API CARDEEP. **Media:** dataviz.
- **CTA magnético circular** como **Vide Infra botón magnético** — `via` GSAP lerp (factor 0.15) +
  spring `elastic.out` + SVG textPath rotante `'EXPLORAR EL MERCADO →'`; fondo cobalt sólido; click →
  page transition con preload de `/explore`. **Media:** €0.
- **Texto-hero distorsionado (opcional, desktop)** como **Thibault Guignand** (`tympanus.net` may-2026,
  GSAP uniform→WebGL bridge, scramble text, chromatic aberration) — `via` R3F ShaderMaterial flowmap
  sobre el texto `'CARDEEP'`; fallback CSS si no hay WebGL. **Media:** €0.
- **Fondo video opcional** como hero loop Higgsfield (charcoal + cobalt, abstracto, velocidad baja) —
  `via` `<video autoplay muted loop playsinline>` + ScrollTrigger parallax. **Media:** VIDEO generado
  (FUTURE, spend-gated). Por defecto: gradient charcoal + shader €0.

---

## 3 · STACK DE MOTION / 3D A AÑADIR

> Base ya instalada: React19 + Vite + `@react-three/fiber` + `three`. Lo siguiente se AÑADE
> (todo gratuito; GSAP es free desde la adquisición Webflow 2025). Patrón: no se rehace el mapa
> R3F existente — se añaden capas.

| Librería | Para qué | Cómo (concreto) |
|---|---|---|
| `gsap` + `@gsap/react` | Toda la coreografía scroll-driven, camera paths, text reveals, FLIP | `useGSAP(cb, {scope:ref})` para cleanup auto en React19; `ScrollTrigger.normalizeScroll(true)` cross-browser; `ScrollTrigger.getAll().forEach(t=>t.kill())` en unmount. |
| GSAP plugins (free): `ScrollTrigger`, `ScrollSmoother`, `SplitText`, `Flip`, `ScrambleText`, `Observer`, `Draggable` | Pin/scrub, smooth, line-mask reveal, filtrado de grid, footer scramble, snap narrativo, garaje drag | `gsap.registerPlugin(...)`. `ScrollSmoother.create({smooth:4, effects:true})` para sensación de cámara flotante. `SplitText.create({mask:'lines'})` (3.13+, `autoSplit/observeChanges` para resize). |
| `lenis` (`@studio-freight/lenis`) | Smooth scroll inercial global, base que hace TODO más premium | `new Lenis()`; `gsap.ticker.add(t => lenis.raf(t*1000))`; `lenis.on('scroll', ScrollTrigger.update)`. Reemplaza scroll nativo en `PublicLayout`. |
| `@react-three/postprocessing` + `postprocessing` | Capa cinematográfica sobre el canvas R3F existente | `<EffectComposer><Bloom luminanceThreshold={0.85} intensity={0.3}/><Vignette/><DepthOfField/><ChromaticAberration/></EffectComposer>`. <50 líneas, efecto inmediato en el hero. |
| `@react-three/drei` | Helpers: suelo espejo garaje, HDRI, GLTF, shaderMaterial tipado | `MeshReflectorMaterial`, `Environment preset='studio'`, `useGLTF` (+ DRACOLoader), `shaderMaterial()`+`extend()`, `useVideoTexture`, `<Text>` (troika SDF) para labels 3D del mapa con Outfit WOFF2. |
| `vite-plugin-glsl` | Importar `.glsl/.vert/.frag` sin inline strings | Para shaders de car-paint (Voronoi flakes + Fresnel + clearcoat), grano, distorsión scroll, partículas del delta. |
| `glsl-noise` | Funciones Perlin/Simplex/Voronoi para los shaders | Grano cinematográfico, car-paint flakes, ambiente. |
| `motion` (ex framer-motion) | Shared-element card→ficha (`layoutId`) sin configurar posiciones | Solo donde Flip es overkill; coexiste con GSAP. |
| `r3f-perf` (dev) | Monitor FPS/GPU para mantener 60fps + adaptive quality | Degradar pixelRatio/shadow map si FPS<30 (crítico, >50% tráfico mobile). |

**Reglas de oro (heredadas del blueprint §5.3/§5.4):** solo `transform`/`opacity`/`clip-path`/`filter`;
`will-change` solo justo antes y removido al terminar; stagger 40ms/item máx 5 visibles;
`prefers-reduced-motion` → todo a opacity-only 20ms (GSAP `matchMedia`); chunk Three.js lazy.

---

## 4 · BRIEF DE MEDIA HIGGSFIELD

> **Prioridad #1 absoluta: UN hero animado de coche.** El resto es batch posterior con luz verde del
> owner (todo el producto es 100% funcional con dato real + shaders €0 sin este gasto — §4 blueprint).
> Prompt de marca normalizado (prefijo a TODOS los clips para coherencia cross-inventory):
> *"dark studio, cobalt blue ambient fill (#3B82F6), deep charcoal shadow zones, white specular on
> chrome, 35mm grain, halation on headlights, cool blue-grey color grade, identity locked, slow reveal."*

### 4.1 HERO ANIMADO (prioridad #1) — "Cobalt Reveal"

- **Pipeline:** (1) `generate_image` (Higgsfield Soul / Nano Banana Pro) para fijar composición y luz →
  (2) `outpaint_image` si hace falta encuadre 16:9 → (3) `generate_video` con **Seedance 2.0** (base,
  identity-lock + multi-ref) → (4) `upscale_video` a 4K → (5) `reframe` a 9:16 para variante mobile.
  Antes de generar: `models_explore(action:'recommend')` con la foto/objetivo para confirmar modelo.
- **Modelo recomendado:** **Seedance 2.0** (image-to-video, identity-lock best-in-class, 4K, hasta 15s,
  audio nativo). Alternativa para acción dinámica: **Kling 3.0**. Alternativa exterior/atmósfera:
  **Veo 3.1**.
- **Aspect ratio:** 16:9 1080p→4K (hero desktop) + variante 9:16 1080p (mobile/social).
- **Duración:** 8-12s, loop limpio.
- **PROMPT (copiar/adaptar por coche del inventario):**
  > *Cinematic commercial shot. Slow 270-degree orbit at hood height, gradual dolly-in to front badge.
  > [MARCA] [MODELO] [COLOR], metallic paint with cobalt blue ambient reflections. Wet urban night,
  > rain-slicked dark asphalt, distant city bokeh. Chiaroscuro lighting: cobalt blue fill (#3B82F6)
  > from left, deep charcoal shadow zones, sharp white specular on chrome trim. 35mm grain, halation
  > on headlights, anamorphic lens flares. Ultra-realistic 4K, 24fps with slight motion blur. Shot on
  > ARRI Alexa Mini LF. One continuous take, no cuts.*
- **Logo CARDEEP:** NO se incrusta en el video (el activo de marca `/brand/cardeep-icon-blue.png` +
  wordmark se compone en la capa DOM/R3F encima del video, nunca regenerado — §4 blueprint). El video
  es fondo atmos `opacity` baja; el wordmark Outfit + el mapa 3D van como overlay nítido.
- **Integración web:** `<video autoplay muted loop playsinline poster="frame.avif" preload="metadata">`
  con cadena de codecs AV1→VP9→H.264 (FFmpeg: `-an` strip audio, AV1 `libsvtav1 -qp 30`, H.264
  `-crf 23 -preset veryslow`, `-movflags +faststart`); poster AVIF <80KB con
  `<link rel=preload as=image fetchpriority=high>`; fallback mobile/`prefers-reduced-motion`/2G → poster.
  Target hero loop <3MB AV1 / <6MB H.264; LCP <2.5s.

### 4.2 BATCH POSTERIOR (NEAR/FUTURE, spend-gated)

| Asset | Modelo | Prompt (núcleo, + prefijo de marca) | AR | Dónde |
|---|---|---|---|---|
| 7 category-art por `EntityKind` | Seedance 2.0 / Soul image | Escena cinematográfica representativa del kind (concesionario / compraventa / garaje / desguace / plataforma / subasta / particular), dark studio cobalt | 16:9 | EntityCard, ficha dealer |
| 8 base de categoría noticias | Soul image | 1 por categoría editorial (mercado / releases / insights / arbitraje), abstracto cobalt | 16:9 | `/noticias` feature/grid |
| Reveal Exploded-View (alta gama) | Seedance 2.0 | `[MARCA MODEL] body separates from chassis, components float in sequence, studio lighting, slow-mo, dark cobalt background` | 16:9 | ficha vehículo >30k€ |
| Footer loop atmos | Veo 3.1 / Kling 3.0 | conducción nocturna ciudad ES, abstracto, velocidad baja, cobalt reflections | 16:9 | footer fondo |

---

## 5 · PLAN DE EJECUCIÓN DEL HERO FARO (orden Awwwards)

> Construir el hero de la Landing `/` a nivel Awwwards, sobre el `SpainMap.tsx` existente. Orden
> estricto (cada paso verificado antes del siguiente). €0 hasta el paso 8.

1. **Base de scroll premium.** Instalar `gsap` + `@gsap/react` + `lenis`. Montar Lenis en
   `PublicLayout`, conectar a `gsap.ticker` y `ScrollTrigger.update`. Verificar: scroll inercial suave,
   `prefers-reduced-motion` desactiva la inercia. (Hace TODO más premium sin tocar nada más.)
2. **Topbar cinematográfico.** Transparente en `scroll=0` (el mapa pasa por detrás) → glass al
   `scrolled>64px` (transición 260ms). Verificar contraste y legibilidad sobre el 3D.
3. **Capa postprocessing sobre el mapa.** Añadir `@react-three/postprocessing` al canvas existente:
   Bloom selectivo (threshold 0.85, strength 0.3) en provincias SELLADO, Vignette perimetral,
   ChromaticAberration leve. Verificar 60fps con `r3f-perf` en gama media; adaptive quality si <30.
4. **Headline kinético.** GSAP SplitText line-mask reveal del titular on-load + cylinder rotation en
   `'VIVO'`. `document.fonts.ready` antes de split; `split.revert()` en cleanup; `observeChanges` para
   resize. Verificar sin huérfanos en HMR.
5. **KPIs scroll-scrub + countUp.** Word-by-word reveal de las 4 cifras vivas al ritmo del scroll,
   número en cobalt. Verificar `tabular-nums` (sin salto de ancho) y dato real de `/stats`.
6. **Scroll-storytelling del censo.** ScrollTrigger pin + ScrollSmoother sobre `camera.position` del
   SpainMap: provincia a provincia se enciende (scrub:1, ease `cinematicSilk`), lookAt interpolado en
   `useFrame`. Labels 3D de provincia con drei `<Text>` (Outfit WOFF2). Verificar sincronía scroll↔cámara
   y `matchMedia` (mobile sin pin pesado).
7. **Atmósfera shader.** `vite-plugin-glsl` + partículas bokeh/polvo (`THREE.Points`, momentum*decay) +
   grano Simplex 8-12% sobre el canvas. Verificar coste GPU y que no compite con el dato.
8. **(Opcional, spend-gated) Video Higgsfield de fondo.** Generar el hero "Cobalt Reveal" (§4.1),
   encode AV1→VP9→H.264 + poster AVIF, montar como capa atmos `opacity` baja detrás del mapa, fade-in
   por Lenis scroll progress. Solo con luz verde del owner.
9. **Auditoría final del hero.** LCP <2.5s (poster preload), CLS 0 (`aspect-ratio` declarado),
   `prefers-reduced-motion` (todo opacity-only), 60fps en mobile (adaptive), screenshots 320/768/1440,
   degradación elegante sin WebGL. Solo entonces se declara faro.

---

**Cierre.** Concepto rector sellado, cada superficie hereda una fuente distinta con técnica y media
declaradas, stack de motion concreto y €0 por defecto, brief Higgsfield priorizando UN hero animado, y
plan de ejecución del faro paso a paso. Marca fiel (cobalt/charcoal/white/Outfit), dato real como media,
gasto diferido a luz verde del owner. Coherente con el blueprint E2E y el audit competitivo.
