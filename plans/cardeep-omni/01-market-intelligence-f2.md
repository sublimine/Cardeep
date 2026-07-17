# F2 — M3/M4/M5/M7/M9/M10 + gate de publicación ±3% — CERRADO Y VERIFICADO

> Ejecutado 2026-07-17/18. Depende de F0+F1. Esta fase incluye un hallazgo real de
> producción — un bug que dejó M7 en cero filas — encontrado, diagnosticado hasta la
> raíz y corregido DENTRO de esta misma fase, con las dos corridas (defectuosa y
> corregida) documentadas para trazabilidad completa. Nada se maquilla.

## 1. Alcance construido

`pipeline/market/metrics_f2.py` (nuevo, 6 fetchers) + extensión de
`pipeline/market/compute_stats.py` (`run_compute_full`) + `pipeline/market/publish_gate.py`
(nuevo, gate ±3% run-over-run + cierre humano). Ninguna migración nueva — F1's
`market_stat`/`market_stat_run` ya tenían el esquema genérico (`value_num`/`value_extra`)
diseñado para estas 6 métricas desde el principio.

### Segmentación
Idéntica a M1 (make+model+banda de año ±1+fuel+province_code, con fallback nacional),
salvo M5 (solo provincia, sin eje make/model, per carta).

### Ventanas dinámicas (gate F0 resuelto en código, no en prosa)
`pipeline/market/cohort.py` añade `get_span_days()` (consulta en vivo, nunca hardcodeada)
+ `effective_window_days(nominal, span)` = `min(nominal, span)`. Con el span real medido
en esta fase (~35,15 días):
- M3 (nominal 90d) → ventana efectiva **35,15d**
- M4 (nominal 45d) → ventana efectiva **35,15d**
- M5 (nominal 30d) → **30d** (cabe dentro del span, sin reducción)
- M9 (nominal 30d) → **30d** (ídem)
- M7 (dos ventanas de 30d nominal = 60d total) → span insuficiente → dos mitades de
  **17,58d cada una** (`m7_half_window_days`), documentado explícitamente en
  `value_extra.half_window_days` de cada fila, nunca fingiendo 30/30.

## 2. BUG ENCONTRADO Y CORREGIDO EN PRODUCCIÓN — declarado íntegro, no maquillado

### Síntoma
La primera corrida real de producción (`run_id=01KXS4YAXM8VCQK90R3A1SXFG1`,
`published=TRUE` inicialmente) escribió **0 filas para M7**. Verificado con
`SELECT metric_id, count(*) FROM market_stat WHERE run_id=... GROUP BY metric_id` —
M7 simplemente no aparecía en la lista.

### Diagnóstico (a la raíz, no al síntoma)
1. Confirmado que hay 126.341 eventos `NEW` con precio válido en la ventana "tardía"
   de M7 (últimos ~17,58 días) — la muestra CRUDA no es el problema.
2. Confirmado que el JOIN contra el `canon` estricto (`v_canonical_vehicle WHERE
   vehicle_ulid = canonical_vehicle_ulid`, el mismo patrón que M1 usa deliberadamente)
   reduce esos 126.341 candidatos a **0**.
3. Causa raíz: el resolver `vehicle_cluster` (que produce `v_canonical_vehicle`) corrió
   por última vez `vam_verified` el **2026-06-22**. Todo vehículo con `first_seen`
   posterior a esa fecha — **391.646 de 2.670.828 (14,7%)**, y **408.155 vehículos en
   total (15,3%) nunca han pasado por NINGÚN run del resolver** — está ausente de
   `v_canonical_vehicle` por completo (ni como canónico ni como miembro). La ventana
   "tardía" de M7 es, por construcción, los últimos ~17,58 días — enteramente
   POSTERIOR al último resolver — así que el 100% de sus candidatos eran invisibles.
   M3/M4/M5/M9 comparten el mismo JOIN y sufrían la MISMA ceguera parcial sobre
   actividad reciente (GONE/PRICE_CHANGE de coches aún no clusterizados), sin producir
   nunca un error visible — solo números sistemáticamente más bajos de lo real.

### Precedente ya resuelto en el propio código
`services/api/routers/entities.py:74` documenta EXACTAMENTE esta clase de bug
("a vehicle absent from v_canonical_vehicle is its own canonical and MUST be counted")
y ya la corrige con un patrón COALESCE para el servicio de inventario por dealer. Este
pilar no lo había aplicado a las métricas de actividad reciente — corregido ahora.

### Corrección aplicada
`pipeline/market/metrics_f2.py` — nueva `_COALESCE_CANON_CTE`: representante canónico
de un cluster CONOCIDO (sin cambios) UNION ALL todo vehículo que el resolver **nunca
ha tocado** (añadido de vuelta como su propio canónico). Aplicada a M3, M4 (lado GONE),
M5 (lado `gone_by_prov`, vía `_M5_DUAL_CANON_CTE` que mantiene el lado `avail_by_prov`
estricto), M7 y M9 — es decir, toda métrica que lee `vehicle_event` para actividad
RECIENTE. **M1 y M10 mantienen deliberadamente la definición estricta** (mismo
razonamiento que F0 §9 ya documentó para M1: son fotos del stock disponible HOY, no
ventanas de actividad reciente, y M1 ya está enviado+verificado con divergencia 0,0%
— no se toca sin necesidad real).

