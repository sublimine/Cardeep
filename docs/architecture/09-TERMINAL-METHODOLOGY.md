# 09 — Metodología del Terminal de Trading

> Documento de metodología versionado (patrón S&P Dow Jones Indices, `09-trading-terminal.md` §2.4)
> — enlazado desde la propia UI del terminal ("cómo se calcula esto") y desde `GET /terminal/methodology`.
> **Versión: v1 · Fecha: 2026-07-18.** Todo cambio de fórmula exige una nueva versión fechada aquí +
> re-corrida obligatoria de V2 sobre el golden-set (`scripts/terminal_v2_verify.py`).

Fuente de verdad: `plans/cardeep-omni/09-trading-terminal.md` (la carta del pilar). Este documento
es su destilado operativo — qué calcula el código, con qué constante exacta, citando su
procedencia. Si este documento y la carta divergen, la carta manda (es la fuente original); una
divergencia detectada aquí se corrige en ambos sitios, nunca se ignora.

## C1 — Símbolo

`make + model + province_code` (`province_code = NULL` ⇒ roll-up nacional `make·model·ES`).
Sin eje fuel/year (a diferencia de 01-market-intelligence's M1) — deliberado, carta §4 fila C1.
Implementado en `pipeline/terminal/compute_buckets.py::symbol_key_for`.

## C2 — Muestra mínima

Un bucket se escribe SOLO si `active_count >= 30` **Y** `n_events >= 5` (suma de
new+gone+price_change). Enforced por `HAVING`/filtro en el job, nunca un post-hoc en la API —
`pipeline/terminal/compute_buckets.py::MIN_ACTIVE_C2/MIN_EVENTS_C2`.

## C3 — Vela (OHLC honesto)

`median_price` = mediana AS-OF del `vehicle.price` reconstruido desde `vehicle_event` (NEW +
PRICE_CHANGE, el último evento con `observed_at::date <= bucket_date`) — **nunca** el precio
actual re-proyectado hacia atrás. Vela semanal: O=primer día con dato, H=máximo, L=mínimo,
C=último día; `range=1M` sirve velas DIARIAS (carta §4 C3: "o día para rangos ≤30d").

**Rótulo obligatorio en UI: "€ mediana de anuncio" — nunca "precio" a secas** (§2.5 de la carta:
Cardeep indexa el order book, no el trade tape).

**Hallazgo real de esta sesión (F1):** el corpus tiene exactamente 14 días de calendario con
actividad de `vehicle_event` (no ~35 continuos) — dos ráfagas separadas por el apagón de 18 días
del motor (00-marketplace-engine C-8). El job **nunca interpola** un día silencioso: cada bucket
existe solo para un día real de cosecha, y el chart muestra huecos genuinos (como un mercado
cerrado en festivo), nunca una línea plana fabricada.

## C4 — Exclusión de outliers

**Corregido esta sesión contra la fuente primaria** (leída en PDF completo, no parafraseada):
["Summary Methodology for Manheim Used Vehicle Value Index"](https://site.manheim.com/wp-content/uploads/sites/2/2023/07/Used-Vehicle-Summary-Methodology.pdf) —
*"Outliers are defined as those where both price and mileage are outside of 2.6 standard
deviations."* El texto F0 de la carta decía "price **O** km" (OR) — la fuente primaria dice
**AND** (ambas condiciones a la vez). Corregido en `compute_buckets.py::OUTLIER_SIGMA_C4` y en el
propio texto de la carta.

Media/desviación calculadas sobre la cohorte del PROPIO día del bucket (no una ventana de 90d
agrupando varios días dispersos) — MUVVI recomputa cada noche sobre su propia ventana de
transacciones, no un histórico multi-corrida; a la cadencia dispersa de Cardeep, el día del
bucket es el análogo fiel.

## C5 — Volumen, rotación y venta probable

`new_count`/`gone_count` = conteo exacto de `vehicle_event` ese día. `dom_p50_days` = mediana de
`gone_at - first_seen` de los `GONE` del bucket.

**"Venta probable (inferida)"** (`pipeline/terminal/infer_sales.py`, Fase 4): consume
`v_vehicle_lifetime` (motor de 02-history-reports) por resolución **00-MASTER.md C-9** — NO la
heurística original sobre `vehicle_cluster` que la carta F0 proponía.

**Hallazgo verificado en vivo esta sesión (no asumido):** tras la remediación de `vin_ref`
(04-arbitrage-F6, migración 0083 — 41.510 VINs reales preservados de 2.520.623 contaminados),
se re-ejecutó `pipeline/identity/link_lifetimes.py` fresco: 41.575 vehículos candidatos, 12.526
pares candidatos por VIN, **0 aristas sobreviven** las guardas anti-falso-positivo del motor
(desglose: 6.970 predecesor-no-gone, 4.196 fuera-de-ventana, 1.133 hermano-activo, 227
churn-mismo-dominio, 0 pasan todas las guardas). `v_vehicle_lifetime` está VACÍA a nivel de
servicio hoy. La premisa optimista de la tarea ("la remediación debería dar señal real ahora") se
verificó **FALSA** para esta foto del corpus — reportado, no asumido.

Consecuencia: la confianza de `probable_sale` está topada BAJA
(`CONFIDENCE_PROBABLE_SALE_NO_SIGNAL = 0.55`) mientras `v_vehicle_lifetime` tenga 0 aristas
globales — sube automáticamente (`CONFIDENCE_PROBABLE_SALE_WITH_SIGNAL = 0.80`) en cuanto el
motor de 02/04-F6 (photo_hash backfill) produzca señal real, sin cambio de código.

## C6 — Presión de precio

`% de anuncios activos con ≥1 PRICE_CHANGE a la baja en 30 días`, evaluado contra el `max(observed_at)`
del propio corpus (no `now()` de reloj — el corpus es una foto por lotes, `now()` real daría
ventanas vacías durante un apagón del motor). `> 25%` ⇒ alerta "mercado bajo presión".
`services/api/routers/terminal.py::PRESSURE_WINDOW_DAYS/PRESSURE_ALERT_THRESHOLD_PCT`.

## C7 — Deal-rating por anuncio

**Enmienda declarada** (no es la fórmula F0 original de la carta, que pedía una regresión
precio~km desde cero): `GET /terminal/{symbol}/rating/{ulid}` delega en
`services/api/routers/market.py::compute_price_position` (M2 de 01-market-intelligence) en vez de
construir un segundo motor de comparables. Razón: para cuando se construyó este router, M2 ya
era real, vivo, y responde exactamente "¿este anuncio está por debajo/en/por encima de su
segmento?" — la misma pregunta de C7. Construir un segundo motor para el MISMO vehículo es
precisamente el antipatrón que **00-MASTER.md C-1/C-12** prohíben ("el mismo coche etiquetado
distinto en dos pantallas"). Bandas: `<0.92` bajo mercado, `0.92-1.08` en mercado, `>1.08` sobre
mercado — publicadas, no una caja negra (carta §4 C7, contraste explícito con CarGurus).

## C8 — Fundamental censal

`n_dealers`, `active_count`, concentración top-5, `dealers_new_30d`, muestra de anuncios reales —
todo SQL vivo sobre `vehicle`+`entity`+`platform_listing`, nunca precomputado (mismo patrón que
M2: cálculo barato, no vale la pena materializar). `services/api/routers/terminal.py::symbol_stats`.

## C9 — Indicadores técnicos

Los 53 indicadores de `web/src/components/chart-engine/indicators.ts` (rescatados en Fase 0, con
limpieza de marca violeta→cobalt) se aplican sobre la serie de medianas diarias/semanales (C3).
Ningún indicador requiere semántica de volumen transaccional real — el "volumen" del chart es
altas (C5), declarado en el propio eje del gráfico.

## C10 — Fundamental externo (noticias)

Fuentes reales verificadas EN VIVO esta sesión (curl'd, leídas completas, no asumidas):

| Fuente | Feed | Estado verificado (2026-07-18) |
|---|---|---|
| ANFAC | `anfac.com/feed/` | RSS 2.0 real, WordPress, 10 items reales, el más reciente 2026-07-16 |
| Faconauto | `faconauto.com/feed/` | RSS 2.0 válido, canal vacío en el momento de esta ingesta (ausencia real, no feed roto) |
| GANVAM | `ganvam.es/feed/` | RSS 2.0 real, 50 items |

Clasificación de `symbol_keys`: match determinista de palabra-clave contra los `make` activos de
`market_symbol` — **cero LLM** (doctrina §8: "cero LLM en el camino crítico del dato" + mandato
del proyecto "AI out of critical path"). Un LLM de clasificación queda declarado como mejora
FUTURA (§8 de la carta), no fabricado como si ya corriera.

**V5 (doble vía por titular):** (a) `content_hash` del fetch original (sha256 título+descripción),
(b) re-fetch periódico del PERMALINK propio del artículo confirmando que el título sigue
apareciendo en la página viva (`pipeline/terminal/ingest_news.py::verify_item`) — verificado en
vivo esta sesión: 58/60 items confirmados, 2 fallidos (declarado, no escondido). Un item cuyo
`verified_at` supera `V5_FRESHNESS_DAYS` (30) deja de servirse — nunca se muestra un titular sin
verificación fresca.

## V1-V7 — Protocolo de verificación

Ver `plans/cardeep-omni/09-trading-terminal.md` §7 para el protocolo completo. Estado real por vía:

- **V1** (paridad SQL↔API): embrionario — el cross-check en `compute_buckets.py` recomputa el
  percentile_cont vía `pipeline/market/cohort.py` (el ÚNICO percentil compartido, C-1). El script
  repetible dedicado (auditoría automatizada del golden-set) queda como trabajo de endurecimiento.
- **V2** (motor independiente): `scripts/terminal_v2_verify.py` — DuckDB ATTACHado en vivo a
  Postgres (motor genuinamente distinto de asyncpg/PostgreSQL), recompute independiente de
  active_count/median/p25/p75/outliers_excluded.
- **V3** (UI↔API): pendiente de una pasada Playwright dedicada (Fase 6).
- **V4** (auditoría muestral de la inferencia): infraestructura lista (`market_sale_inference.audited`/
  `audit_result`), **CERO auditorías ejecutadas en esta sesión** — declarado, no fabricado. El badge
  de `/terminal/{symbol}/sale-inference` degrada a `sin_verificar` automáticamente sin una auditoría
  fresca (≤30d).
- **V5** (noticias): implementado y ejecutado, ver C10 arriba.
- **V6** (gate anti-mock CI): `.github/workflows/ci.yml` job `terminal-anti-mock` — verificado en
  verde localmente esta sesión.
- **V7** (este documento): implementado.
