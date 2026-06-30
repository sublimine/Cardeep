# Mapa maestro de unificación — "que no falten"

> Contrato del owner: el frontend definitivo (`web/`) debe ABSORBER todo el contenido de TailAdmin (87) +
> Spike (88) + lo que ya hay en `web/`, UNIFICADO por sección (no 175 páginas: una sección rica por tema),
> estilo landing, login-gated, dealer-first, sin ruido. Entrada pública = landing. Cada pantalla origen
> queda mapeada a una sección canónica abajo. Marca [x] cuando la sección unificada está construida+verificada.

## IA canónica (nav final, agrupado, dealer-first, lo escondido tras un clic)

### PRINCIPAL
- [ ] **Dashboard** (único, dealer-first) ← web `Dashboard` + TailAdmin `index`(ecommerce)`,analytics,crm,marketing,saas,sales,stocks,logistics,finance` + Spike `index,index2`. Unifica los mejores widgets: KPIs stock/margen/días, ventas, pipeline, oportunidades/arbitrage, actividad, mapa demanda, metas.
- [ ] **Inventario** ← web `Vehicles` + TailAdmin `products-list,add-product,stocks` + Spike `eco-product-list,eco-shop,eco-shop2,eco-shop-detail,eco-shop-detail2,eco-checkout`. Lista+detalle de vehículo, alta, estados, márgenes.
- [x] **Inteligencia** ← (hecho) MATRIX/PLACEMENT/OFFERING + TailAdmin `analytics` widgets de mercado.
- [x] **Arbitrage** ← (hecho) ARBITRAGE.md.

### CRM & VENTAS
- [ ] **Contactos** ← web `Contacts` + Spike `app-contact,app-contact2` + TailAdmin `crm`.
- [ ] **Pipeline / Deals** ← web `Deals` + TailAdmin `crm`.
- [ ] **Tareas / Kanban / Notas** ← web `Kanban` + TailAdmin `task-kanban,task-list` + Spike `app-kanban,app-notes`.

### COMUNICACIÓN
- [ ] **Inbox / Email** ← web `Inbox` + TailAdmin `inbox,inbox-details` + Spike `app-email`.
- [ ] **Chat** ← TailAdmin `chat` + Spike `app-chat,ui-chat-bubbles`.
- [ ] **Notificaciones** ← TailAdmin `notifications` + Spike `ui-notification` (panel + NotificationBell ya existe).

### FINANZAS
- [ ] **Finanzas** ← web `Finance` + TailAdmin `finance`.
- [ ] **Facturas** ← TailAdmin `invoices,create-invoice,single-invoice` + Spike `app-invoice,eco-checkout`.
- [ ] **Transacciones** ← TailAdmin `transactions,single-transaction,billing`.
- [ ] **Planes / Pricing** ← TailAdmin `pricing-tables` + Spike `page-pricing` (+ recarga de tokens, ver API).

### ANALÍTICA & DATOS
- [ ] **Analítica** ← TailAdmin `analytics,marketing,saas,sales,stocks,logistics` (como vistas de informe) + Spike `widgets-charts,widgets-data,widgets-feeds,widgets-cards,widgets-banners,widgets-apps`.
- [ ] **Charts/Maps** (lib interna) ← TailAdmin `bar-chart,line-chart,pie-chart,radar-chart,radial-chart,maps,vector-maps` + Spike `chart-apex-*`. Se realizan como componentes reutilizables (recharts) usados en dashboard/analítica, no como páginas-demo sueltas.

### HERRAMIENTAS
- [~] **API & Tokens** ← (en construcción) + TailAdmin `api-keys,integrations`.
- [ ] **VIN Check / Dossier** ← web `Check,check/*` (cardeep-propio).
- [ ] **Calendario** ← web `Calendar` + TailAdmin `calendar` + Spike `app-calendar`.
- [ ] **Asistente IA** ← TailAdmin `ai,ai-settings` + generadores `code-generator,image-generator,text-generator,video-generator` (se consolidan en UN asistente cardeep con modos; no 4 páginas).

### CUENTA & SOPORTE
- [ ] **Perfil** ← TailAdmin `profile` + Spike `page-user-profile,page-user-profile2`.
- [ ] **Ajustes** ← web `Settings` + Spike `page-account-settings`.
- [ ] **Soporte / FAQ** ← TailAdmin `support-tickets,support-ticket-reply,faq` + Spike `page-faq`.
- [ ] **Blog / Recursos** ← Spike `blog-posts,blog-detail` (opcional, si aporta; si no, fuera — sin ruido).

### AUTH (público, fuera del nav)
- [ ] **Login** ← web `LoginPage` + TailAdmin `signin` + Spike `authentication-login,login2`.
- [ ] **Registro** ← TailAdmin `signup` + Spike `authentication-register,register2`.
- [ ] **Reset / Forgot** ← TailAdmin `reset-password` + Spike `authentication-forgot-password,forgot-password2`.
- [ ] **2FA** ← TailAdmin `two-step-verification` + Spike `authentication-two-steps,two-steps2`.

### SISTEMA / PÁGINAS
- [ ] **Landing pública** ← `portal/index.html` (referencia de estilo) → `web/pages/Landing` (sustituye la DeFi).
- [ ] **Errores** ← TailAdmin `404,500,503,coming-soon,maintenance,success` + Spike `authentication-error,authentication-maintenance`.

### DESIGN SYSTEM (galerías → componentes, no páginas-demo)
Las galerías de UI de TailAdmin (`alerts,avatars,badge,breadcrumb,buttons,buttons-group,cards,carousel,dropdowns,
images,links,list,modals,pagination,popovers,progress-bar,ribbons,spinners,tabs,tooltips,videos,form-elements,
form-layout,basic-tables,data-tables`) y Spike (`ui-*` ×31, `form-*` ×6, `table-*` ×5, `icon-*`) se ABSORBEN como
**componentes del design-system** de `web/src/components` (ya existen Button/Card/Table/Tabs/Modal/Badge/Toast/…;
ampliar los que falten: Accordion, Carousel, Stepper, Datepicker, Ratings, Progress, Pagination, Breadcrumb,
Timeline, Skeleton). Opcional: una página `/componentes` que los muestre. NO se crean 70 páginas-demo.

## Cobertura (que no falten) — 87 TailAdmin + 88 Spike = 175 → todas mapeadas arriba.
Regla: ninguna pantalla origen sin sección destino. Las puramente demostrativas (galerías UI, layouts, charts
sueltos) → design-system/componentes. Las funcionales → su sección canónica unificada.

## Ejecución (bloques revisados, delegados en paralelo + verificados)
1. Landing pública limpia + Auth (login/registro/reset/2FA) — entrada.
2. Dashboard único (unifica los 9+ dashboards) dealer-first.
3. Inventario, CRM (Contactos/Deals/Tareas), Comunicación (Inbox/Chat).
4. Finanzas (Finanzas/Facturas/Transacciones/Planes), Analítica.
5. Herramientas (API[hecho], Calendario, Asistente IA, VIN Check), Cuenta (Perfil/Ajustes/Soporte).
6. Design-system: ampliar componentes que falten + (opcional) /componentes. Errores.
7. Nav final agrupado + auditoría (build, light/dark, responsive, 0 errores, CI) + parte.
