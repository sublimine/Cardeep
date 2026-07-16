# Mapa de monetización — qué info es gratis, qué es de pago

> Responde la pregunta del owner (2026-07-16): "exactamente qué tipo de info debe ir a cada uno, además
> qué tipo de info sería de pago, cuál no". Traduce el modelo de 3 capas de
> [`CARDEEP-OFFERING.md`](../intel-audit/CARDEEP-OFFERING.md) (síntesis de 109 auditorías) a decisiones
> concretas por página/widget de `web/`. No es teoría: cada fila abajo es una prop `plan` en el componente.

## 0. El principio de corte

Regla de una frase: **lo que es del dealer (sus propios datos: stock, deals, agenda, finanzas) es
SIEMPRE gratis — es su negocio, no la venden. Lo que es del MERCADO (observado del censo vivo,
verificado, cross-plataforma) es lo que cardeep vende, y ahí se corta en 3 capas.**

| Capa | Qué es | Plan mínimo | Ejemplo |
|---|---|---|---|
| **Datos propios** | CRM, inventario propio, agenda, chat, finanzas propias | Gratis (todo plan) | Stock, deals, facturas, contactos |
| **Capa 0 — Baseline** | Ficha básica del vehículo, valoración de lista, historial simple | **Starter** (gratis/entrada) | Specs, VIN, precio de lista |
| **Capa 1 — Diferenciadores** | Precio de mercado REAL, price-position, days-to-sell, delta en vivo, dedup, micro-geo, provenance VAM | **Scale** (pago, el hook) | "−8% bajo mercado · 12 días" |
| **Capa 2 — Premium/arbitrage** | Deal-score, sourcing/alertas de chollos, spread dashboard, calculadora de flip | **Enterprise** (pago, el billete recurrente) | Ranking de chollos, alertas push |

Razón de negocio (de `CARDEEP-OFFERING.md` §6): Capa 0 es gratis porque **sin ella cardeep no entra al
mercado** (paridad, no vende nada por sí sola). Capa 1 es el **hook** — se enseña un dato o dos gratis
("teaser") para que el dealer VEA que su coche vale −8% bajo mercado, y para ver el resto (distribución
completa, delta histórico) paga. Capa 2 es **el producto recurrente** — no se enseña nada gratis, solo un
contador ("3 chollos detectados hoy") + CTA, porque es lo que paga las facturas.

## 1. Por página/widget de `web/`

### Dashboard (`pages/Dashboard.tsx`) — home dealer-first
| Widget | Capa | Gratis muestra | Pago desbloquea |
|---|---|---|---|
| KPIs (stock/deals/margen/días) | Datos propios | Todo | — |
| Pipeline, Stale stock, Follow-ups, Activity | Datos propios | Todo | — |
| Posición mercado (price-position, days vs mkt) | **Capa 1** | 1 métrica agregada ("−3.8% bajo mediana") | Distribución p25/p75, tendencia histórica, por-modelo |
| Oportunidades (deal-score / chollos) | **Capa 2** | Contador ("3 chollos detectados") + 1 tarjeta borrosa de muestra | Ranking completo, filtros, alertas |
| Revenue/Coste, Top modelos | Datos propios | Todo | — |

### Inteligencia (`pages/Inteligencia.tsx`)
| Widget | Capa | Gratis | Pago |
|---|---|---|---|
| Ficha de coche: specs, VIN, precio de lista | Capa 0 | Todo | — |
| Residual/depreciación España vs UE | Capa 1 | Vista país propio | Comparativa cross-border completa |
| Days-to-sell (percentiles/mediana) | Capa 1 | Solo "tu dealer" | Top 10%/mediana/cola sector |
| Delta en vivo (SEEN/GONE/Δprecio) | Capa 1 | Últimos 3 eventos | Feed completo + históricos + export |
| Micro-geo (demanda por región) | Capa 1 | Mapa nacional agregado | Desglose provincia/comarca/municipio |

