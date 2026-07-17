# F0 — Verdad de volumen (pilar 01-market-intelligence)

> Ejecutado 2026-07-17. Cierra el hueco #10 del RECON de `01-market-intelligence.md`.
> Método: SQL directo contra `cardeep-pg` (127.0.0.1:5433), script
> `scripts/f0_market_volume_truth.py` (persistido en el repo, no desechable — cualquiera
> puede re-ejecutarlo para refrescar estos números). Cada cifra crítica se cruza por
> ≥2 vías independientes, protocolo §7 de la carta.

## 1. Filas de `vehicle` por status

| status | n |
|---|---|
| available | 2.124.671 |
| gone | 546.156 |
| **TOTAL** | **2.670.827** |

## 2. Filas de `vehicle_event` por tipo

| event_type | n |
|---|---|
| NEW | 2.671.824 |
| GONE | 567.858 |
| PRICE_CHANGE | 323.587 |
| PHOTO_CHANGE | 155.949 |
| KM_CHANGE | 30.142 |
| **TOTAL** | **3.749.360** |

**Verificado por 2 vías independientes**: `GROUP BY event_type` directo (arriba) = 3.749.360,
contrastado contra `product_stats.events` (fila `country_code='ES'`, refrescada por
`scripts/refresh_product_stats.py`, `computed_at=2026-07-17 21:44:38 UTC`) = **3.749.360**.
Coinciden exactamente.

## 3. Span temporal real

- `vehicle_event.observed_at`: **2026-06-12 12:39:18 UTC → 2026-07-17 16:22:06 UTC**
- `vehicle.first_seen`: 2026-06-12 12:39:18 UTC → 2026-07-17 16:20:34 UTC
- **span_days = 35**

### GATE DE DISEÑO (aplicado, no diferido)

El span real es **35 días**, por debajo del umbral de 90 días que la carta fija como
frontera. Consecuencia vinculante para F2:

- **M3** (mediana días-hasta-retirada, ventana móvil nominal 90d) arranca con **ventana =
  span completo disponible (35 días)**, declarada en UI como tal — no se aparenta una
  ventana de 90 días que no existe.
- **M4** (Market Days Supply, ventana estándar vAuto 45d) arranca con la MISMA limitación:
  con 35 días de historial NO hay 45 días de GONE observables. La ventana efectiva de M4
  se declara como **min(45, span_disponible) = 35 días**, con el `n` de GONE en esa ventana
  visible en la UI, y la etiqueta advierte "ventana reducida por antigüedad del censo".
- **M7** (momentum 30d actual vs 30d anterior) requiere 60 días no solapados para su forma
  canónica; con 35 días disponibles esa forma es IMPOSIBLE hoy. F2 implementa M7 con
  ventanas reducidas **declaradas explícitamente** (partición del span disponible en dos
  mitades, ~17-18 días cada una) en vez de fingir 30/30 — o, si el `n` resultante es
  insuficiente por partición, M7 se marca "no disponible aún (requiere ≥60 días de
  historial; hoy: 35)" en vez de inventar un número. La decisión concreta (partir vs
  suprimir) se toma en F2 con el `n` real de cada mitad, no aquí.

## 4. % de `price IS NULL`

| fuente | total | price NULL | % |
|---|---|---|---|
| `servable_vehicle` (view de producción: available + precio saneado + no quarantined) | 2.124.135 | 27.933 | 1,32% |
| `vehicle WHERE status='available'` (raw, 2ª vía independiente) | 2.124.671 | 27.933 | 1,31% |

Diferencia de 536 filas entre las dos vías = exactamente las filas que `servable_vehicle`
excluye por quarantine de `price_trap` o techo de €5M (0047) — coherente con su definición,
no una discrepancia sin explicar.

## 5. % con `make`+`model`+`year` completos (servable_vehicle)

- total = 2.124.135
- completos = 1.717.274
- **80,85%**

## 6. Runs `vam_verified` en `vehicle_cluster_run`

- `vam_verified=TRUE`: **1 run**
- `v_canonical_vehicle` (resolución servida = el run vam_verified más reciente): **2.262.673 filas**

### GATE DE DISEÑO (aplicado)

Existe **1 run `vam_verified=TRUE`** → M1-M10 arrancan sobre `v_canonical_vehicle` (dedup
YA verificado por el Director), **NO** sobre el fallback `photo_hash`+firma "sin verificar"
que la carta reserva para el caso `0 runs`. Decisión tomada con el dato, conforme al
protocolo de la carta §9-F0.

## 7. Cardinalidad de segmentos con `n≥8` (cohorte M1: make+model+year+fuel+province_code)

Sobre `servable_vehicle` JOIN `entity` (price/make/model/year/province_code todos NOT NULL):

- cohortes totales: **441.728**
- cohortes con `n≥8`: **41.804** (9,46% de las cohortes)
- vehículos cubiertos por cohortes `n≥8`: **892.777** (51,98% de los 1.717.274 con
  make+model+year completo)

Confirma que la regla dura `n<8 → "muestra insuficiente"` de M1 SÍ dispara con frecuencia
real (9 de cada 10 cohortes exactas son demasiado finas) — el segmento de M1 en F1 debe
degradar con gracia (mostrar el dato nacional cuando el provincial no alcanza n≥8, tal
como especifica §6 de la carta), no fallar.

## 8. Contraste independiente: ledger de migraciones

- última migración aplicada: **0072** (`0072_vehicle_cluster_country_proof.sql`)
- próxima migración de este pilar: **0073** (re-verificar con `ls migrations/ | sort |
  tail -1` en el momento exacto de crearla — puede haber cambiado por otro frente).

## 9. `available_inventory` global — 2ª vía de contraste

Dos definiciones coexisten en el código, ambas verificadas, NO son la misma cifra
(documentado para que F1 elija la correcta sin confundirlas):

| definición | fuente | valor |
|---|---|---|
| Canónico-estricto (solo filas donde `vehicle_ulid = canonical_vehicle_ulid` dentro de `v_canonical_vehicle`) | `services/api/stats.py::_QUERIES['vehicles_unique_available']`, cacheada en `product_stats` | **1.523.328** — verificado 2 vías: recompute en vivo == valor cacheado en `product_stats` (`computed_at=2026-07-17 21:44:38 UTC`), coinciden exactamente. |
| Global con fallback COALESCE (vehículos fuera de cualquier cluster run cuentan como su propio canónico — patrón `entities.py:74`) | recompute directo (script F0) | **1.981.642** |

La diferencia (458.314) son vehículos `available` que NO han pasado aún por el resolver de
`vehicle_cluster` (fuera del run `vam_verified`) — cuentan en la vía COALESCE pero no en la
estricta. **F1 debe declarar explícitamente cuál usa** para el `n_in` de cada `market_stat_run`
(recomendación: la estricta `v_canonical_vehicle` JOIN, coherente con "runs verificados" del
punto 6 — así el `n` de M1-M10 nunca cuenta un coche dos veces por accidente de resolver
incompleto).

## Contexto adicional (product_stats, no pedido explícitamente por F0 pero relevante para M8/reconciliación GANVAM futura)

- dealers (puntos de venta reales, no particulares/desguace, con stock): 19.509
- provincias: 52
- municipios: 8.132

---

**Cierre F0**: todos los números de esta sección están verificados por SQL directo contra
la DB viva (2026-07-17), con contraste de 2ª vía donde existía un camino independiente
(product_stats cacheado, filtro raw alternativo). Ningún número es estimado o heredado de
documentación previa. Script fuente: `scripts/f0_market_volume_truth.py` (re-ejecutable).
