# cardeep · Inteligencia de Arbitrage (F4)

> Mismo tratamiento que la inteligencia: auditado el sub-universo wholesale/subastas (17 empresas
> `wholesale-intelligence` + auction en `companies/*.md`) y diseñadas las señales de arbitrage que cardeep
> puede computar desde su censo vivo. El arbitrage es la Capa 2 premium de `CARDEEP-OFFERING.md` — el billete.

## 0. Cómo hace arbitrage el sector hoy (lo auditado)
- **Manheim (MMR — Manheim Market Report):** el índice wholesale de referencia en NA; precio mayorista por
  configuración + ajuste por condición/km. vAuto/Cox lo usan para sourcing y "price-to-market".
- **BCA / AUTO1 / OPENLANE / ACV (MarketReport, ClearCar) / CarOffer / Dealer Auction / Autorola / USS /
  Motorway:** datos de puja, precios de remate, demanda B2B, spreads de remarketing; sourcing mayorista.
- **Copart / IAA:** salvage — arbitrage de siniestrados.
- **Patrón común y su LÍMITE:** todos viven en la pata **wholesale** (subasta/B2B), con **muestra** de
  transacciones y datos **gated**. Ninguno unifica wholesale + retail + particular + cross-platform en vivo.

## 1. La superficie de arbitrage de cardeep (su edge)
cardeep ve el **mercado retail/particular completo y vivo** (la pata más grande y donde compra/vende el dealer),
con **delta**, **dedup cross-platform**, **micro-geo** e **historial verificado**. Eso habilita señales que el
sector wholesale-only no puede dar:

1. **Buy-side mispricing (chollos):** anuncio por debajo de su valor de mercado real (residual / robust-z < −2
   contra TODO el comparable vivo) → oportunidad de compra/flip. cardeep tiene el mercado completo para fijar
   el "precio justo" y marcar lo infravalorado. **(Señal nativa, ya prototipada: sweet-spot/residual.)**
2. **Cross-platform gap:** el MISMO coche (dedup VIN/foto) listado más barato en plataforma A que en B → el
   precio de B prueba el mercado; compra en A. Sólo posible viendo todas las plataformas a la vez.
3. **Time-arbitrage:** days-on-market + trayectoria de Δprecio (delta) → predice el suelo / cuándo el vendedor
   capitula → temporiza la compra. Nadie con cobertura censal + delta lo ofrece.
4. **Geo-arbitrage:** mismo modelo más barato en provincia/comarca X que en Y (micro-geo INE) → compra X, vende Y.
5. **Wholesale→retail spread (con datos de socio):** precio de remate (de los players auditados, donde se
   acceda) vs el retail vivo de cardeep → margen de flip por modelo. (Requiere dato wholesale; la pata retail
   ya la posee cardeep.)

## 2. Producto de arbitrage
- **Deal-score por anuncio:** 0-100 (qué tan buena compra es), con el desglose (precio vs mercado, días, Δ,
  cross-platform). Badge en cada ficha del Marketplace.
- **Sourcing/alertas:** "chollos en tu radio/segmento" en tiempo real (sobre el delta SEEN + mispricing).
- **Spread dashboard:** margen de flip por modelo/zona (retail vs wholesale/otra zona).
- **Calculadora de flip:** compra estimada + coste + retail esperado + days-to-sell → ROI y plazo.

## 3. Colocación (coherente con `PLACEMENT-MAP.md`)
- **Ficha de coche:** badge deal-score + "−8% bajo mercado · 12 días · bajó 600€" (junto al price-position).
- **Vista Arbitrage/Sourcing (nueva, en el panel):** ranking de chollos, filtros por margen/zona/segmento,
  alertas. Patrón de las vistas de sourcing de vAuto/ACV MAX/Indicata, pero sobre el mercado retail completo.
- **Alertas:** push cuando aparece/baja un coche que cruza el umbral de deal-score.

## 4. Honestidad de alcance
- cardeep computa **directo** (sin terceros): mispricing, cross-platform, time, geo — toda la pata retail/
  particular, que es la superficie mayor de arbitrage para el dealer.
- El **wholesale→retail spread** necesita el dato de remate (MMR/subastas), gated → vía partnership/feed con
  los players auditados o estimación desde el propio histórico de "GONE" (precio al desaparecer). Marcado como
  dependencia, no como hecho.

## 5. Estado / siguiente
- [x] Sub-universo wholesale/arbitrage auditado (en `companies/*.md`).
- [x] Señales y producto de arbitrage diseñados (este doc).
- [ ] Implementación: deal-score + sourcing view sobre el censo (cuando se priorice el build).
