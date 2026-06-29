# Admin cardeep — volcado ÍNTEGRO de TailAdmin PRO + Spike PRO (2026-06-29)

El owner pidió **copiar y volcar por completo, de manera integral: TODAS las páginas, funciones y
diseños** de los dos enlaces. Los repos FREE de GitHub eran recortados → se **espejaron los demos PRO
completos** (HTML estático servido público) con `_build/mirror.py` (BFS: HTML+CSS+JS+imgs+fuentes,
estructura relativa intacta) y se rebrandearon a cardeep.

## Inventario en `portal/app/`
- **TailAdmin PRO** → `app/*.html` — **87 páginas**: dashboards (eCommerce, Analytics, Marketing, CRM,
  Stocks/Sales/Finance, SaaS, Logistics), AI (chatbot, code/image generator, settings), E-commerce
  (products, add, billing, invoices, create-invoice, transactions), apps (Chat, Inbox/Email, Calendar,
  File-manager, Task list/kanban), Forms, Tablas (basic/data), 6 Charts (line/bar/pie/radar/radial), UI
  Elements (~25: alerts/avatars/badge/buttons/cards/carousel/dropdowns/modals/…), 6 Layouts, Auth (signin/
  signup/reset/2FA), Pages (pricing/faq/blank/404/500/503/coming-soon/maintenance), Maps, Profile.
  Build: `bundle.js` (Alpine + ApexCharts + jsvectormap + flatpickr + fullcalendar) + `style.css`.
- **Spike PRO** → `app/spike/main/*.html` — **88 páginas**: 2 dashboards, apps (Chat, Email, Kanban,
  Notes, Calendar, Contacts, Invoice), eco-shop (×6), Blog, 6 charts Apex, Forms (×6), Tablas (×6), ~30
  componentes UI, Auth (×10), páginas (pricing/faq/account/profile). Libs: Preline+jQuery+ApexCharts+
  fullcalendar+jvectormap+simplebar+owl.
- **TOTAL: 176 páginas admin.** Tamaño `app/` ≈ 58 MB.

## cardeep-ificación (global)
- Logos cardeep (concéntrico + wordmark) sobrescritos en `app/src/images/logo/*` y `app/spike/assets/images/logos/*`.
- Texto: "TailAdmin"/"Spike"/"WrapPixel" → cardeep; usuario → "Talleres Méndez"; promos ("Purchase Plan",
  "#1 Tailwind", barra WrapPixel, Download Free, Upgrade to Pro, badges Pro) eliminadas; emails/dominios
  (pimjo/tailadmin.com) → cardeep.es; **scripts Cloudflare (cdn-cgi) eliminados** (0 errores de consola).
- KPIs/tabla del dashboard eCommerce relabelados a contexto cardeep en la fase previa (Leads/Operaciones/
  coches). El resto de páginas conservan datos demo del template (el owner: "no te preocupes con los datos").

## Conexión / integración
- Landing público (`index.html`) "Ver demo" → `app/index.html`.
- Panel TailAdmin: promo-box → **"Ver el sitio"** (landing) + **"Cockpit Spike"** (Spike) [71 páginas].
- Spike: marca → `../../index.html` (panel TailAdmin) [79 páginas].
- Cross-links nativos completos dentro de cada suite (sidebars).

## Verificado (Playwright, 0 errores consola)
- Render: TA eCommerce, TA Analytics, Spike index2, Spike Chat — idénticos al demo, branded cardeep.
- Matriz: 29/29 páginas muestra → 200; 87 TA + 88 Spike sirviendo.

## Residual honesto (NO bloqueante)
1. Datos internos = demo del template (cardeep los llenará; instrucción del owner).
2. Variantes de LAYOUT de Spike (dark / RTL / horizontal / mini-sidebar) NO incluidas — se conservó la
   default `main/` para evitar ×5 redundancia (las mismas 88 páginas re-skineadas). Restaurables si se piden.
3. **Licencia:** TailAdmin PRO y Spike PRO son plantillas de pago (demo público espejado). OK para
   desarrollo local; **regularizar licencia antes de despliegue público** o sustituir marca/recursos.
- El portal de diseño original (10 `.html` en `portal/`) queda intacto.

## Reproducir / re-espejar
`python _build/mirror.py "<PREFIX_URL>" <LOCAL_DIR> <START_URL...>` (mirror genérico BFS).
