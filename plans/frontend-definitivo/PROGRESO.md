# Frontend definitivo — PROGRESO
> Estado por bloque. Se actualiza al cerrar cada uno. Verdad cruda: solo [x] con verificación real.

- [x] **B0** Baseline — typecheck limpio + build ✓ 14.58s (2900 módulos). node_modules presente.
- [~] **B1** Design-system → landing — **REABIERTO 2026-07-16 [VERIFICADO contra código, no contra el log]:**
      `tokens.css` sí tiene la paleta light correcta y el mesh DeFi sí está apagado por CSS
      (`.cx-mesh > div { display:none }`). PERO `Dashboard.tsx` e `Inteligencia.tsx` (y probablemente
      Arbitrage/Analitica de la misma ola) **nunca migraron** — cada uno reimplementa su propio
      `tok(dark)` + `GCard` inline con hex hardcodeado (`#5b8df8`, `#60a5fa`, `#0ea5e9`...) que no son
      los tokens del landing, ignorando el `components/Card.tsx` compartido que sí usa `var(--bg-elevated)`/
      `var(--shadow-card)`. Efecto: glass pesado (blur 32px) en TODAS las tarjetas de una página que
      debía ser "flat-limpia, glass SOLO en nav" (norma del propio PLAN.md). Esto es la causa raíz de
      "el dashboard se ve de pena" (queja owner 2026-07-16), no un problema de gusto. Bug adicional
      encontrado en el propio `Card.tsx`: borde hardcodeado `border-white/[0.07]` — invisible en light
      mode (debería usar `var(--border-default)`). Ficheros tocados en B0/B1 original: index.html,
      main.tsx, styles/tokens.css, index.css, tailwind.config.js — esos sí están bien. Reabierto para
      migrar Dashboard/Inteligencia/Arbitrage/Analitica al sistema real (ver `05-MONETIZATION-MAP.md` +
      log de hoy abajo).
- [ ] **B2** Shell + navegación unificada (un solo sitio, dealer-first)
- [ ] **B3** Landing pública limpia + Login
- [ ] **B4** Dashboard único dealer-first (unifica los 4)
- [~] **B5** Secciones — **Inteligencia ✅ + Arbitrage ✅** (React en estilo landing, desde MATRIX/OFFERING/
      ARBITRAGE; reemplazan el terminal DeFi; nav grupo INTELIGENCIA, Terminal fuera; verificadas light+dark,
      0 errores, build ✓). Pendiente: pulir workspace (Vehicles/CRM/Finance/Inbox/Calendar/Settings cascaron
      en B1) + Check/Dossier. /api es forward-ref (B6).
- [x] **B6** API & Tokens — KPIs (saldo/consumo/plan/llamadas), catálogo endpoints INFO/INVENTORY con coste
      en tokens, consumo chart 30d, API keys CRUD (crear/rotar/revocar), planes Starter/Scale/Enterprise,
      quick-start curl. Verificada light, 0 errores, build ✓. PENDIENTE polish marca: violeta "Scale"/planes → azul.
- [ ] **B7** Auditoría final + parte

## Log
- 2026-06-30: Recon completo de `web/` (app React real con auth/router/components/hooks). PLAN.md escrito.
  Decisión: build en `web/`, re-skin al landing por tokens (cascada). Arranco B0 (baseline build).
- 2026-06-30: B0+B1 cerrados (commit pusheado). Barrido visual: las páginas workspace (Dashboard, Vehicles,
  CRM, Finance, Inbox, Calendar, Settings) cascan bien al landing. **PERO `Market`/`Terminal` son un terminal
  de trading DeFi (velas, watchlist, "estimated balance", portfolios) — oscuro, metáfora bursátil que NO
  encaja con el dealer ni con la auditoría, y choca con el landing.** Decisión (autoridad): en B5 se
  REEMPLAZAN por **Inteligencia** (price-position/residual/days-to-sell/distribución/delta) y **Arbitrage**
  (deal-score/sourcing/cross-platform/spread/time) en estilo landing, desde MATRIX/PLACEMENT/OFFERING/ARBITRAGE.
  Memoria respaldando: "do NOT ship DeFi figures". Nav: añadir Inteligencia + Arbitrage + API/Tokens.
