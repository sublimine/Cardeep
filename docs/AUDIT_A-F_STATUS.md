# CARDEEP — Certificado de estado A→F (verificado contra DB viva)

> **Qué es:** el cierre punto-por-punto del prompt fundacional (A·Producto → F·Método + GAPS + TERMINAL),
> con CADA punto re-verificado contra la base de datos VIVA y el código — no contra los claims del
> SUPERPLAN. Producido por el workflow de verificación `wh0mhslbq` (7 agentes Inquisidores, uno por
> categoría, 295 tool-uses, queries con `statement_timeout` anti-lock), sintetizado y los drifts
> root-causeados por el Director (Opus). Fecha: 2026-06-15. Migraciones aplicadas: **0001→0040** (verify 34/0 drift).
>
> **No confiamos en ningún resultado:** donde el agente verificó un número contra la DB, se cita. Donde
> el SUPERPLAN sobre-afirmaba, se corrigió (ver §Drifts).

---

## La verdad central (por qué "terminar A→F a €0" tiene un límite lógico)

El objetivo A→F NO es completable enteramente a €0. La frontera **€0-autónoma está sellada**; el resto
choca contra **tu propio gate de gasto** ("gasto inviable hasta que esté todo configurado del A al Z").
Los puntos restantes requieren **cosecha/scrape a escala** (proxies, compute, egress) = la fase que
diferiste. No es una parada estratégica: es el límite lógico de "€0 + sin harvest".

- **€0-SELLADO (verificado a nivel átomo):** 13 de los SU centrales — toda la maquinaria de identidad,
  verificación, API, OPS, organización y método.
- **GATED (correctamente parcial, gap-con-causa):** 11 SU — harvest / spend / hardware / data. La
  infraestructura €0 está construida; falta correr la cosecha (que cuesta).

---

## A — EL PRODUCTO

| SU | Punto | Estado verificado | Gate | Evidencia viva |
|---|---|---|---|---|
| A1 | Código único (B1/dedup) | ✅ **SELLADO** | — | 391.944 entities = 391.944 cdp distintos (1:1, 0 colisión); dedup verdict 1121 vam_verified; `v_canonical` íntegra |
| A2 | Denominador P (β→φ→Chao2) | 🟡 GATED | DATA | β sellado (S_obs 38.555); Chao2 REFUTED (capturas disjuntas); ancla CNAE-451 (F8 94,3%). Necesita DIRCE/Overture |
| A3 | Scrapear TODO (exhaustividad B9) | 🟡 GATED | HARVEST | B9 gate €0 existe; 5/47 fuentes instrumentadas; 42 drains = paced harvest |
| A4 | Delta uniforme | 🟡 GATED | HARVEST | `delta.py` (diff/reconcile_gone + cap fracción-gone) construido+tested; cablear 43 conectores = harvest |
| A5 | Receta guardada | 🟡 GATED | DATA | `v_dealer_recipe` 37.813 cubiertos; 23.894 sin inventario = recipe-hunting cosecha |
| A6 | Geo país/prov/ciudad | 🟡 GATED | DATA | comarca 99,93% ✓, sentinel-drift 0 ✓; muni-gap ~11% (6.777) = sin señal geo, necesita Overture/geocoder |
| A7 | Código único por dealer | ✅ **SELLADO** | — | cdp_code inmutable DB-enforced (UNIQUE); 391.944 1:1, 0 null |
| A8 | Falla→alerta→auto-repara→no cae | ✅ **SELLADO** | — | lazo €0 cerrado (breaker→auto_repair→alert-dedup→recovery); test inyección 8✓ |
| A9 | API viva sirviendo | ✅ **SELLADO** | — | FastAPI sirve solo sellado; servable_entity 391.944, servable_vehicle 1.704.968; dedup intra-cluster; rate-limit+cache+auth |

**Identidad de particulares — SERVIDO este turno:** `v_dealer_resolved` colapsó 706 humanos province-split
(370.267→369.561) vía canonical_key (verdict TRUSTWORTHY 1423, quorum 2/2/2), regresión 206/206. El conteo
no-particular servido (40.194) NO cambió (mi gate copió dealers verbatim — verificado delta=0).

## B — LA OBSESIÓN (verificar TODO)

