# Verificación de integridad de datos — 2026-06-20

> Continúa `DATA_INTEGRITY_AUDIT_2026-06-16.md`. Cada número está [VERIFICADO]
> contra la BD viva (Postgres 127.0.0.1:5433) y la API viva (:8090) en
> 2026-06-20, por vías independientes a la que lo produjo. Objetivo: separar el
> defecto real del artefacto, antes de gastar esfuerzo en fixes innecesarios.

## Resumen ejecutivo (cruda)

De los cuatro defectos reportados desde el portal, **dos no existen en el
backend/datos**, **uno es operativo (no de código)** y **uno no tiene
artefacto que envolver**. La capa de datos está bastante más sana que el marco
de "4 defectos graves" sugería. El verdadero cuello de botella es **operativo**:
la cosecha está **parada desde 2026-06-15** (5 días rancia) y el long-tail/AS24
sin cosechar.

| Defecto reportado | Veredicto verificado | Evidencia |
|---|---|---|
| 1. Identidad/dedup: entidad materializada varias veces, inventario duplicado | **NO es bug de backend.** Residual servido ~80–140 dups reales; el resto son CADENAS correctamente separadas en sucursales. | API colapsa alias (caso flexicarbcn 2→1, 4.470 coches unificados) |
| 2. Inventario topado en ~15 por dealer | **NO existe cap.** La API sirve 4.470 coches de un dealer, paginados completos. Scheduler ya cableado a full-drain. | `/entities/.../inventory` paginado = 4.470 filas |
| 3. Mayoría de dealers sin inventario | **REAL pero operativo.** 12.587 dealers activos sin inventario; solo 1.570 (12%) tienen web cosechable. Cosecha parada + AS24 sin cadencia. | `source_health.last_ok` máx = 2026-06-15 |
| 4. Censos sin ingestar (Overture/PA/CNAE) | **Sin artefacto.** No existen esos adapters en `pipeline/sources/`. Nada que "solo envolver". | `ls pipeline/sources/` |

---

## Defecto 1 — Identidad/dedup: el síntoma raw vs lo servido

**La alarma raw era un artefacto ya resuelto en la capa de serving.**

- Conteo RAW (tabla `entity`, ignorando resolución): 7.280 grupos `nombre
  normalizado + municipio` entre dealers reales → 17.028 filas "colapsables",
  546.318 vehículos en grupos con inventario. **Este número NO refleja lo que
  sirve la API.**
- Conteo SERVIDO (tras `v_dealer_resolved` = B1 ∘ canonical_dedup ∘ F1):
  - Residual por `nombre+municipio` que aún se parte en >1 dealer resuelto:
    **80 grupos, 80 colapsables.**
  - Residual por `website host` (ignorando municipio): 79 grupos, 538
    "colapsables" — **dominado por CADENAS** (ocasionplus.com=19 sucursales/15.569
    coches, flexicar.es=26, clicars.com=4). Son puntos de venta físicos
    distintos que comparten web corporativa; fusionarlos sería over-merge. La
    lista de exclusión de cadenas (`cross_source_dedup.py`) los mantiene
    separados **a propósito y correctamente**.
  - Residual por `phone` (9 dígitos): 107 grupos, 140 colapsables (incluye
    centralitas de cadena).
- **Causa de que el raw asuste y lo servido no:** F1 (inventory-fingerprint,
  `entity_resolution_run` vam_verified=TRUE) ya fusionó 59.506→38.555 dealers
  (20.951 merges) usando Jaccard de inventario, que captura los duplicados
  cross-source que el `nombre+municipio` exacto no ve (municipios geocodeados
  distintos). Ej.: flexicarbcn estaba en muni 08187 (as24) y otro fragmento en
  08019 — F1 los unió por inventario solapado.

**Prueba end-to-end contra API viva** (`/entities/CDP-ES-08-K1A7TPBF`):
- `available_inventory = 4470`, `n_aliases = 1` (dos cdp_codes → un canónico).
- Origen: autocasion_wholesale (3.447) + as24 (1.028) = 4.475 raw → 4.470 tras
  dedup intra-cluster. **Inventario unificado, no partido.**

Ficheros: `services/api/routers/entities.py:60-87` (resolve_cluster + count con
`LEFT JOIN v_canonical_vehicle` + `COALESCE`-to-self), `:127-146`
(/inventory sobre `member_ulids`); `services/api/routers/geo.py:182-194`
(`DISTINCT ON (resolved_cdp_code)`); `services/api/deps.py:73-122`
(resolve_cluster vía `v_dealer_resolved`).

> Nota anti-alucinación: una pasada de agente reportó un "INNER JOIN bug" que
> ocultaría 9.827 coches. **Falso/obsoleto** — el código vivo usa `LEFT JOIN +
> COALESCE` (entities.py:73-79, 130-138; fix GAP-6/E-inventory ya aplicado).
> Verificado leyendo la fuente.

## Defecto 2 — "Topado en ~15": no existe cap en backend

- API: `size` default 50, máx 200 (`entities.py:99-100`); sin cap por entidad.
- Distribución viva de inventario por entidad: sin pico en 15/16 (15→897,
  16→539, 20→1.071 dealers); reparto continuo. No hay corte global.
- Scheduler ya cableado a **full-drain** (no proof-slices): autocasion→módulo
  facet `--segment all --makes all`; coches_com `--all --segment all`;
  coches_net→facet; motor_es `--full --segment all`; wallapop→facet
  (`pipeline/ops/scheduler.py:146-159`). El huérfano `autocasion` y los
  proof-slices YA se repararon (Audit Phase 2).