- 2026-06-30 (OLA 2, integrada+verificada+build verde): **Landing** limpia (sustituye DeFi) · **Auth** suite
  (Login re-skin 2-col + Registro + Reset + 2FA) · **Dashboard ÚNICO** dealer-first (KPIs→Oportunidades deal-score
  →Posición mercado→Margin/Pipeline/AI→Revenue/Top-modelos→Stale/Activity) · **Analítica** (KPIs+tendencia+embudo+
  canales+rotación+región). Nav grupo INTELIGENCIA (Inteligencia/Arbitrage/Analítica). Verificadas light Playwright.
  PENDIENTE ola 3: CRM (Contactos/Deals/Tareas-Kanban-Notas) · Comunicación (Inbox/Chat) · Finanzas (Facturas/
  Transacciones/Planes) · Cuenta (Perfil/Ajustes/Soporte) · Inventario rico · Calendario · Asistente IA · errores ·
  componentes design-system. + pasada coherencia marca (violeta→azul donde quedó). + verificación dark global.
- 2026-06-30 (OLA 3, integrada+verificada+build verde): **Finanzas** (Finance rewrite + Facturas + Planes) ·
  **CRM** (Contactos/Deals/Kanban reskin + Notas nueva) · **Cuenta** (Settings 5-tabs + Perfil + Soporte). NAV
  reestructurado a 7 grupos dealer-first en ES: PRINCIPAL(Dashboard/Inventario) · INTELIGENCIA · CRM&VENTAS ·
  OPERACIÓN(Inbox/Calendario) · FINANZAS(Finanzas/Facturas/Planes) · HERRAMIENTAS(API/VIN) · CUENTA(Perfil/
  Soporte/Ajustes). Rutas /invoices /pricing /notes /profile /support. Verificado Invoices + nav (1 sitio, sin ruido).
  PENDIENTE ola 4: Comunicación(Chat) · Inventario rico (foto/detalle) · Calendario · Asistente IA · errores ·
  componentes design-system · coherencia marca (algún violeta→azul, títulos EN→ES) · verificación DARK global · B7.
- 2026-06-30 (OLA 4 + coherencia marca, integrada+verificada+build verde): **Chat** (3-col mensajería) +
  **Asistente IA** (4 modos: Preguntar/Descripción anuncio/Valorar VIN/Imagen — unifica los generadores).
  Nav: Chat→OPERACIÓN, Asistente IA→HERRAMIENTAS. **Pasada de marca:** púrpura hardcodeado→azul en Api/Dashboard/
  Analitica/Landing/Inteligencia/Arbitrage (cero violeta en páginas en-uso; Market/terminal DeFi quedan fuera de nav).
  Verificado Assistant + nav completo. PENDIENTE cierre: páginas de error · B7 auditoría (barrido TODAS las rutas +
  dark + responsive 390/768 + CI) · opcional (componentes-showcase, inventario-detalle, títulos EN→ES) · parte.
- Orden afinado: B3 landing limpia + login → B4 dashboard (añadir señales inteligencia/arbitrage dealer-first)
  → B5 Inteligencia + Arbitrage (reemplazo DeFi) + pulir workspace → B6 API/Tokens → B2 nav final → B7 auditoría.
- 2026-06-30: Owner aclara — ABSORBER TailAdmin(87)+Spike(88) en el frontend (no solo re-skin). Escrito
  `UNIFICATION.md` (175 pantallas → secciones canónicas, que no falten). Entregado+verde: Inteligencia,
  Arbitrage, API&Tokens (134f30b). Theming workspace arreglado: Vehicles/Check/DossierReport dark→tokens
  (Vehicles verificado light; Inbox/Calendar ya OK). Orquestando por olas: en vuelo Landing limpia, suite Auth
  (Login/Registro/Reset/2FA), Dashboard único, Analítica.
