# CARDEEP — Frontend (Three.js) · Plan de ejecución

> `/goal` 2026-06-16: plataforma end-to-end, 100% funcional, impecable, Three.js. Contenido visual
> a mi criterio ("sorpréndeme"). Informado por: (1) auditoría UX de competidores (workflow
> `wxhwop5f9`), (2) tablero Pinterest del owner (tras login — inaccesible vía fetch; carta blanca).
> Roadmap del owner: **FASE actual = front end**; **DESPUÉS = capa de inteligencia** (estilo
> Indicata/GANVAM: valoración, pricing, analítica de mercado) — la arquitectura NO se cierra a eso.

## Visión (la decisión de dirección — D4 autoridad total)
**CARDEEP = el marketplace 3D-first del mercado de coches de España.** El héroe es literal a tu frase
("el mapa completo de un mercado que nadie tiene entero"): un **mapa 3D navegable de España** que
desciende país▸provincia▸comarca▸ciudad▸dealer, fundido con la **funcionalidad de marketplace**
(buscar/filtrar/listar/detalle) adaptada de los líderes (mobile.de/AutoScout/coches.net). No es decoración:
el 3D ES la navegación + la identidad; el marketplace ES el producto usable.

## Stack (decidido)
- **Vite + React + TypeScript** — base moderna, HMR, build optimizado.
- **react-three-fiber (R3F) + @react-three/drei** — Three.js declarativo (R3F ES Three.js por debajo;
  la opción mantenible para una app data-viz, no un `<script>` monolítico). + postprocessing para el acabado.
- **TanStack Query** — estado de servidor (la API CARDEEP), cache, stale-while-revalidate.
- **CSS con design-tokens** (custom properties) — look bespoke, anti-plantilla; cero "Tailwind por defecto".
- **maplibre/d3-geo + topojson** sólo para proyectar el GeoJSON de provincias ES → geometría extruida en Three.

## Datos / integración (end-to-end real)
La API CARDEEP ya existe (FastAPI, `services/api`). El front consume:
- `/geo/seal` → cobertura por provincia (héroe 3D: altura/color).
- `/geo/{prov}[/{muni}]/entities` + `/geo/{prov}/tree` → drill-down.
- `/entities/{cdp}` · `/inventory` · `/delta` · `/canonical` → dealer + su stock + historial.
- `/stats` · `/vehicles/{id}` · `/platforms/{cdp}/inventory`.
Estrategia dev: levanto la API local (uvicorn contra `cardeep-pg`) + el front pega a `localhost`;
fallback de snapshot JSON estático para el viz geo si la API no está arriba. **Cliente API tipado** (genera
tipos del envelope `{ok,data,error,meta}`).

## Estructura (carpetas — mandato "organización masiva")
```
web/
  src/
    api/          cliente tipado + hooks TanStack Query
    three/        escena, mapa 3D España, materiales/shaders, cámara, controles
    components/   ui/ (botones, cards, panels) · map/ · search/ · detail/
    routes/       landing(héroe 3D) · explore · dealer/[cdp] · vehicle/[id]
    styles/       tokens.css · typography.css · global.css
    lib/          geo (topojson ES), color, animación
    hooks/
  public/         geojson provincias/comarcas ES, fuentes, hero assets
docs/frontend/    00-PLAN · 01-COMPETITOR-AUDIT(synthesis) · 02-DESIGN-SYSTEM · 03-3D-SPEC
```

## Fases (gate binario — no se pasa sin verde + verificación)
- **P0 · Scaffold** — Vite+R3F+TS, estructura, tokens base, cliente API tipado, dev contra API local. [HOY]
- **P1 · Síntesis de diseño** — del workflow de auditoría → `02-DESIGN-SYSTEM.md` (paleta, tipografía,
  componentes, layout) + `03-3D-SPEC.md` (mapa España: proyección, extrusión, cámara, interacción, motion).
- **P2 · Héroe 3D** — mapa de España navegable (provincias extruidas por cobertura, drill-down, dealers).
- **P3 · Marketplace** — buscar/filtrar (facetas adaptadas de competidores) + grid de resultados (cards).
- **P4 · Detalle** — página dealer + página vehículo (PDP: galería/specs/precio/delta/CTA), patrón competidores.
- **P5 · Acabado** — motion, postproceso, responsive (320→1920), reduced-motion, performance (CWV).
- **P6 · Verificación** — E2E (Playwright), visual regression, a11y, Lighthouse; CI; clasificar en GitHub.

## Principios (anti-tontería)
Dirección específica + opinionada (no "clean minimal" genérico) · jerarquía por contraste de escala ·
profundidad real (3D, capas, motion que clarifica) · paleta semántica · estados hover/focus/active diseñados ·
coherencia total. Performance: animar solo transform/opacity, lazy-load del 3D pesado, presupuesto de bundle.
Verificación en cada fase (no confiamos en ningún resultado).

---

## Estado (vivo) — 2026-06-16
> Nota de reconciliación: la síntesis de diseño se consolidó en **un solo** `01-DESIGN.md`
> (auditoría de competidores + dirección + paleta/tipografía), no en `02/03` separados como
> listaba la estructura. El `03-3D-SPEC` se redacta al entrar en P2 (con el GeoJSON ya sorteado).

- **P0 · Scaffold — ✅ HECHO y verificado.** Vite+React+TS+R3F/drei/postprocessing+TanStack
  Query+react-router+d3-geo/topojson instalados. Estructura `src/{api,components,routes,styles}`.
  Cliente API tipado (`api/client.ts` envelope `{ok,data,error,meta}`, header `X-API-Key`, modo
  público) + tipos (`api/types.ts`, contrato verificado contra `services/api/routers/ops.py`) +
  hooks TanStack (`api/hooks.ts`). Defaults del scaffold y assets sin referenciar eliminados.
  **Verificación:** `tsc -b && vite build` verde (76 módulos · JS 102 KB gzip base · CSS 3 KB gzip);
  render comprobado por Playwright (desktop 1440) — shell + héroe + tira de métricas; camino
  degradado de `/stats` (API apagada → fallback "Última instantánea") confirmado, sin errores reales.
- **P1 · Síntesis de diseño — ✅ HECHO.** `01-DESIGN.md` + implementado en `styles/tokens.css` +
  `styles/global.css` (dark command-center, cian de firma, tipografía Clash Display/Inter/JetBrains
  Mono cargada en `index.html`). Shell renderable: `components/Layout.tsx` + `routes/Landing.tsx`.
- **P2 · Héroe 3D — ▶ SIGUIENTE.** Pendiente: (1) sortear GeoJSON/TopoJSON de provincias ES →
  `public/geo/` (hoy vacío); (2) `03-3D-SPEC.md`; (3) escena R3F del mapa de España extruido por
  cobertura (`/geo/seal`), drill-down, dealers. Lazy-load del bundle 3D.
- P3–P6 — pendientes (ver fases arriba).

**Dev local:** `npm --prefix web run dev` → `http://localhost:5173`. El cwd del shell PowerShell es
`…\cardeep\web`. La API (para datos en vivo) se levanta aparte con uvicorn contra `cardeep-pg`.