- Prueba: un dealer sirve 4.470 coches paginados completos (arriba).

**Conclusión:** si el portal muestra ~15, es **frontend** (`web/`, otra sesión)
o **dato rancio**, no el backend.

> Nota anti-alucinación: la misma pasada reportó que el scheduler corría
> proof-slices (omitía `--all/--full`). **Obsoleto** — leyó los defaults de los
> módulos, no los args del REGISTRY del scheduler. Verificado en
> `scheduler.py:146-159`.

## Defecto 3 — El único real: cobertura de inventario (operativo)

- Dealers activos no-particular sin inventario: **12.587** (el "23.888" previo
  incluía `status='unverified'`). Por kind:

  | kind | sin_inv | con_web | sin_web |
  |---|---|---|---|
  | garaje | 7.195 | 796 | 6.399 |
  | compraventa | 2.722 | 447 | 2.275 |
  | concesionario_oficial | 1.340 | 290 | 1.050 |
  | desguace | 1.299 | 7 | 1.292 |
  | plataforma/oem_vo/importador | 31 | 30 | 1 |

- **Solo 1.570 (12%) tienen website** = superficie cosechable. Los otros
  **11.017 (88%) no tienen web** — son puntos censados (OSM/DGT/asociaciones)
  sin presencia online; no hay inventario que raspar (desguaces: 1.292/1.299
  sin web).
- **Causa raíz operativa, no de código:** la cosecha está **parada**. Dato más
  nuevo `vehicle.last_seen` = 2026-06-15 16:02 (hoy 2026-06-20, 5 días rancio).
  `as24_wholesale.last_ok = NULL` (solo `last_fail` 2026-06-08) → AS24 (~278k
  dealers) sin cosechar por cadencia. `coches_net_segments.last_ok = NULL`.
  Varias `family_*` con `consecutive_fails` 1–2.

**Gap accionable real:** ~1.570 long-tail con web (vía conectores `family_*` /
`harvest_dealer` por entidad) + refresco AS24/plataformas. El resto (~11k) es
inherente (sin web).

## Defecto 4 — Censos sin ingestar: sin artefacto

- `pipeline/sources/` contiene: dgt_cat, osm, associations (aedra/acevas/aecs),
  OEM (kia/mg/byd/skoda/dacia/hyundai/mercedes/seat). **No existe** adapter
  Overture, Páginas Amarillas ni CNAE. No hay censo "ya construido sin
  ingestar" que envolver; construirlos es trabajo net-new, no quirúrgico.
- Las asociaciones (AEDRA/ACEVAS/AECS) ya están cableadas como SourceAdapter
  (commit `909a7be`, ya pusheado).

---

## Acción ejecutada — colapso de residuales (2026-06-20)

`scripts/build_residual_namemuni_dedup.py` → run `residual-namemuni-v1`
(vam_verified=TRUE). Overlay no-destructivo sobre `canonical_dedup`, reversible.

- **Set seguro:** 80 grupos `nombre_norm+municipio` con >1 dealer resuelto →
  **73 colapsados**; excluidos 6 cadenas + 1 con direcciones distintas (posible
  sucursal). Cada grupo: mismo nombre, mismo municipio, misma/nula dirección,
  partido entre marketplaces (coches.net/milanuncios/autocasión/as24/OEM).
- **Asserts de seguridad (pasaron):** 0 merges base rotos, 0 cambios colaterales
  (solo 73 nodos cambian de representante), representantes base preservados.
- **Antes→después (API viva):** dealers servidos **29.900 → 29.827** (−73).
  Caso `automotordursan` (muni 28014): códigos `QV2NZ4CJ` (422) + `MH3ZCJ61`
  (2) → ahora ambos resuelven a `QV2NZ4CJ`, API `available_inventory=424`
  unificado, `n_aliases=1`. Cadenas intactas: flexicar.es 87 dealers, 
  ocasionplus.com 25 (sin colapsar).
- **Snapshot/rollback:** `canonical_dedup_backup_20260620` (tabla en BD). Revertir:
  `DELETE FROM canonical_dedup_run WHERE run_id='residual-namemuni-v1';` (CASCADE)
  → `v_dealer_resolved` vuelve a `particular-canonkey-v1`.

## Recomendación (la palanca real)

El backend/datos no necesita parches de los defectos 1, 2, 4. La palanca es
**operativa y debe ejecutarse supervisada** (riesgo de ban AS24 + capacidad de
PC → no se dispara a ciegas):

1. **Reanudar la cosecha** (`python -m pipeline.ops.scheduler`) para refrescar
   los 5 días rancios; los full-drains ya están cableados.
2. **AS24 + long-tail con web (1.570 dealers)**: harvest supervisado
   (`scripts/as24_harvest_batch.py`, conectores `family_*`), con `evict`/
   `capacity_ledger` gestionando capacidad del PC.
3. **No perseguir fantasmas** en el backend de dedup/cap: están sanos.

Antes/después de cada defecto, en una frase:
- D1: antes "17.028 dups raw" → verificado: ~80–140 dups reales servidos; resto
  cadenas correctas. Sin cambio de código necesario.
- D2: antes "topado ~15" → verificado: 4.470 servidos de un dealer; sin cap.
- D3: antes "23.888 sin cosechar" → verificado: 12.587 activos, 1.570
  cosechables; bloqueo = cosecha parada (operativo).
- D4: antes "envolver censos" → verificado: adapters inexistentes; sin
  artefacto.
