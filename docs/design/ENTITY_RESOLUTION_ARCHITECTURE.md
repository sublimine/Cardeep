# CARDEEP — Re-arquitectura de descubrimiento · Resolución de entidad como columna vertebral

> **Estado:** especificación canónica (base del proyecto). Reemplaza el sello B6 monolítico y
> el modelo de particulares-como-entidad. Autoría de la tesis: el Owner (Elias). Auditoría de
> viabilidad y aterrizaje en código: el Director (esta sección + §A).

## Tesis
El descubrimiento NO es enumeración con mejor cobertura: son tres problemas disjuntos sobre tres
poblaciones de cardinalidad y descubribilidad distintas. "Completitud" solo es honesto donde la
población es finita (canales); en el resto se sustituye por *acotación con incertidumbre declarada*.
El instrumento que vertebra el estrato profesional no es scraping ni dedup de listados, sino la
**resolución de entidad (β)**.

## Causa raíz corregida (cada error con su dato medido)
| Síntoma medido | Error | Corrección |
|---|---|---|
| Chapman N̂≈789k | **Desajuste de población** (OSM físico × digital anuncios = disjuntos → captura-recaptura INAPLICABLE, no sesgada) | El estimador opera DENTRO de un estrato homogéneo, nunca entre estratos |
| 99,86% entidades de 1 sola fuente | **Privados modelados como entidad** dominan; singletons legítimos | Privados = listados, jamás entidades |
| 688 cierres cross-canal | Se midió **dedup de listados (α)** creyendo cuantificar profesionales (β) | β separada de α, clave e instrumentación propias |

## Estratos (regla de hierro: ningún estrato presta su método a otro)
| Estrato | Cardinalidad | Afirmación legítima | Método |
|---|---|---|---|
| **C — Canales** (portales/agregadores/redes con escaparate ocasión) | Decenas | «Todos» verificable | Enumeración exhaustiva + saturación |
| **P — Profesionales** (compraventa + concesionario + garaje-que-vende) | Miles | «X% con CI explícito» | Acotación (prior fiscal calibrado) + derivación (β) + Chao2 |
| **R — Privados** (C2C) | Cola no acotada | «Cobertura-vía-listados», nunca de entidades | Captura como listados sobre C |

## Dos pipelines (la separación es el desbloqueo)
- **α — Dedup de listados** (ya = B7 `vehicle_cluster`): ¿mismo vehículo físico en ≥2 canales? Clave VIN/fuzzy(atributos+fotos). Cuenta INVENTARIO. Los «688/245.680 merges» viven SOLO aquí.
- **β — Resolución de entidad** (este build): ¿mismo vendedor profesional? Clave: identificadores fuertes (tel/dominio/watermark/CIF) + **huella de inventario** (solape del conjunto de listados). Deriva el PROFESIONAL. Más robusto: no requiere α cerrado, solo solape ≥θ.

## §A — Auditoría de viabilidad [VERIFICADO DB 2026-06-14]
- Estratos separables HOY por `kind`. ✓
- Identificadores fuertes CASI VACÍOS en canales digitales (wallapop/coches_net/milanuncios tel=0/web=0; autocasión tel 42%, as24 web 42%, osm parcial). → **la huella es la clave DOMINANTE de β, no el identificador**.
- Huella disponible: **182.999 coches compartidos cross-entity** (vía B7). β construible YA.
- DIRCE en `data/official/` (dirce_301 provincia, dirce_294 ccaa). φ calibrable post-β.
- Tarea añadida (no en la spec original): **extraer tel/dominio de los canales que los exponen** (wallapop user.location/web_slug, milanuncios, fichas coches.net) → refuerzo de β.

## Maquinaria estadística (estrato P, DENTRO del estrato)
- **Chao2 / jackknife**, NO Lincoln-Petersen (P viola capturabilidad homogénea: el grande está en todos los canales, la compraventa en uno). `Ŝ = S_obs + Q₁²/(2·Q₂)`.
- **Dirección del sesgo:** canal×canal (mismo mecanismo) infla m₁₂ → DEPRIME N̂ → **da un SUELO, no un techo**. Independencia real = mecanismos ortogonales: fiscal (DIRCE) × comercial (canal) × geográfico (mapa, *acotado a P*).
- **DIRCE = prior calibrado:** φ (fracción-ocasión) se MIDE intersectando el censo con dealers que C ya vio vendiendo ocasión. `N_prof ≈ φ·N_fiscal`, φ con su CI.

## Cierre por estrato (doble candado en P)
- C: saturación (fuente nueva aporta <ε% canales) → «todos» verificable.
- P: coincidencia `observado_saturación ≈ N̂_Chao2` dentro del CI → EVIDENCIA de completitud (no prueba). Los dos números salen de mecanismos independientes; su coincidencia es el cierre, su discrepancia el diagnóstico.
- R: sin cierre de entidad. Cobertura-vía-listados.

## Plan de ejecución (orden = dependencia de build)
- **F0** — Congelar C (enumeración + saturación) · re-modelar 329k particulares → listados con dedup-α interno (salen del modelo de población).
- **F1** — Levantar β (columna vertebral): resolución de entidad sobre huella(B7)+identificadores, separada de α. Blocking O(n²) (P son miles) + adjudicación con modelo caro (R1). Entregable: S_obs dealers derivados. ← EN CURSO.
- **F2** — Calibrar prior fiscal: DIRCE ∩ dealers F1 → φ, N_prof.
- **F3** — Chao2 sobre mecanismos ortogonales + cierre contra saturación. Reportar gap + CI.
- **Continuo** — α (inventario) en paralelo, sin bloquear F1-F3.

## Definición formal de victoria
1. Enumeré TODOS los canales (C), verificado por saturación.
2. Acoté P dentro de X% con CI explícito (Chao2 ortogonal + DIRCE calibrado + saturación coincidente).
3. β deriva los dealers como subproducto de la cobertura de listados — no los rastreo.
4. Privados cubiertos vía listados, sin afirmar jamás cobertura de entidades.
Quien afirme enumeración exacta de dealers, o redefine la población hacia el registro fiscal (proxy), o miente. La honestidad de CARDEEP = declarar la incertidumbre de P y la finitud de C como afirmaciones de naturaleza distinta, sin confundirlas.
