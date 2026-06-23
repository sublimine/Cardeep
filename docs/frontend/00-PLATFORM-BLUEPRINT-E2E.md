# CARDEEP — Blueprint Maestro de Plataforma (End-to-End)

> **Arquitecto jefe · 2026-06-23.** Síntesis autoritativa de las 16 specs de superficie + coherencia
> con `01-DESIGN.md` (tokens), `02-REFERENCES.md` (tablero del owner), `03-MOTIONSITES-AUDIT.md`
> (calibre de motion), `04-COMPETITIVE-UX-AUDIT.md` (patrones del sector ES).
> Este documento gobierna la coherencia de TODO el producto. Cada superficie individual tiene su
> spec atómico; aquí se sella el sistema que las une: visión, sitemap, auth, media global, design
> system y roadmap de construcción superficie-por-superficie.
>
> Doctrina: dato real es el media · cada botón con lógica · €0 donde se pueda · NO inventar dato
> que no existe · marca fiel (cobalt/charcoal/white, NADA de violeta/magenta como CTA).
>
> **Nota de marca cobalt vs cian:** el mandato de marca declara Cobalt Blue `#3B82F6` · Deep
> Charcoal `#111B27` · White. El design system implementado (`01-DESIGN.md` / `tokens.css`) usa
> base `#0A0E17` + acento cian `#35E0D0`. Varias specs de superficie heredaron el cian.
> **DECISIÓN DE ARQUITECTURA (sellada): la marca manda — `#3B82F6` cobalt es el acento de acción
> canónico.** El cian `#35E0D0` se RETIRA como acento primario; se permite solo como matiz de
> rampa de datos secundaria (señal viva en sparklines/ticker), nunca como CTA ni como color de
> identidad. Sección §5 fija la migración de tokens. Toda spec que diga "cian #35E0D0 CTA" se
> interpreta como "cobalt #3B82F6 CTA".

---

## 1 · VISIÓN + PRINCIPIOS DE PRODUCTO

### 1.1 Qué es CARDEEP end-to-end
CARDEEP es **el mapa vivo y verificado del mercado de coches** — hoy España, mañana Europa, después
el mundo. El backend ya existe y es real: **2,35M coches · 436k entidades · delta completo (altas,
bajas, Δprecio, Δfoto, Δkm, historial) · verificación VAM cero-confianza · cobertura por provincia
con sello estadístico · API que sirve solo lo verificado · 2,2M fotos reales en DB.**

El producto end-to-end es una plataforma de **siete capas** sobre ese censo:

1. **Descubrimiento** — landing cinematográfica + marketplace inteligente (mapa 3D + lista).
2. **Profundidad por activo** — ficha de vehículo con historial gratis (estilo Carfax) + ficha de dealer.
3. **Inteligencia** — arbitraje quirúrgico (Indicata, más profundo) + terminal de análisis técnico (TradingView del coche).
4. **Comunidad** — foro/red social anclado a datos verificados + asistente IA "Deepy".
5. **Operación B2B** — dashboard institucional, garaje 3D, cross-posting + inbox unificado, finanzas + CRM + flota.
6. **Distribución** — API marketplace + pricing, cobertura territorial/expansión.
7. **Atención** — noticias/novedades + centro de notificaciones.

### 1.2 El norte: Europa → mundo
La cobertura territorial NO es una página: es el **foso defensivo visible**. CARDEEP es el único
actor con el censo completo de ES y un denominador medido y confesado (no reclamado). La expansión
a Europa se ancla públicamente en `/cobertura` (wishlist-first, lead magnet API) para generar
demanda anticipada antes de tener el dato. El producto se diseña multi-mercado desde el día 1:
todo lo geo es parametrizable por país, no hardcoded a España.

### 1.3 Principios rectores (los 8 mandamientos)
1. **El dato real ES el media.** Las 2,2M fotos reales y el mapa 3D vivo son el activo. No se tapan con stock ni generadas innecesarias.
2. **Cada botón tiene lógica.** Cero decoración. Si un elemento no comunica o no actúa, desaparece.
3. **Honestidad institucional.** Se confiesan los gaps con su causa (35,2% C2C excluido, Canarias 59,4%, Tier-1 spend-gated). Ningún competidor publica su denominador; CARDEEP sí.
4. **Dark luxury / command-center.** Todos los competidores son blancos y se parecen. CARDEEP rompe por contraste total: base oscura cinematográfica, cobalt eléctrico, datos que brillan.
5. **3D-first donde demuestra; 2D donde trabaja.** El mapa 3D es identidad y navegación. Las superficies de productividad (inbox, cross-posting, terminal) NO llevan 3D pesado — el dato es el protagonista.
6. **€0 por defecto.** Shaders R3F reutilizados, SVG inline, CSS puro, cero librerías para lo que CSS resuelve. Gasto (media generada, LLM, HA) solo con luz verde del owner.
7. **Motion deliberado (doctrina GTA VI).** Si quitas la animación y el significado no cambia, no debe existir. Solo `transform`/`opacity`/`clip-path`/`filter`. `prefers-reduced-motion` siempre respetado.
8. **Fase explícita por cada cosa.** `now` (construible ya sobre dato real) · `near` (gap de 1 endpoint/tabla) · `future` (data/compute/spend-gated). Nunca se finge que un `future` es `now`.

---

## 2 · SITEMAP GLOBAL + NAVEGACIÓN + AUTH

### 2.1 Árbol de rutas completo

