# F1 — Migración `0074_market_stat` + `compute_stats.py` (M1) — CERRADO Y VERIFICADO

> Ejecutado 2026-07-17/18. Depende de F0 (`01-market-intelligence-f0.md`), cuyos gates
> de diseño se aplican aquí sin reabrir la discusión.

## 1. Migración

- **Número real**: `0074_market_stat.sql` (NO `0073` como proponía originalmente la
  carta §5 — al momento de crear el archivo, `ls migrations/*.sql | sort | tail -1`
  mostró `0073_auth.sql` ya consumido por un frente paralelo. Renumerado sin choque,
  documentado en la cabecera del propio archivo de migración).
- Tablas: `market_stat_run` (una ejecución: metodología, ventana declarada, `n_in`,
  `metrics_computed`, `checks` JSONB, `published`) + `market_stat` (filas de agregado:
  `metric_id`, claves de segmento nullable según métrica, `n`/`p25`/`p50`/`p75`/
  `value_num`/`value_extra`, ventana, timestamp).
- Aplicada con `python -m scripts.migrate up` → `applied 0074 0074_market_stat.sql`.
- **Rollback probado**: `DROP TABLE market_stat; DROP TABLE market_stat_run;` ejecutado
  dentro de una transacción deliberadamente abortada (verificado: las tablas
  desaparecían tras el DROP, y sobrevivían intactas tras el abort) — sintaxis y
  reversibilidad confirmadas sin tocar el estado real.
- Índices: `idx_market_stat_run_published` (sirve "último run publicado"),
  `idx_market_stat_lookup` (patrón de consulta make+model+year+fuel+province),
  `idx_market_stat_province` (M5, futuro).

## 2. Helper compartido (`pipeline/market/cohort.py`)

Factorizado UNA vez per resolución C-1/C-12 de `00-MASTER.md` — los demás pilares
(03/04/06/07/09) lo importan en vez de reimplementar percentiles/medianas/ventanas.
Contiene: `MIN_COHORT_N=8`, `METHODOLOGY_VERSION="v1"`, `YEAR_BAND_RADIUS=1`,
`percentile_cont()` (reimplementación pura-Python de `percentile_cont` de PostgreSQL,
fórmula RN=1+q·(n−1) con interpolación lineal), `median()`, `divergence_pct()`.

**Verificado por 16 tests unitarios puros** (`tests/test_market_cohort.py`, sin DB):
valores de 10 elementos calculados a mano (p25=325, p50=550, p75=775 para
[100..1000] paso 100 — fórmula verificada dígito a dígito en el docstring del test),
casos borde (n=1, q=0, q=1, vacío, q fuera de rango), `divergence_pct` simétrico.
**16/16 PASSED.**

## 3. `pipeline/market/compute_stats.py` — M1

### Universo
Estricto: `v_canonical_vehicle WHERE vehicle_ulid = canonical_vehicle_ulid` (un único
run `vam_verified`, per F0 §6) ⋈ `servable_vehicle` (disponible, precio saneado, no
quarantined) ⋈ `entity` (province_code). Recomendación de F0 §9 aplicada literalmente.

### Segmentación M1
`make + model + banda de año ±1 (ancla) + fuel + province_code`, con fila nacional
paralela (`province_code=NULL`) por `make+model+fuel+año-ancla` — ambas computadas en
UNA sola sentencia SQL (CTE `base` materializada una vez, reutilizada por la rama
provincial Y la nacional, evitando pagar 2 veces el coste del escaneo de universo).
Regla dura `n<8 → nunca una fila` aplicada en el propio `HAVING` de SQL, no como
filtro posterior.

### Verificación — protocolo §7 de la carta, ambas vías ejecutadas

1. **SQL vs Python, 5 segmentos reales** (criterio F1 explícito): los 5 segmentos de
   mayor `n` del run se re-consultaron con una query RAW independiente (mismo filtro,
   sin `percentile_cont`), se ordenaron y recalcularon en `pipeline/market/cohort.py`
   puro. **Resultado: divergencia 0,0% en los 5 (n, p25, p50, p75) — tolerancia
   exigida <0,5%, superada con margen completo.** Segmentos verificados: Peugeot
   208/2008 (2023-2025), SEAT Ibiza 2024 — todos Gasolina, escala nacional (n entre
   5.072 y 7.026).
