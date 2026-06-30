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
- [ ] **B5** Secciones end-to-end (inventario, CRM, finanzas, inteligencia, arbitrage, check, settings)
- [ ] **B6** API & Tokens (venta info + inventario por tokens)
- [ ] **B7** Auditoría final + parte

## Log
- 2026-06-30: Recon completo de `web/` (app React real con auth/router/components/hooks). PLAN.md escrito.
  Decisión: build en `web/`, re-skin al landing por tokens (cascada). Arranco B0 (baseline build).
