# 04 · VERIFICACIÓN TERRITORIAL — censo vs cobertura (fase F8)

> El frente que responde, con denominador autoritativo y **no** con estimación, a la
> pregunta del SELLO 100%: *¿qué % del universo real de puntos de venta de España tenemos,
> y dónde está el hueco con nombre?* Censo-anclado contra INE DIRCE (registro legal) y
> contra Overture Maps Places (POI ortogonal, licencia abierta). **Regla dura heredada:**
> ningún número se canta por encima de la confianza de su fuente; cada celda lleva su tag
> `[VERIFIED]` / `[MODELED]` / `[DIRECTIONAL]`. *Mejor confesar el hueco que vender una mentira.*

Artefactos de evidencia (en [`../research/territorial/`](../research/territorial/)):
`TERRITORIAL_COVERAGE.md` (informe + escalera de confianza), `GAP_MAP.md` (gap ranqueado +
inflación C2C), `coverage_ccaa.json`, `coverage_province.json`, `ine_cnae4511_by_province.json`,
`ine_tabla301_raw.json` (pull INE crudo), y el aterrizaje POI: `poi_coverage_by_province.json`,
`poi_dealers_es.json`, `poi_new_candidates.json`, `_poi_overture_raw.json`.

---

## 1 · Titular honesto (cobertura nacional)

| Marco | Nuestro | Denominador INE | Cobertura | Tag |
|---|--:|--:|--:|:--|
| **Ventas — registral-ortogonal** (el titular honesto) | **21.759** | **23.085** locales CNAE 451 | **94,3 %** | `[VERIFIED]` |
| Ventas — bruto (todas las fuentes) | 33.611 | 23.085 locales 451 | 145,6 % | `[VERIFIED count, ratio inflado por C2C]` |
| Ventas — vs registro de empresas | 33.690 negocios | 14.367 empresas 451 | 234,5 % | `[VERIFIED, ancla-suelo]` |
| **Desguace — censo exacto** | **1.299** | **1.292** CAT autorizados (DGT) | **100,5 %** | `[VERIFIED exacto — SELLADO]` |
| Garaje (subconjunto `sells_cars`) | — | CNAE 452 = 50.294 (techo de taller) | **incomputable** | `sells_cars` sin poblar (confesado) |

**La cobertura nacional VERIFICADA del segmento VENTAS es 94,3 %** (21.759 de 23.085 locales
INE CNAE 451), contando solo atribución registral/geo/OEM/directorio y excluyendo el
primer-descubrimiento en marketplaces C2C. Los otros ratios son números reales que **NO** son
victorias de cobertura:

- El **bruto 145,6 % NO es 145 % de cobertura**: es **contaminación C2C** `[VERIFIED — SQL]`.
  11.852 de 33.710 entidades-venta (35,2 %) se descubrieron primero en milanuncios/wallapop
  (plataformas C2C que la doctrina de cobertura atribuye al centinela-plataforma, no enumera
  como dealers). Quitarlas → registral 21.759 → 94,3 %.
- El **234,5 % vs el registro de empresas es chequeo-suelo, no techo**: DIRCE cuenta solo
  empresas con actividad **principal** 451; infra-cuenta autónomos, actividad secundaria e
  informales. >100 % = **saturación del registro formal**, no un hueco.
- **Desguace SELLADO a 100,5 %** contra el censo legal DGT-CAT (1.292 CAT autorizados) —
  denominador *exacto*, no estimación.

---

## 2 · Escalera de confianza (leer antes de fiarse de una celda)

| Capa | Ancla | Confianza | Por qué |
|---|---|:--:|---|
| **Nacional ventas 94,3 %** | INE locales 451 = 23.085 (exacto) vs 21.759 registral (SQL) | **VERIFIED** | Ambos extremos leídos en vivo; dos caminos INE independientes (div-45×share y `ine_cnae4511_by_province.json`) aterrizan en 23.085 exacto. |
| **CCAA × locales 451** | INE publica locales-451 exacto por CCAA; Σ19 = 23.085 | **VERIFIED — ALTA** | La capa **portante**. Integridad chequeada (Σ19 == nacional). |
| **Provincia × 451** | INE **no** publica provincia × 451 (confidencial). Provincia = locales div-45 exactos (tabla 301) **asignados** a 451 por el share nacional 0,2605 | **MODELED — MEDIA** | La asignación supone mezcla-de-ventas uniforme — input de modelo declarado. Los *ranks* son fiables; el % exacto lleva incertidumbre de asignación. |
| **Desguace × DGT-CAT** | DGT-CAT censo legal = 1.292 (exacto) vs 1.299 | **VERIFIED — EXACTO** | Censo legal, no estimación. Sellado. |
| **Municipio × 451** | No existe denominador INE por debajo de CCAA (secreto estadístico) | **DIRECTIONAL — BAJA** | Antes solo POI-acotable vía OSM, que es **circular** (OSM es una de nuestras fuentes). **Resuelto parcialmente en §3 con Overture (ortogonal).** |
| **Garaje** | `sells_cars` sin poblar → denominador indefinido | **INCOMPUTABLE** | Confesado, no fingido. |

