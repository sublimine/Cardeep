# RIVR DeFi — Auditoría átomo + dirección de réplica/integración

> **Goal del owner (2026-06-27):** *"Borra la landing actual. TODO y replica e integra de manera
> impecable y a nivel átomo este recurso de a→z. TODO!"* — recurso:
> `https://motionsites.ai/?prompt=rivr-defi-landing` (item **"RIVR DeFi · Landing Page"**, premium).
>
> Auditado con **navegador real** (Playwright), no WebFetch. El template es gated; se reconstruye
> (no se clona código): replicamos estructura + estética + motion + calidad, e **integramos** el
> contenido y la marca CARDEEP. €0 (sin media de pago).

## 1 · Qué es el recurso
Landing **DeFi light-luxury** de MotionSites. Estética: fondo claro/off-white, **render 3D surreal
"fluid/liquid"** (columnas, esfera dorada, sofá bouclé, esferas cromadas, rocas sobre agua y
montañas brumosas — paleta azul-fría + dorado), tipografía **editorial grande** (grotesca, peso
medio, tracking negativo, gris-charcoal), glass sutil, mucho aire. Motion firma MotionSites:
smooth-scroll (Lenis), reveals escalonados, render con flotación/parallax, countUp en stats.

Asset disponible en repo: `web/public/landing-rivr-scene.png` (render exacto del estilo, "Fluid
Asset Streams") + `web/public/landing-rivr-bg.mp4`. Se reutilizan como backdrop del hero (€0).

## 2 · Estructura átomo (hero → footer)
1. **Nav** — logo izq · links centro (Ecosystem/Economics/Developers/Governance) · CTA pill der ("Book Demo", flecha ↗). Transparente arriba → glass al scroll.
2. **Hero** — eyebrow pill ("Fluid Staking") · **H1 editorial gigante** ("Fluid Asset Streams") · subcopy 2 líneas · render 3D a sangre detrás · stat flotante glass abajo-izq ("5.2K Active Yielders" + "Join Discord") · enlace "Documentation" abajo-der.
3. **Stats row** — 4 métricas grandes con sublabel: `$2.4B · 8.5% · 140K+ · <2s`.
4. **"Architected for high-performance DeFi"** — título de sección + **bento de cards glass**: "Real-time Yields" (card grande con mini-mockup UI), "Unlock the liquidity of your staked assets", "Smart contracts audited by leading firms", etc.
5. **CTA band cinematográfico** — imagen paisaje atardecer + **H2 editorial** ("Melt rigid assets into fluid yield.") + botones ("Launch App").
6. **Footer** — wordmark + columnas de links sobre fondo claro.

## 3 · Mapping de integración → CARDEEP (dato real, censo del coche)
| RIVR DeFi | CARDEEP |
|---|---|
| "Fluid Asset Streams" | **"El mercado del coche, líquido."** (metáfora de liquidez conservada) |
| "transform rigid holdings into liquid cash" | "Indexamos, verificamos y deduplicamos el inventario vivo de cada punto de venta." |
| Stats $2.4B / 8.5% / 140K+ / <2s | **2.378.534 coches · 450.647 dealers · 52 provincias · delta <2s** (cifras reales DB, countUp) |
| "Architected for high-performance DeFi" | **"Arquitectura de un censo de alto rendimiento"** → cards: Inventario vivo · Delta completo (altas/bajas/Δprecio/Δfoto) · Verificación VAM · Cobertura certificada |
| "Melt rigid assets into fluid yield." | **"Convierte un mercado opaco en dato líquido."** + CTA "Explorar el censo" / "Acceso API" |
| Footer RIVR | Footer CARDEEP (wordmark + Producto/Cobertura/API/Empresa) |

Datos: por orden del owner se **mantienen los ficticios/demo** donde no haya endpoint; las cifras
del hero/stats usan los counts reales ya verificados (DB viva). Cada botón con lógica (no decorativo).

## 4 · Marca + tokens (reconcilia "replica el recurso" + marca CARDEEP)
- Base **light-luxury** (fondo `#eef1f6`/off-white, charcoal `#111B27` texto) — fiel al recurso.
- **Acento de acción = cobalt `#3B82F6`** (`--c-violet` en `tokens.css`; CTAs/badges). El dorado del
  render se conserva como matiz premium secundario. **Prohibido violeta/magenta/cian como CTA**
  (el `gradient-text` heredado NO se usa).
- Glass: sistema existente (`--glass-*`, `.glass`, light-mode ya definido).
- Tipografía: **Inter variable** (ya cargada) peso 300–600, tracking negativo, escala editorial
  `clamp()`; mono JetBrains para cifras (`tabular-nums`).

## 5 · Motion
Lenis smooth-scroll (`web/src/pages/landing/useLenis.ts`, ya existe) · framer-motion reveals
(stagger 60–90ms, `--ease-out-expo`) · parallax del render en el hero · countUp en stats ·
hover refinado en cards/CTAs. **Solo transform/opacity/clip-path/filter.** `prefers-reduced-motion`
respetado en todo.

## 6 · Plan de construcción (rama `feature/landing-rivr-defi`)
1. ~~Auditar recurso (navegador real)~~ ✅ (este doc).
2. Borrar/reemplazar landing actual (`Landing.tsx` dark + `landing-sections.tsx`).
3. Hero (nav + render parallax + H1 editorial + stat glass + CTAs cobalt).
4. Stats row (countUp, cifras reales).
5. "Arquitectura" bento de cards glass.
6. CTA band cinematográfico + Footer.
7. Verificar: navegador real (vs original), build `tsc + vite`, responsive 320–1440, `prefers-reduced-motion`, consola limpia.

Stack: React 18 + framer-motion + lenis + CSS tokens. **Sin three.js** (render pre-hecho = €0, fiel a MotionSites).
