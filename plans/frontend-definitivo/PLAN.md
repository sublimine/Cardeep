# cardeep · Frontend definitivo — PLAN

> Goal owner (2026-06-30): UN frontend definitivo, institucional, 100% funcional. Unificar los dashboards y
> secciones repartidos en 3 "portales" (portal/ diseño · TailAdmin · Spike) + la app real `web/` en UNA sola
> plataforma. Estilo = **el landing** (`portal/index.html`: General Sans, claro #EAECEF, minimal elegante,
> #3B82F6). Login-gated: landing pública → al entrar, todo (info, inteligencia, dashboards, arbitrage).
> Sistema de venta de APIs por tokens (info + inventario). Dealer-first: lo más relevante arriba, el resto
> accesible sin ruido. Integrar la auditoría de inteligencia/arbitrage ya hecha. Cero ruido, cero caos.

## Decisión de arquitectura (verificada en recon)
- **Construir en `web/`** (Vite+React+Router+Tailwind, app real con auth/components/hooks/api ya hechos y CI
  verde). NO se reescribe lo funcional; se REUTILIZA.
- **Re-skin al landing** a nivel design-system (cascada por tokens, no por archivo).
- `portal/` (diseño estático, mi arbitrage/inteligencia, TailAdmin/Spike) = **fuente de contenido/placement**,
  no destino. El landing `portal/index.html` = ancla de estilo (se porta a `web/` como `Landing`).
- Datos: UI 100% funcional con la capa de datos existente (catalog + hooks); cablear `:8090` cuando el owner
  abra el stack (gate). No inventar cifras DeFi (memoria: "do NOT ship DeFi figures").

## Norte de diseño (del landing — VERIFICADO leyendo portal/index.html)
- Tipografía: **General Sans** (400-700) display/UI + **JetBrains Mono** para dato/número (tabular-nums).
- Paleta light (def.): `--bg #EAECEF · --panel #FFFFFF · --panel2 #F1F3F6 · --ink #13161B · --ink2 #5E6470 ·
  --ink3 rgba(19,22,27,.4) · --line rgba(20,28,40,.09) · --mint #3B82F6 · --mint2 #E8F0FE · --ctl #111827`.
- Dark (del landing): `--bg #0B0D11 · --panel #15181F · --ink #F3F2EC · --mint #5B96F8 · --ctl #F3F2EC`.
- Superficies **flat-limpias**: panel blanco, borde 1px sutil, `shadow-sm 0 14px 34px -18px rgba(38,46,62,.24)`,
  radios 18-24px. Glass SOLO donde el landing lo usa (nav flotante, barra de filtro). **Sin mesh de orbes en
  páginas de app.** Microinteracción: `cd-press` (hover -2px, active .98), reveals `cdUp` con IntersectionObserver.
- Principio: minimalismo = precisión. Jerarquía por escala/espacio, no por ruido.

## Bloques (ejecución secuencial, cada uno verificado: build + Playwright + light/dark + 0 errores consola)

### B0 · Baseline congelada
- `npm --prefix web ci` (o install) + `npm --prefix web run build` verde ANTES de tocar → baseline.
- Screenshots Playwright del estado actual (dashboard/market/terminal) como referencia anti-regresión.

### B1 · Design-system → landing (FUNDACIÓN, cascada global)
- `web/src/styles/tokens.css` + `index.css`: General Sans (fontshare) + JetBrains Mono; repaletar light a la
  neutra del landing; **light por defecto** (html.light o root); aplanar `.glass/.card/.bezel` a panel+borde+
  shadow-sm del landing; neutralizar `GlobalMesh` (App.tsx) → fondo flat del landing (mantener hook dark).
- `tailwind.config.js`: fontFamily.sans = General Sans; alinear tokens si hace falta.
- Criterio: build verde; dashboard/market renderizan en estilo landing (claro, flat, General Sans); dark OK.

### B2 · Shell + navegación unificada (un solo sitio)
- `layout/Shell.tsx`: sidebar/topbar en estilo landing; agrupar secciones con lógica (no ruido); logo+nav del
  landing; theme toggle; command palette (ya existe SearchCommand) + NotificationBell. Dealer-first.
- Criterio: toda sección accesible desde un sitio; coherente con landing; responsive (sidebar→drawer móvil).

### B3 · Landing pública (la limpia) + Login
- Portar `portal/index.html` → `pages/Landing.tsx` (hero índice vivo, trust strip, bento "todo el ciclo", CTA),
  React + framer-motion suave. Retirar la DeFi (ShaderBackground/Preloader/Cursor) o archivarla.
- `auth/LoginPage.tsx` re-skin landing; flujo 100% funcional (ya hay AuthContext/ProtectedRoute).
- Criterio: `/` no-auth = landing limpia; login entra a `/dashboard`; estilo landing.

### B4 · Dashboard ÚNICO dealer-first (unifica los 4)
- Unificar contenido de: portal `dashboard.html` + TailAdmin (analytics/ecommerce/crm) + Spike + `web/Dashboard`.
- Orden dealer-first (lo que decide primero): **(1)** salud del stock + KPIs (margen, días-stock, valor parado),
  **(2)** oportunidades/arbitrage (deal-score top, chollos), **(3)** mercado/precio-position + delta, **(4)**
  pipeline/deals, **(5)** finanzas resumen, **(6)** actividad/alertas. Lo secundario → tras un clic, no en la cara.
- Criterio: una sola pantalla, sin ruido, jerarquía clara, datos de inteligencia integrados.

### B5 · Secciones end-to-end (unificar variantes, 100% funcional)
- Inventario/Marketplace (web `Vehicles` + `Market` + portal marketplace) · CRM (Contacts/Deals/Kanban) ·
  Finanzas · Inbox · Calendar · **Inteligencia** (web `Terminal/Intel` + mi MATRIX/PLACEMENT/OFFERING) ·
  **Arbitrage** (web `Terminal/Arbitrage` + mi ARBITRAGE.md: deal-score/sourcing/cross-platform/spread/time) ·
  VIN Check/Dossier · Settings/Perfil. Cada una en estilo landing, contenido unificado, navegable.
- Criterio: cada sección completa, sin huecos, coherente, verificada en navegador.

### B6 · API & Tokens (NUEVO — venta de info + inventario por API)
- Sección `pages/Api.tsx` (ruta `/api-tokens` o `/developers`): catálogo de endpoints (info: valoración,
  historial, market-intelligence, deal-score; inventario: feed de stock), **medición por tokens** (saldo,
  consumo, planes/recarga), API keys (crear/rotar/revocar), docs/ejemplos, uso reciente. Modelo de pricing por
  tokens. Estilo landing. (UI funcional; emisión real de keys/cobro = gate backend/owner.)
- Criterio: pantalla institucional de "vender APIs por tokens" coherente con la oferta de `CARDEEP-OFFERING.md`.

### B7 · Auditoría final + parte
- Barrido de regresiones (build, typecheck, todas las rutas render, light/dark, responsive 390/768/1280,
  0 errores consola), CI verde, commit por bloques. Parte de entrega.

## Criterios de aceptación (la puerta de finalización)
- [ ] `web` build + typecheck verdes; CI 6/6 verde.
- [ ] Estilo landing coherente en TODA la app (General Sans, flat-limpio, #3B82F6, light+dark).
- [ ] Un solo sitio: landing pública → login → app con todas las secciones; sin "3 portales".
- [ ] Dashboard único dealer-first, sin ruido, jerarquía con lógica.
- [ ] Inteligencia + arbitrage integrados desde la auditoría real.
- [ ] Sección API-por-tokens (info + inventario).
- [ ] 0 errores consola; responsive; render verificado Playwright por sección.

## Verificación por bloque
build (`npm --prefix web run build`) + typecheck + Playwright (screenshot + console.errors==0, light & dark) +
commit. Nunca declarar un bloque sin su verificación.
