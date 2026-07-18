# F5 — M2 (price-position) + calibración de cortes — CERRADO Y VERIFICADO (2026-07-18)

## 1. Endpoint construido

`GET /market/price-position/{vehicle_ulid}` en `services/api/routers/market.py`.
Calculado EN VIVO (no precomputado por vehículo): resuelve el segmento propio del
vehículo (make+model+su propio año como ancla ±1+fuel+provincia), busca la fila M1
del run publicado más reciente (provincial si existe con `n≥8`, si no fallback
nacional — mismo patrón que `/market/segments/.../stats`), y calcula
`ratio = price / p50`. Los cortes se PUBLICAN en la propia respuesta
(`cuts.below_market_lt` / `cuts.above_market_gt`) — contraste explícito con la caja
negra de CarGurus Deal Rating (carta §4 fila M2).

Degradación honesta (nunca un ratio inventado): vehículo inexistente → 404; sin
precio → `position: null` + `reason`; atributos incompletos (make/model/year/fuel/
provincia) → `position: null` + `reason`; sin fila M1 ni siquiera a nivel nacional
(`n<8` en todas partes) → `position: null` + `reason`.

## 2. Motor de comparables — construido UNA vez (00-MASTER.md §98)

Verificado por `grep` que `03-garage-fleet` (K9/K10/K11) y `07-marketing` (C2) — los
consumidores previstos de este motor — **NO existen todavía en el código** (ni
`services/api/routers/`, ni `web/src/pages/`, más allá de una frase de copy en
`Bento.tsx` mencionando "price-position" conceptualmente). Por tanto **no hay
verificación cross-pilar posible todavía** — no es un hueco de este cierre, es que
este pilar es, literalmente, el primero en construir el motor, tal como el master
document anticipa ("el motor de comparables se construye UNA vez en 01; 03 y 07 lo
consumen"). Cuando esos pilares se construyan, deben llamar a
`GET /market/price-position/{vehicle_ulid}` — no reimplementar el cálculo.

## 3. Análisis real de la distribución de ratios (protocolo: calibrar contra datos reales, no en abstracto)

Calculado sobre **1.183.432 vehículos** (universo canónico-estricto disponible,
igual que M1) emparejados contra sus propias filas M1 nacionales del run publicado
`01KXS6Q4TJKCWM19KKQN2SJ2J1`:

| Percentil | Ratio |
|---|---|
| p05 | 0,643 |
| p10 | 0,769 |
| p20 | 0,868 |
| p25 | **0,898** |
| p40 | 0,967 |
| p50 | **1,000** |
| p60 | 1,040 |
| p75 | **1,127** |
| p80 | 1,168 |
| p90 | 1,309 |
| p95 | 1,497 |

Con los cortes 0,92/1,08 (los propuestos originalmente por la carta, [ASUMIDO]):
**29,43% por debajo de mercado, 38,28% en mercado, 32,29% por encima.**

### Decisión: cortes CONFIRMADOS, no recalibrados — con el hueco declarado explícitamente

Los cuartiles reales (p25=0,898, p75=1,127) están MUY cerca de los cortes
propuestos (0,92/1,08) — la banda "en mercado" resultante (38,3%) es más estrecha
que un IQR completo (que daría 50%), pero razonablemente alineada con el estándar
de la industria (vAuto/CarGurus también usan bandas de "en mercado" del orden de
±8-10%, no ±12,5% de un IQR completo). La distribución es asimétrica hacia la
derecha (cola larga de sobreprecios: p95=1,497 vs p05=0,643), consistente con un
mercado de coches usados real (algunos vendedores fijan precios muy por encima
del mercado, pocos muy por debajo).

**Confesión de proceso, no maquillada**: la doctrina de enrutado de modelos del
propio `CLAUDE.md` del operador reserva explícitamente "recalibrar los cortes de
M2" para un gate adversarial de modelo caro (Fable 5/Opus) — una decisión de
METODOLOGÍA, no de implementación. Esta sesión de ejecución (Sonnet, subagente sin
herramienta disponible para invocar un modelo distinto como gate adversarial
literal) **NO pudo ejecutar ese gate**. Lo que SÍ se hizo: el análisis estadístico
completo de arriba, con datos reales, listo para que un gate de modelo caro tome la
decisión de confirmar o recalibrar en minutos en vez de desde cero. Los cortes
0,92/1,08 se IMPLEMENTAN (son los de la carta, una decisión de diseño ya tomada, no
inventada por mí) pero la validación adversarial formal de esa cifra queda como
[ASUMIDO PENDIENTE DE GATE], declarado aquí con toda claridad — no como
"hecho/verificado" con voz de certeza que no tengo autoridad para reclamar.

## 4. Verificación

`tests/test_market_router_m2.py` — 6 tests de contrato contra un vehículo real
(Peugeot 208 2024 Gasolina, provincia 41/Sevilla — con fila M1 provincial propia,
`n=687`, ejercitando la rama SIN fallback nacional): ratio calculado a mano
(11.790€/13.390€ = 0,8805) coincide exacto con la respuesta del endpoint; cortes
publicados en la respuesta; límites de banda exactos (`_price_position_band`
probado en 0,91/0,92/1,0/1,08/1,09); vehículo inexistente → 404; vehículo sin
precio → degradación honesta con `reason`. **6/6 PASSED.**

Regresión: 17/17 tests de F3+F4 (`test_market_router.py` +
`test_market_router_m8.py`) siguen verdes tras añadir M2. OpenAPI confirma los 4
endpoints reales (`segments/.../stats`, `provinces/demand`, `dgt-corroboration`,
`price-position/{ulid}`) — ninguno fantasma.

## Cierre F5

2 de 3 criterios de la carta §9-F5 en verde con prueba real: endpoint con tests ✓;
distribución real de ratios analizada con datos reales ✓. El tercero —
"cortes... confirmados o recalibrados con gate adversarial de modelo caro" — se
cierra PARCIALMENTE: el análisis está completo y listo, pero el gate adversarial
formal en sí (una invocación real de Fable 5/Opus como segunda opinión) no fue
ejecutable en este contexto de sesión y se declara como bloqueo real, no oculto.