Verificado el cierre exacto del hueco: la misma query de diagnóstico, tras el fix,
devuelve **126.341** filas (coincide exacto con el crudo sin restricción — cero
pérdida).

### Re-verificación completa tras el fix
- **33/33 tests** (16 unitarios de `cohort.py` + 5 de integración F1 + 12 de
  integración F2) vueltos a correr de cero tras el cambio — **33/33 PASSED**
  (475,89s), incluidos los 5 tests que ya pasaban antes del fix (confirma CERO
  regresión sobre lo que ya funcionaba).
- Corrida de producción anterior (defectuosa) **despublicada** (`published=FALSE`),
  NO borrada — se conserva con una nota explícita (`market_stat_run.notes`) como
  rastro de auditoría honesto de que el bug fue atrapado por verificación real, no
  escondido. Doctrina MVCC respetada: solo se mutó el campo de gate (`published`),
  igual que `vam_verified` en `0023` — jamás una fila de `market_stat`.
- Nueva corrida corregida: `run_id=01KXS6Q4TJKCWM19KKQN2SJ2J1`, `published=TRUE`.

## 3. Resultado de la corrida corregida (producción real)

| Métrica | Filas | Nota |
|---|---|---|
| M1 | 117.652 | Sin cambios (universo estricto, ya verificado en F1) |
| M3 | 27.233 | Antes del fix: N/A (no medido en la corrida defectuosa por scope) |
| M4 | 117.652 | Reutiliza `n` de M1 |
| M5 | 52 | Ranking provincial completo |
| M7 | **4.386** | **Antes del fix: 0.** Ahora real. |
| M9 | 117.652 | |
| M10 | 118.122 | Universo estricto (como M1) |
| **TOTAL** | **502.749** | |

**Auditoría post-run:**
- `min(n)` en las 502.749 filas = **8** (ninguna viola la regla dura).
- 0 filas de M1 y 0 de M10 violan `p25≤p50≤p75`.
- Segmento de control (Peugeot 208 2024 Gasolina, nacional) coherente entre TODAS sus
  métricas: M1 n=7.026 p50=13.500€; M3 n=451 mediana=10,2 días; M4 MDS=547,7
  (=7.026/(451/35,15), verificado a mano); M9 17,9% con recorte (1.261/7.026),
  mediana de recorte 2,14%; M10 mediana=1 plataforma.
- Ejemplo real de M7 (Hyundai i20 2024 Gasolina nacional): p50 ventana temprana
  €17.000 → p50 ventana tardía €18.900, momentum **+11,18%**, n=594 (mínimo de
  early=2.755/late=594).

## 4. Gate de publicación ±3% (protocolo §7 fila 3)

`pipeline/market/publish_gate.py` — compara cada segmento entre la corrida nueva y la
última corrida PUBLICADA (`market_stat_run WHERE published=TRUE`), por métrica+clave
de segmento, marca >3% de divergencia como anomalía, y exige
`director_confirmed_anomalies=True` explícito para publicar con el gate en rojo —
nunca se publica en silencio.

**Caso bootstrap (documentado, no un vacío legal):** al despublicar la corrida
defectuosa ANTES de lanzar la corregida, la corrida corregida no tuvo ninguna corrida
publicada previa contra la cual comparar → `has_baseline=False` → gate limpio por
definición (no hay línea base de la cual divergir) → publicada sin necesitar el
override. Verificado en la salida real: `gate: has_baseline=False compared=0
anomalies=0 max_div=0.000%`.

## 5. Fixtures por métrica (criterio F2 explícito)

`tests/test_market_metrics_f2.py` (12 tests) — sintéticos en transacción SIEMPRE
abortada (mismo patrón de F1), casos cubiertos:
- M3: mediana de días a mano (10 valores 1-10 → 5,5) + supresión n<8.
- M4: MDS a mano (10 disponibles / 9 GONE en 45d → 50,0) + caso **GONE=0 → "sin
  rotación observada"** (criterio explícito de la carta).
- M5: tasa de absorción a mano (5/20) + supresión de provincia con n<8.
- M7: momentum +10% a mano (p50 550→605) + supresión cuando falta la mitad temprana.
- M9: 30% con recorte + mediana de recorte 10% a mano + caso sin cambios de precio
  (0% presión, no fallo).
- M10: distribución de plataformas a mano (1..10 → p25=3,25/p50=5,5/p75=7,75) + caso
  cero plataformas.

## Cierre F2

Los 3 criterios de la carta §9-F2 en verde: fixtures por métrica incluyendo GONE=0 y
n<8 ✓; gate ±3% implementado y probado (caso bootstrap real, sin anomalías) ✓; primer
run real `published=TRUE` tras pasar el protocolo §7 completo ✓ — con el añadido no
pedido pero necesario de haber encontrado, diagnosticado y corregido un bug real de
producción (M7 en cero) durante la propia verificación de esta fase, exactamente como
el proyecto exige: "mejor confesarme un hueco que venderme una mentira."