```
PÚBLICO (sin auth) — Capa 0
├── /                          Landing cinematográfica            [NOW]
├── /explore                   Marketplace (mapa 3D + lista)      [NOW]
│   ├── ?mode=coches|dealers   toggle de modo
│   └── ?prov=NN&make=&...      estado de filtros en URL (shareable)
├── /vehicle/:ulid             Ficha vehículo + Historial gratis  [NOW]
├── /dealer/:cdp               Ficha dealer                       [NOW]
│   └── /dealer/:cdp/garage     Garaje 3D (showroom moldeable)    [NOW]
├── /intel                     Inteligencia & Arbitraje           [NOW parcial / NEAR]
├── /terminal                  Terminal de análisis técnico       [NOW]
│   └── /terminal/screener      Screener cuantitativo             [NEAR]
├── /community                 Foro / Red social                  [NOW UI / FUTURE social layer]
│   ├── /community/thread/:id
│   ├── /community/user/:handle
│   └── /community/inbox
├── /cobertura                 Cobertura territorial / Expansión  [NOW]
├── /noticias                  Noticias y novedades               [NOW 70% / NEAR]
│   └── /noticias/:slug         Artículo (SSG, SEO)
├── /pro/api                   API Marketplace + Pricing          [NOW]
│   └── /pro/api/docs           Docs OpenAPI (público)
├── /notificaciones            Centro de notificaciones           [NOW core / NEAR persist]
│   └── /notificaciones/preferencias
├── /404                       Not found                          [NOW — existe]
└── SEO long-tail (near, SSG):
    ├── /coches/:prov/:marca/:modelo
    ├── /concesionarios/:prov
    └── /desguaces/:prov

AUTENTICADO — Capa 1 (usuario básico) [FUTURE]
├── /login · /signup           Auth (magic-link + OAuth Google)
├── /perfil                    Mi cuenta
├── /alertas                   Búsquedas guardadas + alertas
└── /garaje                    Mi garaje (favoritos en showroom 3D)

DASHBOARD DEALER — Capa 2 (rol dealer) [FUTURE]
├── /pro/dashboard             Overview / command-center (KPIs P&L)
├── /pro/flota                 Gestión de stock + kanban
├── /pro/crm                   Pipeline de leads con contexto CARDEEP
├── /pro/finanzas              P&L, margen, benchmark provincial
├── /pro/mercado               Inteligencia provincial / radar competidores
├── /pro/publish               Cross-posting multi-plataforma
├── /pro/inbox                 Inbox unificado
├── /pro/analytics             Analytics de publicaciones
├── /pro/api/dashboard         Gestión de claves API + uso + facturación
└── /pro/config                Perfil de entidad + integraciones

ADMIN — Capa 3 (rol admin) [FUTURE]
└── /admin                     Panel de operaciones (equipo CARDEEP)
```

`robots.txt` / `sitemap.xml` (now): indexar solo público de descubrimiento e inteligencia
(`/`, `/explore`, `/vehicle`, `/dealer`, `/cobertura`, `/noticias`, `/pro/api`, SEO long-tail).
Bloquear `/pro/dashboard`, `/pro/flota..config`, `/admin`, `/notificaciones`, `/community/inbox`.

### 2.2 Navegación global (3 layouts)

- **PublicLayout** (= `Layout.tsx` actual, ampliar): topbar sticky + `<Outlet>` + footer.
  - Topbar `scroll=0`: transparente (el mapa 3D pasa por detrás). `scrolled>64px`: glass
    (`--glass-bg` + blur + `border-bottom 1px --glass-border`), transición 260ms.
  - Links now: Mapa (`/`) · Explorar (`/explore`). Near: Inteligencia (`/intel`, badge Beta) ·
    Cobertura (`/cobertura`) · Noticias (`/noticias`). CTA derecha: "Acceso API" (now → GitHub) →
    se sustituye por "Login" al construir auth → avatar+dropdown cuando autenticado.
  - Campana de notificaciones (badge contador SSE) entra al construir `/notificaciones`.
  - Deepy FAB (botón flotante IA) montado UNA vez en el layout, persistente entre rutas.
  - Móvil ≤768px: hamburger → Drawer glass desde la derecha (`--z-drawer:150`, focus-trap, Esc cierra).
- **DashboardLayout** [future]: sidebar izquierda colapsable (72px↔240px) + topbar reducido con
  identidad de entidad (`cdp_code` mono + kind badge + veredicto VAM). Sin footer público.
- **AuthLayout** [future]: panel glass centrado sobre `SpainMap` en modo atmos (autorotate lento,
  `opacity 0.28`, no interactivo). Sin nav ni footer.

### 2.3 Modelo de auth/roles (por capas)
- **Capa 0 — público sin auth:** toda la lectura del censo. Es el MVP actual; el backend sirve
  lectura sin auth cuando `CARDEEP_API_KEY` no está seteado. (verificado en `api/client.ts`).
- **Capa 1 — usuario básico [near→future]:** Supabase Auth (magic-link + Google OAuth, coherente
  con el ecosistema del owner / Habana Legacy). JWT en **cookie httpOnly** (no localStorage → XSS).
  Desbloquea: alertas, garaje de favoritos, foro participativo, notificaciones persistidas.
- **Capa 2 — dealer profesional [future]:** rol `dealer` en JWT; ownership del `cdp_code`
  verificado por VAM (email a la entidad ya registrada). Desbloquea `/pro/*`.
- **Capa 3 — admin [future]:** rol `admin`, solo por invitación.
- **Guardas:** `ProtectedRoute` verifica JWT, redirige a `/login?next={ruta}`. BFF/proxy server-side
  inyecta la API key en prod (el bundle nunca lleva la key). CSRF token en mutations. Rate-limit ya en backend.

---

## 3 · LAS 16 SUPERFICIES (sección por superficie)

> Cada superficie tiene su spec atómico completo (botones+lógica, data-mapping, motion, build-notes).
> Aquí se sella: propósito en 1 línea, secciones núcleo, **decisión de media estrella**, comparable y fase.

### 3.1 Landing cinematográfica `/` — [NOW mayoritario]
**Propósito:** impacto de primer segundo + conversión a explore/dealer/API en <2 clics + credibilidad
técnica legible. **Secciones:** topbar glass · hero split 55/45 (copy + mapa 3D) · command strip de
cobertura (tabs Venta/Desguace) · 4 KPIs vivos (countUp) · 3 pilares editoriales · delta vivo (feed) ·
panel dealers (mockup con dato real) · sección API (code block) · grid 52 provincias · footer con estado API.
**Media estrella:** `SpainMap.tsx` (R3F) extruido por cobertura, Bloom selectivo en SELLADO, autorotate,
hover HUD, clic → `/explore?prov=NN`. **Botones clave:** Explorar (→/explore, CTA primario) · Acceso API
(→GitHub) · tabs Venta/Desguace (re-render barra segmentada). **Data:** `/stats`, `/geo/seal`,
`/entities/{cdp}` (mockup), delta snapshot (now) → `/delta` (near). **Comparable:** motionsites (calibre)
+ Indicata (dominio) + GTA VI (composición). **Fase:** hero+mapa+KPIs+cobertura+grid = now; DeltaFeed
endpoint + mockup dinámico + form dealer = near; price-rating + Deepy = future.

