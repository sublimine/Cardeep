# Landing pública (`/landing`) — rediseño con 3D, marketplace e inteligencia

> Encargo del owner 2026-07-16: llevar `/landing` "a otro nivel", menos ruido,
> visualmente perfecto; auditar qué hacen las 109 empresas auditadas
> (`plans/intel-audit/`) y el estudio de marketplace (`docs/frontend/04-COMPETITIVE-UX-AUDIT.md`)
> para decidir qué implementar; dar visibilidad real a marketplace e inteligencia;
> usar 3D/Three.js para inmersión — explícitamente NO el mapa 3D de España (ese
> vive solo en `/explore`/`/cobertura`, decisión ya tomada y confirmada por el
> owner con dureza durante esta sesión). Ejecución autorizada "hands off",
> sin más rondas de aprobación tras confirmar la dirección 3D-sí/mapa-no.

## Contexto real encontrado (no lo que decían los docs viejos)

- El landing vivo NO era el hero cinematográfico oscuro de
  `docs/frontend/05-CINEMATIC-ART-DIRECTION.md` (23-jun, superado). Era un mirror
  estático (`dangerouslySetInnerHTML`) de `portal/index.html`: hero claro con
  vídeo de fondo, sin Three.js pese a tener `three`+`@react-three/fiber`+`@react-three/drei`
  instalados y sin usar en ningún sitio del árbol.
- `plans/frontend-definitivo/` (activo, actualizado el mismo día 16-jul) confirma
  que el sistema claro/General Sans/flat es la referencia viva del proyecto — el
  propio owner lo usó hoy para corregir el Dashboard. No se pivotó a oscuro.
- Dos estudios distintos, ambos reales: `docs/frontend/04-COMPETITIVE-UX-AUDIT.md`
  (15-18 marketplaces de coches) y `plans/intel-audit/` (109 empresas de datos/
  inteligencia de automoción — Indicata, GANVAM, JATO, Autovista, CARFAX...,
  síntesis en `CARDEEP-OFFERING.md` + `PLACEMENT-MAP.md`, 1.353 patrones).
- No existe endpoint real de valoración (`grep` vacío en `services/api/routers`);
  `Inteligencia.tsx` corre sobre datos mock. Cardex/PLACEMENT-MAP sí valida 3
  patrones honestos y replicables: contador de confianza en hero (Datium),
  widget de valoración instantánea en home (Motorway/AutoTrader UK) y preview
  "semáforo" sin contenido (autoDNA) — este último es el único que no exige
  inventar un número, así que es el que se implementó.
- API real viva en `:8090` (verificado por curl): `/stats` (dealers 18.967,
  vehículos 1.576.673, 52 provincias) y `/geo/seal` (cobertura venta 79,7%).
  Nunca antes consumida por ninguna página del app rehecho (`frontend-definitivo`
  corre 100% en mock hasta este cambio).

## Decisión de diseño

1. **No pivote de sistema de diseño.** Se evoluciona el light/General Sans/glass
   ya vigente; no se reabre el mapa 3D ni se vuelve a la dirección oscura de junio.
2. **3D sí, no-mapa.** Hero con una escena R3F propia (`IndexCore`): icosaedro con
   `MeshTransmissionMaterial` + shell wireframe, reactivo a scroll/mouse, lazy-
   loaded (chunk propio, fuera del bundle inicial). Metáfora deliberada del
   titular ("índice vivo"), no decoración genérica — €0, sin generación de
   assets ni coche con licencia/IA.
3. **Cero datos inventados.** Se sustituyen los 4 números hardcodeados del mirror
   estático (incluida la etiqueta incorrecta "fuentes vivas" sobre el conteo de
   dealers, y dos cifras sin respaldo real: "+142 altas hoy", "27 mercados UE")
   por 4 cifras reales de `/stats`+`/geo/seal`. Sin valoración instantánea falsa:
   en su lugar, teaser honesto con `PremiumGate`/`entitlements.ts` ya existentes
   (Capa 0 libre vía `/check` real; Capa 1/2 gateadas, mismo mecanismo que ya usa
   el resto de la app tras login).
4. **Visibilidad marketplace + inteligencia** vía: bento reordenado (Índice
   nacional con cifra real, Historial, Inteligencia, **Arbitrage** — sustituye
   "Garaje 360°", que no tenía ruta real —, Finanzas) + banda comparativa
   "100% del mercado vs. inventario parcial" con la cobertura real.
5. **Menos ruido**: eliminados `pages/landing-sections.tsx` (741 líneas, 0
   imports), toda la carpeta `pages/landing/` de la era DeFi (`Cursor.tsx`,
   `Preloader.tsx`, `ShaderBackground.tsx`, `useLenis.ts`, 0 referencias), los
   orbes de `GlobalMesh` en `App.tsx` (ocultos por una regla CSS `!important`
   global desde antes de esta sesión — dead en todas las rutas, confirmado
   leyendo `tokens.css`), y `pages/portal/landingPortal.ts` (huérfano tras migrar
   `Landing.tsx` a React real).

## Bugs reales encontrados y corregidos durante la verificación

- Ruta de imagen rota (`/assets/cd-icon.png`, no existe en `web/public/`; el real
  es `/uploads/cd-icon.png`) — causaba un 404 real, cazado con Puppeteer
  (Playwright estaba ocupado por otro agente; Obscura resultó incompatible con
  la ejecución de módulos ES de esta SPA incluso en rutas no tocadas como
  `/login` — descartado como herramienta válida para esta verificación).
- `CountUp` gateado por `IntersectionObserver` con umbral 60% dejaba los 4 KPIs
  de la franja de confianza mostrando un "0" indistinguible de un dato real
  cuando la sección no había entrado aún en viewport (medido, no intuido).
  Corregido: anima al montar, sin gate de scroll.
- El 4º teaser de inteligencia (`micro-geo-detail`) desbordaba su tarjeta:
  el contenido del overlay de `PremiumGate` (166px) no cabía en la tarjeta
  difuminada que lo sostenía (62px), y al no haber `overflow:hidden` en el
  contenedor, el overlay se salía visualmente sobre la fila de arriba.
  Corregido con `min-h` + layout vertical en la tarjeta base.
- Barra de filtro del hero desbordaba el texto del botón "Ver coches" en 390px
  de ancho. Corregida a diseño responsive (2 selects + botón ancho completo en
  móvil, 3 selects + botón en fila desde `sm:`).

## Fuera de alcance (detectado, no tocado)

- Bundle principal de `index-*.js` ~1,23 MB / 342 KB gzip — preexistente (todas
  las páginas de la app se importan de forma estática en `App.tsx`, sin
  `React.lazy` por ruta). No es un problema introducido por este cambio ni
  parte del encargo; requeriría tocar el router de toda la app.
- 404 de `favicon.ico` — preexistente en todo el sitio, no específico de `/landing`.
- Sin menú hamburguesa en nav móvil (los links Marketplace/Inteligencia/Historial
  se ocultan bajo `md:`) — decisión deliberada de foco en el CTA principal, no
  un olvido, pero queda como mejora futura si el owner la quiere.
- Cambios en paralelo de otro agente en `src/api/cardeep.ts` (tipos de
  delta/platforms) detectados sin tocar — no son de este trabajo.

## Verificación

`tsc --noEmit` + `vite build` verdes · render real contra API viva (`:8090`)
verificado con Puppeteer (Playwright ocupado por otro proceso del propio owner)
en 1440/768/390px · consola sin errores propios (solo el favicon 404 preexistente)
· light y dark verificados visualmente · `prefers-reduced-motion` respetado en
`HeroScene`, `Reveal` y `CountUp`.