### Arbitrage (`pages/Arbitrage.tsx`)
| Widget | Capa | Gratis | Pago |
|---|---|---|---|
| Deal-score badge en ficha | Capa 2 | Solo el score numérico | Desglose (vs mercado/días/Δ/cross-platform) |
| Sourcing / ranking de chollos | Capa 2 | Contador + top-1 difuminado | Ranking completo + filtros margen/zona/segmento |
| Spread dashboard (retail vs wholesale) | Capa 2 | — (bloqueado, requiere dato wholesale de partner) | Cuando exista feed de socio |
| Calculadora de flip (ROI) | Capa 2 | — | Completo |
| Alertas push de chollos | Capa 2 | — | Completo |

### Inventario (`pages/Vehicles.tsx`) / Marketplace
| Widget | Capa | Gratis | Pago |
|---|---|---|---|
| Ficha propia (specs, fotos, estado) | Datos propios | Todo | — |
| Badge deal-score por anuncio (comparador) | Capa 2 | — | Completo (mismo gate que Arbitrage) |

### VIN Check / Dossier (`pages/check/*`)
| Widget | Capa | Gratis | Pago |
|---|---|---|---|
| Identidad + specs | Capa 0 | Todo | — |
| Historial (siniestros/km/propietarios) | Capa 0/1 | Resumen (nº de eventos) | Dossier PDF completo con detalle |
| Valoración retail/trade/residual | Capa 1 | 1 cifra | Rango completo + comparables |

### Analítica (`pages/Analitica.tsx`)
Vistas de informe sobre datos propios (KPIs/tendencia/embudo/canales/rotación) = **datos propios,
gratis**. Si en el futuro se añaden benchmarks contra el sector (percentil de tu dealer vs otros) eso
pasa a Capa 1.

### API & Tokens (`pages/Api.tsx`)
No es "gratis/pago" binario — es el **canal de venta** de todo lo anterior por API (medido en tokens,
ya construido en B6). Catálogo INFO (valoración/historial/market-intelligence/deal-score) e INVENTORY
(feed de stock) cobran por llamada según la capa del dato que sirven (Capa 0 barato, Capa 2 caro).

## 2. Mecánica de gating en UI (nueva pieza — ver `PremiumGate.tsx`)
- **Teaser (Capa 1):** el dato SÍ se muestra pero degradado — 1 métrica agregada visible, el desglose
  (distribución, histórico, cross-border) detrás de `PremiumGate` con blur + CTA "Desbloquear con Scale".
- **Contador + muestra (Capa 2):** nunca se enseña el dato completo gratis — solo un contador ("N
  detectados hoy") + 1 item de muestra difuminado, para crear deseo sin regalar el producto.
- **Datos propios:** nunca gateados, en ningún plan — es el dato del dealer, no de cardeep.

## 3. Planes (alineado con `pages/Pricing.tsx` / `pages/Api.tsx`)
- **Starter** (gratis): datos propios + Capa 0. Entrada sin fricción, el "empata" de `CARDEEP-OFFERING.md`.
- **Scale** (pago, el hook — Capa 1 completa): precio de mercado real, price-position, delta, dedup,
  micro-geo, provenance. El "billete" de entrada.
- **Enterprise** (pago, el billete recurrente — + Capa 2): arbitrage completo (deal-score/sourcing/
  spread/flip), alertas, API con cuota alta.

## 4. Estado
- [x] Estrategia de capas heredada de `CARDEEP-OFFERING.md` (ya sólida, 109 auditorías).
- [x] Este mapa: capas → páginas/widgets concretos de `web/` (este doc).
- [ ] Implementación: `User.plan` + `entitlements.ts` + `PremiumGate.tsx` (siguiente bloque).
- [ ] Aplicar el gate en Dashboard (Oportunidades) primero; extender a Inteligencia/Arbitrage/Check después.