### 3.2 Marketplace inteligente `/explore` — [NOW base / NEAR filtros server]
**Propósito:** puerta de entrada usable al inventario; el mapa ES la navegación, la lista ES el producto.
Unifica los dos pasos actuales (ProvinceGrid→DealerBrowser) en un flujo continuo con estado en URL.
**Secciones:** topbar contextual (toggle Coches/Dealers + search + hit-count) · panel izq mapa 3D
selector geo (380px) · panel der lista infinita · sidebar filtros (facetas de la auditoría: marca→modelo,
precio €/mes, año, km, combustible, cambio, tipo-vendedor, DGT, sello) · VehicleCard / DealerCard ·
TrustBar · estados skeleton/empty/error. **Media estrella:** mapa 3D como **selector geográfico
interactivo** con drill-down a municipios (MuniPin, near) — ningún competidor tiene un mapa 3D funcional
como navegador. **Botones clave:** toggle Coches/Dealers (cambia schema+endpoint) · click provincia
(zoom cámara 800ms + `?prov=`) · "Ver N coches" (serializa filtros en URL) · card → ficha con `?back=`.
**Data:** `/geo/{prov}/entities`, `/entities/{cdp}/inventory`, `/geo/seal` (now); `/inventory/search`,
`/inventory/makes`, `/geo/{prov}/stats` (near). **Comparable:** AutoScout24 + AutoTrader UK + Carvago;
superamos en dark + 3D + granularidad de entidad + delta. **Fase:** layout split + URL-state + reuso
de componentes = now; búsqueda global server-side + pines municipio + facetas = near; price-rating + DGT = future.

### 3.3 Ficha de vehículo + Historial gratis `/vehicle/:ulid` — [NOW]
**Propósito:** la ficha más rica y honesta del mercado ES; historial completo GRATIS (NEW→PRICE_CHANGE→
PHOTO_CHANGE→KM_CHANGE→GONE) como diferencial vs Carfax/Carvertical de pago. Sin registro, sin paywall.
**Secciones:** hero galería a sangre (glass overlay: título + precio oversized + badges) · rail sticky
de acción (precio + Δ + CTA deep_link + dealer chip) · specs command-center · **timeline de historial** ·
plataformas (comparador cross-listing) · dealer mini-card (mapa mini R3F) · alias banner · estados.
**Media estrella:** la **timeline de historial de vida** como dataviz (dots semánticos + old→new + Δ),
gratis — el moat de confianza. **Botones clave:** Ver anuncio original (deep_link, _blank) · Ver ficha
canónica (si is_canonical=false) · Ver todo el historial (paginación) · miniaturas galería (crossfade).
**Data:** `/vehicles/{ulid}`, `/vehicles/{ulid}/history`, `/vehicles/{ulid}/platforms` (todo VERIFIED now);
price-rating heurístico now → endpoint valoración near; galería multi-foto near (DB tiene 2,2M, API expone 1).
**Comparable:** Carfax/Carvertical (lo damos gratis) + AutoScout (price-rating + rail sticky) + TradingView
(chart de precio, near). **Fase:** todo el núcleo = now; chart recharts + galería + DealerMiniCard inventory = near; ML valoración + ITV = future.

### 3.4 Inteligencia & Arbitraje `/intel` — [NOW 60% / NEAR 30% / FUTURE 10%]
**Propósito:** convertir 2,3M coches + 2,6M eventos en señales accionables: valoración, arbitraje
(precio anómalo vs P50), profundidad por segmento, velocidad de rotación, anomalías. Dual: dealer
institucional + comprador-inversor. **Secciones:** hero command-center (particle field del delta) ·
Market Pulse (histograma P25/P50/P75 + velocidad + profundidad) · **señales de arbitraje (heat-map
bento)** · historial de precio individual · profundidad geo (árbol) · delta nacional (feed) · acceso
institucional. **Media estrella:** el **heat-map de oportunidades de arbitraje** (bento de cards con foto
real + descuento vs P50 + mapa de calor de señales por provincia) — Indicata pero más profundo y con
deep-link directo al anuncio. **Botones clave:** ver señales (scroll+prefiltro) · filtrar (URL params,
cálculo en front sobre cache) · señal → ficha con chart · export CSV. **Data:** `/stats`, `/geo/seal`,
`/entities/{cdp}/inventory` + `/delta` (now, P50 sobre subset); `/market/stats`, `/market/velocity`,
score normalizado (near); GANVAM/Eurotax, ML (future). **Comparable:** Indicata + TradingView + Carfax;
superamos en censo completo + historial individual + deep-link. **Fase:** ver distribución arriba.

### 3.5 Terminal de análisis técnico `/terminal` — [NOW core / NEAR screener]
**Propósito:** TradingView del coche — charts precio/volumen/evento por make·model·provincia, screener,
watchlist, sobre el delta real. El producto diferenciador absoluto. **Secciones:** TopBar command rail
(SymbolSearch + período + alertas) · workspace split 3 columnas redimensionables · WatchlistPanel
(localStorage, €0) · **ChartPanel (OHLC + overlays + marcadores de evento)** · EventFeed (polling 60s) ·
InspectorPanel (dealer/vehículo) · ScreenerPanel · HeatmapPanel (D3 treemap) · AlertsPanel (`/alerts`) ·
SourceHealthBar (`/sources`, admin). **Media estrella:** el **ChartPanel OHLC** construido agregando
PRICE_CHANGE del delta en buckets temporales — el dato ES el medio, estilo Bloomberg. **Botones clave:**
SymbolSearch (debounce 300ms) · período 7d/30d/90d/1y (recalcula since) · pausar feed · export PNG/CSV.
**Data:** todos los endpoints verificados now (`/stats`, `/geo/*`, `/entities/{cdp}/*`, `/vehicles/{ulid}/*`,
`/alerts`, `/sources`); facetas globales + auth watchlist = near; market intelligence + LLM = future.
**Comparable:** TradingView + Indicata + Bloomberg (densidad, no fealdad). **Fase:** ChartPanel+EventFeed+
Inspector+Heatmap+Watchlist+Alerts = now; screener completo + persistencia = near; Indicata-style = future.