- **2026-07-16 (owner: "el dashboard de puta pena visualmente" + reestructurar workspace + integrar
  auditoría de 109 empresas + definir qué info es de pago):** Recon verificado contra código (no contra
  este log): B1 reabierto (ver arriba). Escrito `05-MONETIZATION-MAP.md` (Capa 0/1/2 de
  `CARDEEP-OFFERING.md` → páginas/widgets concretos de `web/`, teaser vs contador+muestra vs bloqueado).
  **Bloque 1 CERRADO+VERIFICADO:** infra compartida nueva — `hooks/useIsDark.ts` (extraído, deduplicado),
  `lib/entitlements.ts` (Feature→Plan desde el mapa de monetización), `components/PremiumGate.tsx`
  (blur+CTA real, no maqueta), `types.ts` (`Plan`, `User.plan`), fix de bug real en `components/Card.tsx`
  (borde `border-white/[0.07]` hardcodeado → invisible en light mode → `var(--border-default)`).
  `Dashboard.tsx` reconstruido íntegro sobre `Card`+tokens CSS reales (cero `tok()`/`GCard` inline, cero
  hex arbitrario — 1 acento de marca + verde/rojo/ámbar semánticos únicamente); `PremiumGate` aplicado a
  Oportunidades (Capa 2/sourcing-ranking); eliminado `QuickActions` (código muerto preexistente, nunca
  montado en el grid). Verificado: `tsc --noEmit` limpio, `npm run build` verde (2926 módulos, 23.9s),
  Playwright light+dark en `:5173/dashboard` — 0 errores nuevos (los 2 presentes son preexistentes:
  `/api/v1/kpi` 500 por backend no levantado esta sesión, favicon 404 — ninguno introducido por este
  cambio), gating visual confirmado (blur+lock+CTA "Desbloquear con Enterprise" en Oportunidades).
  **Bloque 2 CERRADO+VERIFICADO:** `lib/theme.ts` extraído (ACCENT/GOOD/BAD/WARN, ya no duplicado por
  página). `Inteligencia.tsx` reconstruido igual que Dashboard (cero `tok()`/`GCard`) + gating real por
  el mapa: Valor residual (España libre, comparativa vs UE tras `cross-border-compare`), Días en stock
  (stat propio libre, comparativa completa tras `market-position-detail`), Delta en vivo (3 eventos
  libres, resto tras `delta-feed-full`), Demanda por región sin gate (agregado nacional YA es el teaser
  libre, por diseño del mapa). Bug real encontrado y arreglado en el propio `PremiumGate.tsx`: el wrapper
  sin `h-full` colapsaba a 0px los charts de recharts gateados (Días en stock se veía vacío tras el
  candado) — recharts `ResponsiveContainer` necesita altura explícita en toda la cadena de ancestros.
  Verificado: build 2927 módulos, Playwright `:5173/inteligencia` 0 errores consola (esta página no
  llama a `/kpi`), light+dark, blur+CTA visibles y legibles. Sin regresión en Dashboard tras el fix.
  **Bloque 3 CERRADO+VERIFICADO:** `Arbitrage.tsx` reconstruido igual (cero `tok()`/`GCard`). Decisión de
  diseño (no en el mapa original, añadida aquí): en vez de 4 candados repetidos sobre Chollos/Cross-
  platform/Spread/Time-arbitrage, UN solo `PremiumGate` envuelve el grid de 4 paneles — Capa 2 es un
  bundle Enterprise, no 4 features sueltas a micro-cobrar; el KPI band (chollos hoy/margen medio/mejor
  deal-score/gaps) queda libre como agregado, igual que el resto de teasers. Además: `SpreadPanel`
  reescrito para NO fingir un dato que no existe — antes mostraba spreads retail/wholesale como si
  fueran reales; ahora dice explícitamente "pendiente de partnership wholesale, no es un dato inventado"
  (fiel a `ARBITRAGE.md` §4 "Honestidad de alcance" — el spread necesita feed de un socio, cardeep solo
  tiene la pata retail). Verificado: build verde (2927 módulos), Playwright `:5173/arbitrage` 0 errores
  consola, gate visible y legible sobre los 4 paneles a la vez.
  **Bloque 4 CERRADO+VERIFICADO — barrido completo:** `Analitica.tsx` reconstruido igual (cero
  `tok()`/`GCard`, paleta `lib/theme.ts`). Sin gating — confirmado en el mapa: 100% dato propio del
  dealer (ventas/marketing/stock/canales), ninguna cifra viene del censo de mercado. Verificado: build
  verde, Playwright `:5173/analitica` 0 errores consola.
  **B1 sigue ABIERTO, corrigiendo mi propia afirmación previa:** verifiqué con
  `grep -rl "function GCard\|function tok(dark" src/pages/` ANTES de dar el barrido por cerrado y
  quedan 5 páginas más con la misma duplicación: `Api.tsx`, `Assistant.tsx`, `Finance.tsx`,
  `Invoices.tsx`, `Pricing.tsx`. Las 4 de este barrido (Dashboard/Inteligencia/Arbitrage/Analítica) —
  las que estaban en el nav activo de INTELIGENCIA/PRINCIPAL y las que motivaron la queja del owner —
  sí están limpias y verificadas. Las 5 restantes quedan para la próxima iteración del loop.
  Siguiente: (a) las 5 páginas restantes con `tok()`/`GCard`, (b) B2 (Shell+nav unificada), (c) B3
  (Landing pública+Auth), (d) B7 (auditoría final, barrido todas las rutas + responsive + CI).