Gaps CCAA genuinos `[VERIFIED]`: **Ceuta 19,2 %, Melilla 25,0 %, Canarias 59,4 %** (islas +
ciudades autónomas + 54 % de pérdida de geocoding en Canarias). Defecto municipal real = **el
hueco de geocoding**: 13.741 entidades (32,5 %) llevan provincia pero **no** `municipality_code`.

---

## 3 · Denominador POI Overture — ORTOGONAL (cierra el hueco #11)

`TERRITORIAL_COVERAGE.md §4.11` dejó **explícitamente confesado** que el denominador POI
Overture estaba `INCOMPLETE` y que su % **no se publicaba** hasta ingerir el extract. Esta
sección lo **aterriza**: sustituye el POI circular (OSM) por una fuente independiente de
nuestra intake (Overture Maps Places, `2026-05-20.0`, licencia CDLA-Permissive-2.0).

**Pipeline (DuckDB anónimo sobre S3 → GeoResolver INE → dedup 3-claves contra DB viva):**
extrae los POI ES de categorías `car_dealer / used_car_dealer / automotive_dealer / car_buyer /
commercial_vehicle_dealer / truck_dealer`, resuelve `lat/lon → provincia/municipio` por el
GeoResolver INE, y deduplica contra `entity (kind<>'particular', status='active')` por
`bare_host`, `norm_name|municipality_INE` y `norm_name|province_INE`.

| Métrica | Valor | Nota |
|---|--:|---|
| POI ES totales (Overture) | **19.727** | `[VERIFIED]` — `poi_coverage_by_province.json` |
| geo-resueltos (provincia) | 19.645 | 99,6 % |
| muni-resueltos | 18.715 | |
| **cruzados con DB** | **6.523** | host 3.696 + nombre\|muni 1.803 + nombre\|prov 1.024 |
| **candidatos nuevos** | **13.204** | POI sin match por estas claves |
| sin geo | 82 | |
| operativos marcados "closed" | **0** | |

> **CÓMO LEER el 13.204 — anti-alucinación (crítico).** **NO** son 13.204 dealers que falten.
> Nuestra DB tiene **33.690** negocios-dealer (ancla INE §1), **~1,7× el set ES completo de
> Overture (19.727)** — igual que ya superamos OSM ~10×. El 13.204 es el **techo de una
> superficie de leads**: incluye variantes de nombre que el dedup de 3 claves no captó,
> no-dealers mal categorizados por Overture, cerrados y duplicados. Es material de la fase
> DESCUBRIR (no de cobertura). El **6.523 cruzado** es la verdad positiva: confirma solape
> sustancial DB↔Overture por una vía ortogonal. Overture es **ancla-suelo / cross-check**, no
> un recuento de huecos.

**Estado del frente:** ✅ denominador POI aterrizado y reconciliado (cierra el `INCOMPLETE`
del §4.11). ⏳ **PENDIENTE (declarado):** validar el 13.204 (dedup de variantes + filtro
no-dealer + operating-status) antes de que **una sola** fila cuente como dealer real nuevo →
ver [NOT-VALIDATED.md](NOT-VALIDATED.md).

---

## 4 · Método reproducible (CLI)

```bash
# Denominador INE DIRCE (registro legal) — tabla 301/294, ref 2025-01-01 Definitivo
#   Tempus3 JSON API servicios.ine.es/wstempus/js/ES, op 43 / IOE 30203
#   → docs/research/territorial/ine_*.json + coverage_*.json
# Denominador POI Overture (ortogonal) — release 2026-05-20.0, CDLA-Permissive-2.0
#   DuckDB anónimo sobre S3 + GeoResolver INE + dedup 3-claves contra entity viva
#   → docs/research/territorial/poi_*.json
# Numerador (DB viva):
CARDEEP_DSN=postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep \
  psql -c "SELECT province_code, count(*) FROM entity \
           WHERE kind IN ('compraventa','concesionario_oficial') AND status='active' \
           GROUP BY 1;"
# Join numerador/denominador: CCAA (ALTA) · provincia (MEDIA) · municipio (Overture, ortogonal)
# Desguace: join directo al censo exacto DGT-CAT (1.292)
```

## 5 · Trampas / notas

- **Provincia × 451 es MODELED, no INE-directo.** INE no publica provincia × CNAE-451; se
  asigna por el share nacional 0,2605. Citar el rank, no el % al dígito.
- **Municipio sin denominador INE.** Confidencial bajo CCAA. Overture acota (ortogonal) pero
  no es censo: no se publica un % municipal Overture-anclado hasta validar el 13.204.
- **>100 % = sobre-recogido, NO "más que cubierto".** Acción ahí: anclaje CIF + dedup
  C2C/dealer, no más descubrimiento.
- **Sin verdict VAM-slice.** La verificación territorial es una **medición censo-anclada**
  (denominador externo vs conteo DB), no un `platform_slice`; por eso no lleva
  `verification_verdict` id propio (mismo criterio que las filas de DESCUBRIR en
  [VALIDATION-INDEX.md](VALIDATION-INDEX.md)). Su prueba es el par denominador-fuente +
  query DB nombrada, reproducible por el CLI de §4.