### 3.6 Comunidad / Foro / Red social `/community` — [NOW UI+sidebar / FUTURE social layer]
**Propósito:** el foro de inteligencia donde el dato se vuelve conversación verificada — posts anclados
a vehículos/dealers/provincias reales, reputación por señal. **Secciones:** hero (pulso vivo) · mapa de
calor de conversación (SpainMap colorMode=activity) · feed de hilos (relevancia CARDEEP) · filtros+search ·
**panel lateral de datos vivos** (price movers + dealer activity + VAM recientes) · hilo individual con
anchor cards · perfiles · inbox · composición con DataLinker. **Media estrella:** las **anchor cards**
(VehicleAnchorCard/DealerAnchorCard) que incrustan dato verificado real con sparkline de precio dentro de
un post — cero-competencia. **Botones clave:** nuevo post (pre-rellena anchor desde contexto) · vincular
dato CARDEEP (busca inventario real) · votar (optimista) · filtrar por provincia (mapa). **Data:** sidebar
de mercado = now+near (endpoints triviales sobre dato en DB); capa social completa (users/threads/votes/
reputation) = future (servicio+tablas nuevos). **Comparable:** Hacker News + Reddit (densidad/votos) +
motionsites (ejecución) + Carfax (historial incrustado gratis). **Fase:** UI + componentes de dato
CARDEEP funcionan day-1 contra API real; capa social = future, no se bloquean mutuamente.

### 3.7 Deepy — Asistente IA `/` (widget transversal) — [NOW UI / NEAR backend LLM]
**Propósito:** widget conversacional embebido en TODAS las rutas que responde en lenguaje natural sobre
inventario/cobertura/entidades con contexto de la vista activa; primera interacción = onboarding.
**Secciones:** FAB persistente (partículas orbitando) · panel chat (drawer der / bottom-sheet móvil) ·
contexto de vista activa (inyectado al LLM) · historial (sessionStorage, 40 turnos) · mini-cards de
respuesta (entity/vehicle/coverage navegables) · suggestions contextuales · onboarding (avatar shader) ·
error states honestos. **Media estrella:** las **mini-cards navegables** dentro del bubble (no texto plano,
no links externos — objetos del producto con dato real). **Botones clave:** FAB toggle · enviar (tool-calling
contra API, ReAct ≤3 llamadas) · chips · ver todos en mapa. **Data:** TODOS los endpoints de lectura
existentes vía tool definitions (now); único gap = BFF `/deepy/chat` (litellm + GPT-4o-mini o Ollama €0,
near). **Comparable:** Perplexity (citas/fuentes) + Intercom (FAB persistente); superamos en contexto de
vista + honestidad cero-alucinación garantizada por tool-calling. **Fase:** UI now; endpoint LLM near; alertas/ML future.

