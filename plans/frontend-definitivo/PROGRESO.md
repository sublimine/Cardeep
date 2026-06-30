# Frontend definitivo — PROGRESO
> Estado por bloque. Se actualiza al cerrar cada uno. Verdad cruda: solo [x] con verificación real.

- [x] **B0** Baseline — typecheck limpio + build ✓ 14.58s (2900 módulos). node_modules presente.
- [x] **B1** Design-system → landing — General Sans + JetBrains Mono, paleta light neutra del landing
      (#EAECEF/#FFF/#13161B/#3B82F6) con overrides `-ch` para Tailwind, light-first (main.tsx), mesh DeFi
      aplanado (cx-mesh flat + orbes ocultos). Verificado Playwright (dashboard en estilo landing) + build ✓.
      Ficheros: index.html, main.tsx, styles/tokens.css, index.css, tailwind.config.js.
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
- Orden afinado: B3 landing limpia + login → B4 dashboard (añadir señales inteligencia/arbitrage dealer-first)
  → B5 Inteligencia + Arbitrage (reemplazo DeFi) + pulir workspace → B6 API/Tokens → B2 nav final → B7 auditoría.
- 2026-06-30: Owner aclara — ABSORBER TailAdmin(87)+Spike(88) en el frontend (no solo re-skin). Escrito
  `UNIFICATION.md` (175 pantallas → secciones canónicas, que no falten). Entregado+verde: Inteligencia,
  Arbitrage, API&Tokens (134f30b). Theming workspace arreglado: Vehicles/Check/DossierReport dark→tokens
  (Vehicles verificado light; Inbox/Calendar ya OK). Orquestando por olas: en vuelo Landing limpia, suite Auth
  (Login/Registro/Reset/2FA), Dashboard único, Analítica.