2. **Recuento de universo por 2ª vía independiente**: `n_in` del run = 1.241.426;
   recontado de forma independiente tras el run con una query ad-hoc separada (mismos
   filtros, lanzada por fuera del job) = **1.241.426 — coincide exacto**.

### Fixtures con percentiles precalculados a mano (criterio F1 explícito)

`tests/test_market_compute_stats.py` — 5 tests de integración, datos sintéticos
(`__CARDEEP_TEST_MAKE_*__`, nunca colisionan con inventario real) insertados dentro de
una transacción SIEMPRE abortada (mismo patrón de `tests/test_evict.py`), adjuntados
al ÚNICO `vehicle_cluster_run` `vam_verified=TRUE` real para resolver correctamente vía
`v_canonical_vehicle`:

- 10 precios `[100..1000]` paso 100 → hand-calculado p25=325/p50=550/p75=775 —
  **el SQL real de `fetch_m1` los reproduce exactos.**
- n=5 (<8) → **cero filas** (ni provincial ni nacional) — confirma la supresión dura.
- 5+5 repartidos en 2 provincias (cada una <8) → **ninguna fila provincial, SÍ fila
  nacional** (n=10, mismos p25/p50/p75 de arriba) — confirma el fallback nacional del
  §6 de la carta cuando la muestra provincial no alcanza.
- `run_compute()` escribe `market_stat_run`+`market_stat` con `published=FALSE`
  SIEMPRE en F1, y persiste el resultado del cross-check en `checks` JSONB.

**5/5 integration tests PASSED** (169,6s, contra la DB viva real, rollback confirmado:
verificado que `__CARDEEP_TEST_MAKE_N10__` NO existe en `vehicle` tras cada test).

## 4. Run de producción real (no sintético)

Ejecutado `python -m pipeline.market.compute_stats` contra el universo completo:

| Campo | Valor |
|---|---|
| `run_id` | `01KXS2KR1PDHPT3KE6X57BR85N` |
| `n_in` (universo canónico-estricto) | 1.241.426 |
| filas `market_stat` escritas | 117.652 (86.734 provinciales + 30.918 nacionales) |
| `published` | **FALSE** (criterio F1: "run de prueba con published=FALSE") |
| cross-check SQL vs Python | 5/5 segmentos, divergencia máxima **0,0%** |
| tiempo total | 221,3 s (~3,7 min — job batch, no camino de API; cadencia diaria es aceptable) |

**Auditoría post-run adicional** (más allá del criterio mínimo, verificación cruzada
propia):
- `min(n)` en las 117.652 filas = **8** — ninguna fila viola la regla dura.
- **0 filas** violan `p25 ≤ p50 ≤ p75` (monotonía de la distribución, sobre las
  117.652 filas completas, no solo la muestra de 5).
- Recuento independiente de `n_in` (query separada, fuera del job) = 1.241.426,
  coincide exacto con el `n_in` que el job escribió en `market_stat_run`.

## 5. Ventana declarada (gate F0 heredado)

`window_description` del run: *"M1: snapshot vivo (sin ventana temporal — distribución
de precio anunciado HOY sobre stock canónico disponible; banda de año ±1)"* — M1 no
tiene componente temporal de ventana móvil (es un corte transversal del inventario
disponible AHORA), por lo que el gate de span<90d de F0 no le aplica a M1 directamente
— sí aplicará a M3/M4/M7 en F2, donde se declarará explícitamente la ventana reducida.

## Cierre F1

Los 4 criterios de verificación de la carta §9-F1 están en verde con prueba real:
migración aplicada+rollback probado ✓; fixture con percentiles a mano test
rojo→verde ✓; recompute Python vs SQL sobre 5 segmentos reales <0,5% (logrado: 0,0%)
✓; run de prueba `published=FALSE` ✓. Nada de esto es una afirmación sin prueba —
cada número de esta nota es la salida real de un comando ejecutado en esta sesión.