### 3.8 Dashboard institucional `/pro/dashboard` — [NOW 85% / NEAR auth+P&L]
**Propósito:** command-center post-login dark-luxury: KPIs vivos, inventario con delta, actividad
timeline, mapa de cobertura propio, inteligencia de mercado. Convierte al dealer en operador soberano.
**Secciones:** top nav + identity rail · **hero KPI bar** (inventario/altas/bajas/Δprecio/rank) · inventario
paginado con delta · timeline actividad (polling 60s) · panel inteligencia (histograma + mini-mapa +
competidores) · mapa ubicación (Mapbox static) · vista cliente (saved+alertas) · configuración entidad.
**Media estrella:** el **KPI bar vivo** + mini-mapa 3D de cobertura propia vs competidores en provincia —
fusiona Indicata con estética command-center que ningún competidor ES tiene. **Botones clave:** repricing
sugerido (VAM lote) · marcar vendido (P&L) · ver historial precio · comparar en provincia · export CSV.
**Data:** 8 endpoints verificados cubren 85% now; price-histogram + P&L (coste) + saved = near; price-rating
+ serie temporal = future. **Comparable:** tablero Pinterest (#68/#38/#80) + Indicata/AutoScout HändlerIQ
(superamos: censo total, no solo anuncios pagados). **Fase:** tabla+timeline+mini-mapa+competidores+CSV = now; auth+coste/P&L+CRM = near.

### 3.9 Garaje 3D `/dealer/:cdp/garage` — [NOW]
**Propósito:** showroom tridimensional del dealer: sus coches reales en escena de estudio oscura,
orbitables, comparables, configurables desde el inventario vivo. La demostración más rotunda de la
profundidad de dato. **Secciones:** EntryGate (clip-path portal) · **SceneStage R3F** (suelo reflector +
luz 3 puntos + podium emissive + Bloom/CA/Vignette) · CarProxy (photo-card now / GLB near) · InventoryRail ·
SpecsHUD · CompareMode (2 coches) · FilterBar (client-side) · DeltaLiveFeed · Exit/Share. **Media estrella:**
la **escena de estudio R3F con suelo reflectante** donde la foto real del inventario se trata como objeto
premium (MeshReflectorMaterial + Bloom). **Botones clave:** ver anuncio original · comparar · compartir
garaje (`?v=:ulid`) · filtros/orden client-side. **Data:** `/entities/{cdp}`, `/inventory`, `/delta`,
`/vehicles/{ulid}/history` (todo now); price-rating + platforms en HUD = near; GLB 3D real (generate_3d) +
configurador + WebXR = future. **Comparable:** tablero #57/#90 + configurador Volvo EX30 (#7); superamos:
multi-coche, multi-dealer, dato real, CompareMode. **Fase:** todo el showroom photo-card = now; GLB/AR = future.

### 3.10 Cross-posting + Inbox unificado `/pro/publish` `/pro/inbox` — [NOW estado / NEAR motor]
**Propósito:** publicar el inventario en N plataformas a la vez y leer/responder todos los chats desde una
superficie. Elimina el trabajo duplicado del dealer. **Secciones:** DealerShell + sidebar (Inventario/
Publicaciones/Inbox) · inventario con estado de publicación por plataforma · **PublishPanel** (slide-in,
selector plataformas + log SSE en vivo) · tracker de publicaciones (deep_links reales) · inbox split
lista+hilo · conexión de plataformas (OAuth/key) · analytics (cobertura semáforo). **Media estrella:** el
**PublishLog en tiempo real** (SSE, stagger de progreso por plataforma) + cobertura semáforo (inventory vs
platform_listing). **Sin 3D** — herramienta de productividad. **Botones clave:** publicar selección (POST
batch + suscribe SSE) · conectar plataforma · responder (enruta a plataforma) · despublicar/re-publicar.
**Data:** estado de publicación + deep_links + cobertura = now (`platform_listing` en DB); publish_job +
platform_credentials + inbox_thread/message = near (migraciones 0033-0035). **Comparable:** Hootsuite/Buffer
(inbox split, disparo multi) + Indicata (analytics); superamos: inventario ya indexado + deep_link real day-1.
**Fase:** inventario+tracker+semáforo+shell = now; publish+inbox+conexión = near; typing/impresiones/LLM-desc = future.

### 3.11 Finanzas + CRM + Gestión de flota `/pro/finanzas` `/pro/crm` `/pro/flota` — [NOW core / NEAR auth+P&L+CRM]
**Propósito:** terminal de inteligencia financiera y operativa: P&L vivo sobre inventario real, pipeline
CRM con contexto CARDEEP, gestión de flota con delta. Monetización natural del backend. **Secciones:**
shell + nav módulos · overview command-center (bento KPIs) · **gestión de flota** (tabla densa: precio
VAM, Δ vs mercado, días en stock, plataformas + kanban + row expandible con historial) · CRM kanban
(leads + sugerencias alternativas del stock propio) · finanzas (P&L + simulador latente + benchmark) ·
mercado (observatorio + radar competidores) · config. **Media estrella:** el **simulador de P&L latente**
(treemap: capital inmovilizado por stock >45d vs precio VAM real) — no existe en ningún competidor.
**Botones clave:** repricing lote · marcar vendido · sugerir alternativas al lead · calcular P&L latente ·
radar competidores · crear alerta de mercado. **Data:** flota+historial+VAM+radar+observatorio+CSV = now;
auth+coste/P&L+CRM+alertas+scoring = near; cross-posting+financiación+previsión = future. **Comparable:**
LaCentrale Pilot + AutoScout HändlerIQ + mobile.de Sale Probability; superamos: censo total + delta + P&L
latente sobre VAM real + dark cinematográfico. **Fase:** ver data.

### 3.12 API marketplace + Pricing `/pro/api` — [NOW]
**Propósito:** vender el inventario vivo como producto de datos SaaS — acceso por API key (por dealer, por
provincia, delta completo), planes escalonados, docs, dashboard de claves. Cierra el loop B2B. **Secciones:**
hero (DataFlowShader: grafo de España con partículas de eventos) · propuesta de valor (3 pilares con métrica
viva + snippet JSON) · **pricing (4 planes: Starter/Developer €49/Pro €199/Enterprise)** · matriz de
endpoints por plan · quick-start (cURL/Python/JS/Go, snippets reales) · dashboard de claves (autenticado,
near) · casos de uso · trust+transparencia · FAQ técnico · footer conversión. **Media estrella:** la **tabla
de pricing + matriz de endpoints** anclada 100% al `API_CONTRACT.md` real (rate limits, cache, envelope).
**Botones clave:** obtener clave gratuita (lista de espera now → Stripe near) · activar plan · solicitar demo
Enterprise · copiar snippet · revelar/rotar clave (dashboard). **Data:** `/stats`, `/geo/seal`, snippets
reales (now); webhooks + telemetría uso + auth portal + Stripe (near); `/geo/exhaustiveness` + rate per-tenant
+ SLA HA + VAM en shape (future). **Comparable:** RapidAPI/Stripe/Twilio docs (claridad) + Algolia/Mapbox
(pricing); superamos: dato es el 100% del mercado real, no índice curado. **Fase:** todo el marketing+docs = now; dashboard+billing+webhooks = near; exhaustiveness+HA = future.

### 3.13 Noticias y novedades `/noticias` — [NOW 70% / NEAR pipeline]
**Propósito:** terminal editorial del mercado ES — dato real convertido en señal periodística (mercado,
releases, insights, arbitraje), con SEO long-tail masivo y retención. **Secciones:** hero editorial (titular
generado del delta + shader niebla) · **ticker de mercado en vivo** · feature article (foto generada por
tema) · grid editorial bento · **panel observatorio** (mini-mapa price-delta + barras top provincias +
sparklines por segmento) · artículo `/noticias/:slug` (lectura + sidebar de datos + links semánticos) ·
filtros categoría · newsletter. **Media estrella:** el **panel observatorio** (mini-mapa 3D coloreado por
variación de precio semanal + dataviz) — datos propietarios que nadie más puede publicar. **Botones clave:**
leer análisis · ver observatorio (→/cobertura o /intel) · explorar estos coches (→/explore con filtros del
artículo, loop editorial↔marketplace) · suscribirse · cargar más (URL ?page). **Data:** ticker+hero+observatorio+
mini-mapa = now (delta+stats+seal); worker de generación de artículos + RSS = near; LLM profundo + imágenes
continuas = future. **Comparable:** LaCentrale Observatoire + Bloomberg/TradingView + CarGurus Market Report;
superamos: censo 100% + delta completo + generación automática. **Fase:** 70% now, pipeline de artículos near.

### 3.14 Centro de notificaciones `/notificaciones` — [NOW 80% / NEAR persist / FUTURE WhatsApp]
**Propósito:** terminal de inteligencia en tiempo real — cada alerta de precio/stock/delta/sistema llega
clasificada, priorizada, accionable; preferencias granulares por canal. El moat de delta hecho visible al
usuario final. **Secciones:** nav bell + drawer universal · vista completa + filtros (8 tipos) · **feed de
alertas** (agrupación temporal, severidad por color) · taxonomía (PRECIO_BAJADO el rey, NUEVO_STOCK, AGOTADO,
FOTO/KM_ACTUALIZADO, MATCH, SISTEMA) · preferencias (tipos × canales + umbrales €/%) · detalle drawer (sparkline
precio) · historial · onboarding persuasivo. **Media estrella:** el **feed con SSE en vivo** (nueva notificación
entra con flash de borde cobalt) + sparkline de precio en el detalle. **Botones clave:** campana (SSE) · pills
filtro (URL) · ver vehículo (→ficha) · buscar similares (→/explore con filtros del agotado) · toggle preferencia
· umbral % (debounce). **Data:** delta+first_seen/last_seen+VAM = now; tabla notifications+preferences+SSE+push
web = near; WhatsApp+email+resumen B2B = future. **Comparable:** AutoTrader/CarGurus/Wallapop/mobile.de alerts;
superamos: delta de km+foto+precio sobre censo verificado en tiempo real con umbrales. **Fase:** 80% now.

### 3.15 Cobertura territorial / Expansión `/cobertura` — [NOW]
**Propósito:** el tablero del 100% — cada provincia, segmento y gap confesado; prueba estadística + producto
de inteligencia territorial + narrativa de dominio + ancla de expansión Europa. **Secciones:** nav persistente
(estado nacional vivo) · **hero mapa 3D pinned (scroll-scrubbing)** que enciende provincias en orden de
cobertura · stats nacionales (94,3% + certificado MSE) · tabla CCAA · **panel de gaps honestos** (5 cards con
causa) · mapa interactivo + ProvincePanel · tabla 52 provincias (CSV) · metodología (captura-recaptura) ·
**expansión Europa** (shader radar + waitlist) · comparativa de mercado · CTA final. **Media estrella:** el
**hero scroll-scrubbing** que narra la construcción del censo provincia a provincia (equivalente al opening-map
de GTA VI, pero con el censo real). **Botones clave:** click provincia (ProvincePanel + `?prov=`) · ver
metodología (gap card) · ordenar/export CSV · acceso anticipado API Europa (lead). **Data:** `/geo/seal`,
`/geo/exhaustiveness`, `/geo/completeness`, `/stats`, `/geo/{prov}/entities` (now); CCAA agrupado + tendencia +
waitlist + mapa Europa shader = near; denominador municipal + sells_cars + Tier-1 walled + países live = future.
**Comparable:** Indicata (rigor) + Carfax (certificado) + GTA VI (scroll-storytelling); **sin competidor
directo — territorio propio.** **Fase:** núcleo now; tendencia+waitlist+Europa = near; gaps data/spend-gated = future.

### 3.16 Sistema de diseño + IA global — [NOW base / NEAR componentes]
**Propósito:** el sistema nervioso — tokens canónicos, navegación, auth por capas, sitemap, estrategia global
de media que mantiene coherencia del hero 3D al último panel. **Contenido:** §1 tokens canónicos (base viva en
`tokens.css` + 12 que faltan: glass, glow, gradients, radius-card, z-drawer, ease-reveal, text-display) · §2
sitemap completo · §3 navegación (3 layouts) · §4 auth por capas · §5 estrategia de media (árbol de decisión
por slot) · §6 motion choreography global (4 capas) · §7 componentes globales (existen Badge/Panel; faltan 12:
Button, Input, Select, Spinner, EmptyState, ErrorBoundary, Drawer, PriceRatingBadge, VehicleCard, EntityCard,
StatTicker, CoverageBar). **Media estrella:** el propio **árbol de decisión de media** (§4 de este blueprint).
**Fase:** tokens base+layout+nav+mapa+Badge/Panel+API tipado = now; 12 tokens + 12 componentes + Drawer +
motion.css + auth + dataviz = near; video generado + AuthLayout + dashboard B2B = future.

---

## 4 · PLAN DE MEDIA GLOBAL (la delegación del owner)

Árbol de decisión: por cada hueco, ¿imagen real / generada / stock / VIDEO / 3D / shader / dataviz / animación?
**Regla madre: el dato real ES el media.** Se genera o renderiza solo donde el dato no existe o la experiencia
exige cinemática. Coherencia: una sola atmósfera (charcoal + cobalt), cero AI-slop.

| Slot (dónde) | Tipo | De dónde sale | Fase |
|---|---|---|---|
| Hero landing / explore / cobertura / dashboard mini / community / vehicle-mini | **3D R3F** | `SpainMap.tsx` existente, datos `/geo/seal` vivos (extrusión por cobertura, color por verdict) | now |
| Atmósfera hero (partículas/niebla/grano) | **shader R3F** | GLSL propio reutilizado entre superficies, €0 | now/near |
| Foto de vehículo (card, ficha, garaje, anchor, inbox, notif) | **imagen real** | `photo_url` del inventario (2,2M fotos en DB) | now |
| Fallback sin foto | **imagen generada (SVG inline)** | 7 siluetas de carrocería sobre `--surface-2`, €0, nunca stock | now |
| Identidad de dealer (card, ficha, anchor) | **generada procedural** | monograma/iniciales con color hash del nombre; logo real si `logo_url`/favicon existe | now |
| Category art de entidad (7 kinds) | **generada (Higgsfield)** | 1 imagen cinematográfica por EntityKind, batch único, versionada | near |
| Mapa de calor / treemap / heatmap señales | **3D R3F / dataviz D3** | `SpainMap` colorMode + D3 treemap; datos `/geo/seal` + delta | now |
| Charts (historial precio, OHLC, P&L, observatorio, histograma) | **dataviz** | recharts/D3 con tokens CARDEEP (cobalt sobre ink, estilo TradingView), datos delta/history | now |
| Sparklines (sidebar, notif, anchor) | **dataviz** | SVG puro / d3-shape, `/vehicles/{ulid}/history`, €0 | now |
| Garaje — escena de coche | **3D R3F** | MeshReflectorMaterial + foto real como textura; GLB real (generate_3d) | now / future |
| Particle field del delta (intel, API hero) | **shader R3F** | GLSL, eventos del `/delta` mapeados a posición/color | now |
| Estado vacío (sin resultados) | **shader R3F / stock curado** | shader de puntos (explore/intel); fotos emocionales del tablero Pinterest (onboarding/404) tratadas en tono cobalt | now |
| Skeleton / loading | **animación CSS** | shimmer keyframe, €0, nunca spinner global | now |
| Iconos de evento / plataforma / kind | **generada (SVG/Lottie)** | SVG inline propios + 6 Lotties de evento <5KB, €0 | now |
| Code blocks (API, landing) | **animación** | typewriter CSS sobre código real del `API_CONTRACT.md` | now |
| Hero video de fondo | **VIDEO generado (Higgsfield)** | conducción nocturna ciudad ES estilo GTA VI, modo atmos opacity baja | future (gasto) |
| Feature/article art (noticias) | **generada (Higgsfield) + 8 base por categoría** | 1 imagen por artículo featured; set base reutilizado por categoría | near |
| Mapa Europa (cobertura) | **shader R3F** | LineSegments GeoJSON Natural Earth + radar scan, ES en cobalt | near |
| Logo / icono marca | **activo real** | `/brand/cardeep-icon-blue.png` + wordmark, nunca regenerar | now |
| Badge VAM / veredicto | **animación CSS** | glow semántico por `SealVerdict`, dot pulsante en SELLADO | now |

**Disciplina anti-slop:** ninguna imagen de stock genérico salvo el slot de empty-state/onboarding (curado del
tablero Pinterest del owner, tratado en tono cobalt). El gasto de media generada (Higgsfield/video) se difiere
hasta luz verde del owner; el producto es 100% funcional con dato real + shaders €0 sin ese gasto.

---

## 5 · SISTEMA DE DISEÑO

### 5.1 Tokens de marca (canónicos — sellados a la marca)
```
/* BASE — charcoal cinematográfico */
--ink            #0A0E17     /* fondo (deja brillar el 3D) — alias operativo de Deep Charcoal */
--charcoal-brand #111B27     /* charcoal de marca para superficies de marca/print */
--surface-1/2/3  #0F1626 · #161F33 · #202C46
--line           #283356     --glass-border  rgba(59,130,246,0.15)
--glass-bg       rgba(15,22,38,0.72)  /* + backdrop-filter blur(20px) saturate(140%) */

/* TEXTO */
--text-1/2/3     #EEF2FB · #9AA6C4 · #5D6A8C

/* ACENTO — COBALT BLUE (marca, acción, identidad) */
--accent         #3B82F6     --accent-hi  #60A5FA     --accent-dim  #1E5FD0
--on-accent      #04122E
--accent-2       #6366F1     /* indigo SOLO foco/rim 3D — nunca CTA */
--gradient-cobalt  linear-gradient(135deg,#3B82F6 0%,#1D4ED8 100%)
--gradient-data    linear-gradient(180deg,transparent,rgba(8,12,21,0.95))

/* DATOS SECUNDARIOS — cian retirado como acento; permitido solo en señal viva */
--signal-live    #35E0D0     /* sparkline/ticker "vivo", NUNCA CTA ni identidad */

/* SEMÁNTICO precio/veredicto (el ADN-inteligencia) */
--price-good/fair/high  #22C55E · #F5B33C · #F0556B
--seal-sellado/parcial/gap  → accent · price-fair · price-high
--glow-seal  0 0 32px rgba(59,130,246,0.22)   --glow-gap  0 0 20px rgba(240,85,107,0.25)
```
**Migración:** las specs que heredaron `#35E0D0` como CTA se reescriben a `#3B82F6`. El cian solo
sobrevive como `--signal-live` en elementos de "dato respirando" (ticker, sparkline). La rampa de cobertura
del mapa pasa a `GAP #F0556B → PARCIAL #F5B33C → SELLADO #3B82F6` (sellado en cobalt, no cian) para
coherencia de marca.

### 5.2 Tipografía
- **Display/hero:** una grotesca con carácter (Clash Display / Outfit variable). `--text-display: clamp(3.5rem,2rem+8vw,8.5rem)` (portada) · `--text-hero: clamp(2.75rem,1.5rem+6vw,6.5rem)` · `--text-hero-tight: line-height 0.92`.
- **UI/cuerpo:** Inter / Geist — legibilidad densa.
- **Datos/mono:** Geist Mono / JetBrains Mono con `tabular-nums slashed-zero` — precios, `cdp_code`, timestamps SIEMPRE en mono (alineación de terminal). Precio en extra-bold oversized = ancla visual (lección de la auditoría).

### 5.3 Motion
- Durations: `--dur-fast 140ms` · `--dur 260ms` · `--dur-slow 520ms`.
- Curvas: `--ease-out cubic-bezier(0.16,1,0.3,1)` (defecto) · `--ease-reveal cubic-bezier(0.22,1,0.36,1)` (entrada hero/paneles).
- **Solo `transform`/`opacity`/`clip-path`/`filter(blur)`.** Nunca width/height/top/margin. `will-change` solo justo antes, removido al terminar.
- Stagger en listas: 40ms/item, máx 5 visibles (240ms total). `prefers-reduced-motion`: todo a opacity-only, 20ms.

### 5.4 Atmósfera 3D
- Base `#0A0E17` con gradiente radial cobalt fijo (profundidad, nunca negro plano).
- `SpainMap` con MeshStandardMaterial emissive por verdict, FogExp2 density 0.08, Bloom sutil (threshold 0.85, strength 0.3) → SELLADO brilla en cobalt. OrbitControls limitados, autorotate con guard reduced-motion. Chunk Three.js lazy (~249KB gzip).
- 3D solo donde demuestra (landing/explore/cobertura/garaje/intel/dashboard-mini). Las superficies de productividad (cross-posting, finanzas tablas, terminal charts) usan dataviz 2D — el 3D pesado es inapropiado para trabajo repetitivo.

### 5.5 Componentes (atom-level)
- **Existen:** `Badge`, `Panel`, `SpainMap`+`Province`+`mapColors`, `Certificate`, `VehicleCard`, `DealerCard`, `ProvinceGrid`, `DealerBrowser`, API tipado (`client/hooks/types`).
- **Faltan (near, en orden):** Button (gradient-cobalt primario / borde / ghost / loading) · Input · Select · Spinner · EmptyState · ErrorBoundary · Drawer (móvil) · PriceRatingBadge · StatTicker (countUp) · CoverageBar · EntityCard · CardSkeleton.
- **Patrón común:** named exports, leen tokens vía CSS custom properties (cero hardcode de color en TSX), props tipadas con interface explícita. Container max 1440px. Breakpoints 320/480/768/1024/1280/1440. `aspect-ratio` declarado antes de cargar media (CLS 0).
- **Glass:** paneles flotantes con `--glass-bg` + blur + border `--glass-border` 1px. Cards con sombra de contacto `0 8px 24px rgba(0,0,0,0.45)`, nunca plana.

---

## 6 · ROADMAP POR FASES

### NOW — construible YA sobre el dato real (orden de construcción superficie-por-superficie)
> Estado del repo: P0–P5 verdes (Landing, Explore, Dealer, Vehicle funcionan contra API viva).
> El trabajo NOW es elevar de "funcional" a "cinematográfico" + sellar el design system.

0. **Sistema de diseño (§16):** 12 tokens nuevos + migración cian→cobalt + 12 componentes UI + `motion.css` + Drawer. **Bloquea a todo lo demás — primero.**
1. **Landing** → elevar a cinematográfico (countUp, coreografía de entrada, pilares, code block, grid 52).
2. **Marketplace `/explore`** → layout split unificado + URL-state + reuso de SpainMap/DealerBrowser/VehicleCard.
3. **Ficha vehículo** → hero galería + rail sticky + timeline historial (todo el wire verificado) + plataformas + alias.
4. **Garaje 3D** → subruta del dealer; SceneStage + CarProxy photo-card + Rail + CompareMode + DeltaFeed.
5. **Terminal** → ChartPanel OHLC + EventFeed + Inspector + Heatmap + Watchlist (localStorage) + Alerts/Sources.
6. **Inteligencia & Arbitraje** → hero particle + Market Pulse + heat-map de señales (P50 sobre subset) + chart individual.
7. **Cobertura territorial** → hero scroll-scrubbing + stats + certificado + tablas CCAA/provincias + gaps + metodología.
8. **API marketplace** → marketing + pricing + matriz endpoints + quick-start con snippets reales.
9. **Noticias** → ticker + observatorio (mini-mapa + dataviz) + grid (el 70% sin pipeline).
10. **Centro de notificaciones** → nav bell + feed + preferencias + drawer (el 80% sobre delta).
11. **Comunidad** → UI + sidebar de mercado (componentes de dato CARDEEP day-1; capa social = future).
12. **Deepy** → UI completa (widget transversal); funciona en cuanto exista el BFF LLM (near).

### NEAR — gap pequeño (1 endpoint / 1 tabla / 1 migración)
- **Backend de datos:** `/inventory/search` (facetas globales), `/inventory/makes`, `/geo/{prov}/stats`, `/market/stats`, `/market/velocity`, `/delta` paginado, `/vehicles/price-movers`, `/entities/active`, `/entities/recently-verified`, `/geo/exhaustiveness` (redeploy).
- **Deepy:** BFF `/deepy/chat` (litellm + GPT-4o-mini o Ollama €0, tool-calling ReAct).
- **Auth Capa 1:** Supabase magic-link + Google OAuth, JWT httpOnly, ProtectedRoute, AuthLayout.
- **Persistencia:** tablas `notifications`/`notification_preferences`, `publish_job`/`platform_credentials`/`inbox_thread`/`inbox_message` (migraciones 0033–0035), watchlist/alertas de usuario, SSE + push web.
- **Pipeline editorial:** worker de generación de artículos (análisis estadístico del delta + tabla `news` migración 0033) + RSS.
- **Media generada (batch único):** 7 category-art por kind + 8 base de categoría de noticias + mapa Europa shader.
- **Price-rating real:** job de agregación de distribución por make·model·año·provincia (datos ya existen).
- **Componentes near:** mapa 2D split (Maplibre) en explore, MuniPin, dataviz recharts.

### FUTURE — data / compute / spend-gated (orden = decisión del owner)
- **Europa → mundo:** F0 del primer mercado extranjero; todo lo geo ya parametrizable.
- **Inteligencia profunda (Indicata-style):** capa analítica sobre el delta acumulado (curva de depreciación, liquidez, tiempo en mercado, score de confianza ML).
- **Terminal full:** market intelligence + per-tenant rate limits + SLA HA.
- **Capa social completa:** servicio + tablas users/threads/posts/votes/reputation; motor de reputación; ActivityBanner shader.
- **Deepy avanzado:** RAG sobre fichas, alertas personalizadas, predicción de precio.
- **Garaje:** GLB 3D real (generate_3d), configurador color/acabado, WebXR/AR.
- **CRM/finanzas full:** integración cross-posting con plataformas (acuerdos API), financiación (partner), previsión de demanda, scoring de cierre.
- **API marketplace:** cobertura Tier-1 walled (Wallapop/Milanuncios spend-gated), `/geo/exhaustiveness` en Enterprise.
- **Datos externos:** ITV/propietarios (DGT/registral), GANVAM/Eurotax, etiqueta DGT por matrícula.
- **Media:** video hero generado (Higgsfield), generación continua de imágenes editoriales.
- **Notificaciones:** WhatsApp Business API, email transaccional, resumen B2B de competencia.

### Secuencia macro (dependencias)
```
Design System (§16) ──► [Landing, Explore, Vehicle, Dealer, Garaje]  (NOW, paralelizable tras el DS)
        │                          │
        ▼                          ▼
   [Terminal, Intel, Cobertura, API, Noticias, Notif, Community]  (NOW, dependen de tokens+componentes)
        │
        ▼
   Auth Capa 1 ──► [Deepy backend, Notif persist, Community social, Alertas, Garaje favoritos]  (NEAR)
        │
        ▼
   Auth Capa 2 (dealer) ──► [Dashboard, Flota, CRM, Finanzas, Cross-posting, Inbox, API dashboard]  (FUTURE)
        │
        ▼
   Europa F0 + Inteligencia profunda + ML  (FUTURE, spend/data-gated)
```

---

**Cierre.** El producto se construye sobre un backend real y verificado; el frontend tiene base probada
(P0–P5 verdes). La ruta crítica es: **sellar el design system → elevar las superficies NOW a cinematográficas
sobre el dato real → auth Capa 1 para desbloquear el NEAR → auth Capa 2 para el B2B FUTURE → Europa.** Ninguna
superficie miente sobre su fase; cada media tiene origen declarado; cada botón tiene lógica; €0 hasta que el
owner autorice gasto. Marca fiel: cobalt, charcoal, white — el cian se retira a señal de dato secundaria.