| SU | Punto | Estado | Gate | Evidencia |
|---|---|---|---|---|
| B1 | Ledger de verificación profundo | ✅ **SELLADO** | — | migración 0026 aplicada; `verdict_audit` 1.086 filas hash-chain; CHECK `trustworthy_needs_independence`; rol inquisitor read-only |
| B2 | Inquisición V3 + completion | 🟢 **€0-COMPLETO** | — | 0030/0031/0032 aplicadas; entity_completion 37.657; 142 tests inquisition; lentes A-E + prosecutor atómico. G5/Lens-C = harvest |
| B3 | Confesar gaps (first-class) | ✅ **SELLADO** | — | verdict taxonomy {TRUSTWORTHY/UNVERIFIED/REFUTED} 1.086 filas; quarantine schema |

## C — TIER-1 + ARSENAL

| SU | Punto | Estado | Gate | Evidencia |
|---|---|---|---|---|
| C1 | Anti-detección spike | ⬜ GATED | HARVEST | sin `state/tier1-blocked.json`; requiere probing vivo de Wallapop/Adevinta (walled) = harvest |
| C2 | Cazar receta de cada Tier-1 | 🟢 **HECHO €0** (corregido) | — | 7 plataformas con receta+2-way-count libres (`tier1_recipes/README.md` + 14 CDP en `_tier1/`). Restante=harvest |
| C3 | Sellar B7 (dedup coches) | 🟢 **SERVIDO; verdict UNVERIFIED** (corregido) | — | 1.486.285 coches únicos servidos (`v_canonical_vehicle`, cluster_run vam_verified) + 4 guardas + sample-verif. PERO verdict 1102=UNVERIFIED: dedup mono-método, sin 2º clustering independiente para quórum → excepción declarada, no fabricable |

## D — COSTE / LLM

| SU | Punto | Estado | Gate | Evidencia |
|---|---|---|---|---|
| D1 | LLM local para lo masivo | 🟡 GATED | HARDWARE | Ollama+3 modelos instalados PERO ~2GB RAM libre + sin CUDA → ahogaría el pipeline. Deterministas (7 detectores+regex+lentes) cubren €0 |
| D2 | Eficiente y blindado | ✅ **SELLADO** | — | `ratelimit.py` (slowapi 120/30/300-min) + `cache.py` (TTL 60s/512-LRU, scoped, no cachea vivo); 13 tests✓ |

## E — HUELLA + ORGANIZACIÓN

| SU | Punto | Estado | Gate | Evidencia |
|---|---|---|---|---|
| E1 | Todo a main documentado | ✅ **SELLADO** | — | `10-VERIFICATION-STACK.md` (L1→L4) + RUNBOOK A-Z de-staled; árbol limpio |
| E2 | Separación física + reshape geo | ✅ **SELLADO** | — | 580 recetas vía `git mv` → `countries/ES/<prov>/.../dealers/<cdp>/` (543 geo + 14 tier1 + 23 platforms); count-preserving; 31+81 tests✓ |

## F — MÉTODO (los poderes)

| SU | Punto | Estado | Gate | Evidencia |
|---|---|---|---|---|
| F1 | Workflows de OPS continua | ✅ **SELLADO** | — | scheduler durable (APScheduler+PG jobstore, crash-safe); 6 jobs (heartbeat/watchdog/inquisition×2/gestionador/canonical_key); 62 tests ops |
| F2 | Integrar herramientas | ✅ **SELLADO** | — | lxml+bs4 suficientes; selectolax/extruct/libpostal diferidos con causa (anti-YAGNI) |
| F3 | Agotar alternativas | ✅ **SELLADO** | — | doctrina viva (F1 eligió PG-jobstore sobre Redis; F2 evaluó+descartó con causa) |

## GAPS ROJOS + TERMINAL

