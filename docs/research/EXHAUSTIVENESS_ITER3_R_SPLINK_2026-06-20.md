# Exhaustiveness — Iteración 3: rpy2 cerrado + Splink + denominador bajo ≥2 modelos

**Fecha:** 2026-06-20 · **Estado:** VERIFICADO contra BD viva (127.0.0.1:5433) · **Commits:** `1f86139`, `a4c1acf`, `8bf5ca2`, `c7e64da`.

> Todo `[VERIFICADO]` salvo marca explícita. Cifras reproducibles con
> `python -m pipeline.exhaustiveness.cli run --unit splink --r-crosscheck`.

## 1. Hueco rpy2 — CERRADO (no pendiente)

Causa raíz (systematic-debugging): rpy2 fallaba en Windows por faltar **`make`**
(de Rtools), no porque R no fuera librería. Vías agotadas y resueltas:

- R 4.6.0 instalado **sin admin** (`C:\Users\elias\R-portable`) — paquetes `Rcapture`,
  `dga`, `LCMCR`, `jsonlite` instalados y cargando.
- **Rtools45 instalado con elevación** (`Start-Process -Verb RunAs`, UAC) → `make`
  disponible en `C:\rtools45\usr\bin`.
- `estimators_r._configure_r_env()` autoconfigura `R_HOME` + Rtools-make en PATH →
  **`rpy2_available() == True`**, R 4.6.0 in-process, `LCMCR` cargado.
- Validado: `lcmcr_rpy2` recupera N=1000 IC[945, 1073] sobre fixture conocido.

Dos canales R operativos: **rpy2 in-process** (rápido, para el rollup nacional) y
**Rscript-subprocess** (robusto, fallback). Ambos usan los paquetes reales.

## 2. Denominador NACIONAL bajo ≥2 modelos independientes (lo que pide §2.9)

Sobre la unidad Splink, 51 estratos certificados, n_obs_certificado = **1.935**:

| Modelo | N̂ nacional | IC 95% | Ancho IC | Cobertura cert. (cota inf.) |
|---|---:|---|---:|---:|
| Log-lineal Python (Fienberg) | 2.887 | [2.196, 3.579] | 1.383 | 54.1% |
| **LCMCR (latent-class Bayesiano, rpy2)** | **2.276** | **[2.044, 2.508]** | **464** | **77.1%** |

LCMCR corrió en **51/51** estratos. Es **−66% más estrecho** que el log-lineal y
sistemáticamente más bajo: el log-lineal **sobre-extrapola** en estratos
heterogéneos; LCMCR (robusto a heterogeneidad de captura) es el estimador más
defendible para una población de dealers muy heterogénea. La divergencia entre
modelos **es** la doble-verificación §2.3 en acción.

### Por estrato (ejemplos, Python → LCMCR)
| Estrato | K | n_obs | Python N̂ (IC) | LCMCR N̂ (IC) | Efecto |
|---|---|---:|---|---|---|
| 28/concesionario (Madrid) | 5 | 142 | 345 [150, 540] | **179 [157, 215]** | IC −78%, corrige over-extrapolación |
| 31/otros | 4 | 104 | 154 [104, 491] | **128 [108, 189]** | IC −79% |
| 09/otros (Burgos) | 5 | 321 | 411 [321, 595] | **378 [332, 508]** | concordante, más estrecho |
| 35/otros | 2 | 101 | 201 [101, 395] | **126 [103, 208]** | IC −64% |

## 3. Merge Splink (§V6) — solapamiento m por estrato

Linkage probabilístico (Fellegi-Sunter/DuckDB) por nombre(JaroWinkler, accent-folded)
+municipio+phone+web, **blocking difuso** (prefijo de nombre) + **union-find con el
dedup determinista** (unidad de captura nunca más fina que `v_dealer_resolved`).

- Solapamiento **≥2 listas: 898 → 1.074 (+20%)**; **≥3 listas: 55 → 79 (+44%)**.
- Pareado (47 estratos en ambos): **18 estrecharon su IC**; **Burgos 09/otros:
  ancho IC 477 → 274 (−43%), cobertura 41% → 54%**.
- Estratos identificados 48 → 51.

## 4. Split honesto certificado vs no-certificado (anti-maquillaje)

Los estratos sin solapamiento suficiente (denominador desconocido) **ya no se
pliegan al rollup** como 100% cubiertos. Nacional separa:
- **CERTIFICADO** (51 estratos, n_obs 1.935): cobertura cota inferior 54–77% según modelo.
- **NO-CERTIFICADO**: ~24.400 dealers en estratos de solapamiento insuficiente.

**Hallazgo honesto:** el cuello de botella es la delgadez de las listas ortogonales
(la mayoría de dealers aparece solo en marketplace no-ortogonal o en 1 sola lista).
Subir la cobertura certificada requiere **más listas ortogonales** — los vectores
**DORK (V3)** y **REG/BORME (V4)** ya están en la taxonomía (`lists.py`).

## 5. Seam de triangulación externa CNAE-451/DIRCE — cableado (§2.7)

`triangulation.py`: loader CSV (`province_code,segment,n_external`) → consumido por
`seal.compute(external_census=)`; auto-carga `countries/ES/census/dirce_cnae451.csv`.
`triangulate()` da ratio + verdicto (consistent / n_hat_high / n_hat_low / no_anchor).
**Sin cifras fabricadas**: si falta el CSV, `status='pending external census'` y el
pipeline corre igual. Listo para activarse al cargar el extracto fiscal.

## 6. Verificación independiente (SQL, camino distinto)
- Nacional certificado splink persistido en `exhaustiveness_estimate` (NULL,NULL):
  n_obs=1.935, N̂(loglineal)=2.887, IC[2.196, 3.579] — reconcilia con el rollup Python.
- Burgos 09/otros persistido: ancho IC 477→274, cobertura 0.410→0.540.
- 74.541 filas en `discovery_splink_cluster`. 14 estratos sellados ≥95%.

## Criterios §2.9
- [x] Matriz `discovery_capture` por ≥4 listas ortogonales (GEO/CENSUS/DGT/ASSOC/OEM; DORK/REG cableados).
- [x] `LCMCR` (y `Rcapture`) corren vía rpy2/Rscript y emiten N̂+IC por estrato.
- [x] Cross-source dedup (Splink) → m sube (+20%/+44%).
- [x] **Denominador nacional con IC bajo ≥2 modelos** (log-lineal Python + LCMCR).
- [x] Tablero por provincia×tipo (`v_exhaustiveness_seal` + `report.py`).
- [~] Triangulación externa: seam cableado; pendiente cargar el CSV DIRCE/DGT.