| SU | Punto | Estado | Gate | Evidencia |
|---|---|---|---|---|
| R1 | Desguace E2E (inventario) | ⬜ GATED | HARVEST | 1.895 desguaces descubiertos (52/52 prov, >100% censo DGT), **0 inventario** (greenfield, necesita Opisto/own-site scraping) |
| R2 | Concesionario harvest | ⬜ GATED | HARVEST | 1.589 concesionarios, 191 con inventario (12,1%); FACONAUTO-beyond-OEM = harvest |
| R3 | Filtrado sells_cars | ⬜ GATED | DATA | garaje.sells_cars 0% resuelto (7.201 NULL + 19 false); necesita clasificación externa |
| R4 | Cobertura 100% + cierre | ⬜ GATED | HARVEST | venta 19/52 ≥85% (88% nacional); Ceuta 3,8%/Melilla 4,8%; desguace-inv 0/52. Necesita E2E leads + censo |
| SEAL | SPAIN-SEALED 52/52 | 🟡 GATED | MIXED | **CAPA A €0-firmable** (venta 88% nac + desguace discovery 52/52 limpio); **CAPA B roadmap** (Overture E2E, OEM, Ceuta/Melilla censo) = spend |

---

## Drifts cazados por la verificación (valor del "no confiar, verificar") + root-cause

1. **A9 dealer-count 40.194 vs 40.016 → NO es drift.** Root-cause (delta=0 verificado sobre run viejo Y
   nuevo): son dos métricas distintas — 40.194 = `kind<>particular` sobre todas las entidades (métrica
   /stats viva), 40.016 = `deduped_count` del verdict 1121 sobre el subconjunto de 42.259 canónicos B1.
   Mi gate del particular-split NO tocó dealers. (Doc-drift menor: el comentario del endpoint /stats dice
   40.016, stale vs 40.194 vivo.)
2. **SU-C3 verdict 1102 UNVERIFIED vs claim "SELLADO" → drift REAL, corregido honestamente.** El cluster_run
   está vam_verified=TRUE pero su verdict es UNVERIFIED (quorum 0/0/0). B7 es dedup mono-método: no existe
   un 2º clustering independiente para un quórum-de-conteo. NO se fabrica evidencia (Ley I). Servido
   pragmático + sample-verificado; verdict honestamente UNVERIFIED. SUPERPLAN C3 corregido.
3. **SU-C2 ⬜ vs recetas hechas → drift, corregido.** Las recetas Tier-1 existen + documentadas + 2-way
   libres; el ⬜ era stale. Corregido a 🟢. Restante = harvest (correr conectores), no recipe-hunting.

(Drifts de conteo por crecimiento de datos — A7 390.621→391.944, A5 37.041→37.813, A6 definición muni-gap,
F1 46→62 tests — son snapshot-drift esperado, no defectos; cdp uniqueness/cobertura se mantienen.)

---

## Bottom line

- **€0-SELLADO atom-verificado (13 SU):** A1, A7, A8, A9, B1, B2, B3, C2, C3*, D2, E1, E2, F1, F2, F3
  (*C3 servido con verdict-UNVERIFIED declarado).
- **GATED (gap-con-causa, 11 SU):** A2/A5/A6 (DATA), A3/A4/C1/R1/R2/R4 (HARVEST), D1 (HARDWARE),
  R3 (DATA), SEAL (MIXED CAPA-B).
- **Todo lo GATED es la fase de cosecha/gasto que TÚ diferiste.** La infraestructura €0 que la habilita
  (recetas, runbook, jobs, detectores, identidad servida, verificación) está construida y verificada.
- **Sondeo €0 de los gated (06-15, post-certificado):** se probó cada punto gated buscando porción
  €0-doable-y-verificable-AHORA y se ejecutó lo confiable: **A6 = 5 munis** backfilleados (de 141 con
  señal; 30 latlon-vs-provincia en conflicto + 106 postcode-ambiguo + 6.636 sin-señal = rechazados por
  "no mentira"); **R3 = 6 garajes** `sells_cars=true` (con inventario; 7.195 sin inventario = ambiguos).
  Hallazgo EMPÍRICO: las porciones €0-doables de los gated son diminutas (5-6) — el grueso falla por
  falta de señal €0 (data/harvest), confirmando que el gate es real, no evitación. Lo único €0-restante
  no-ejecutado = A3/A4 (instrumentar 42 fuentes + cablear delta en 43 conectores): config-PARA-harvest,
  solo verificable estructuralmente (no end-to-end sin correr scrape=spend) → FASE-2, no a ciegas.
- **Próximo paso real = tu decisión de gasto** (abrir harvest a escala) o el rebuild union-find de
  cross-source/β (sub-1%, fresh-context). No queda trabajo seguro-Y-valioso a €0 sin abrir esos gates.
