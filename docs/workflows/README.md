# CARDEEP — Workflows átomo del E2E por dealer (F3)

> Diseño con precisión átomo de las 5 fases + verificación transversal del mandato.
> Cada fase declara: objetivo · entradas · pasos · gates · artefactos · fallo · idempotencia.
>
> **Mejora del método (autorizada por el mandato):** el pipeline de PRODUCCIÓN es
> código Python determinista (`pipeline/`), barato y escalable — no agentes por dealer.
> La herramienta `Workflow` (agentes) se reserva para lo que necesita inteligencia:
> **caza de receta en plataformas Tier-1** y **verificación adversarial**. Así el coste
> caro va solo a decidir; lo masivo (descubrir, parsear, ingerir) corre en local/€0.

## Arquitectura de capas
```
pipeline/
  sources/            # adaptadores de fuente (1 por fuente del censo F1)
    base.py           # contrato SourceAdapter -> Iterable[DiscoveredEntity]
    dgt_cat.py        # DGT CATV (desguaces) — IMPLEMENTADO
  discover.py         # FASE 1 DESCUBRIR  — IMPLEMENTADO
  scrape.py           # FASE 2 SCRAPEAR   — F3-cont
  recipe.py           # FASE 3 RECETA     — F3-cont
  ingest.py           # FASE 4 API        — IMPLEMENTADO (entidades); inventario F3-cont
  evict.py            # FASE 5 BORRAR     — F3-cont
  verify.py           # VERIFICAR (VAM)   — IMPLEMENTADO (count quorum)
  geo.py              # resolución nombre->código INE
```
> Los módulos no implementados NO existen aún como ficheros (anti-stub): se crean al
> implementarlos, fase a fase. Este doc es la arquitectura visible; el código es la verdad.

## FASE 1 — DESCUBRIR (`pipeline/discover.py`) · IMPLEMENTADO
- **Objetivo:** dada una fuente del censo, producir entidades reales (punto de venta)
  con geo INE + código único, e ingerirlas idempotentemente.
- **Entradas:** un `SourceAdapter` (p.ej. `dgt_cat`). 
- **Pasos:** fetch fuente → normalizar a `DiscoveredEntity` → resolver provincia/municipio
  a código INE (`geo.py`) → mintar `cdp_code` (dominio>CIF>nombre+muni>nombre+prov) →
  upsert `entity` + `entity_source` (provenance multi-fuente para dedup/capture-recapture).
- **Gate (VAM):** nº entidades ingeridas de la fuente == nº que la fuente declara
  (quórum ≥2 vías: conteo API + conteo página + conteo en DB). Tasa de geo-resolución
  reportada; las no resueltas se ingieren con municipio NULL (honesto), no se descartan.
- **Artefacto:** filas en `entity`/`entity_source` + veredicto en `verification_verdict`.
- **Fallo:** fuente caída → alerta origen-exacto + se sigue; nunca aborta el barrido global.
- **Idempotencia:** `ON CONFLICT (cdp_code)` → re-descubrir no duplica; refresca `last_seen`.

## FASE 2 — SCRAPEAR (`pipeline/scrape.py`) · F3-cont
- **Objetivo:** extraer el inventario COMPLETO de las URLs de una entidad.
- **Pasos:** cargar config dealer → drenar paginación hasta agotar → huella de cliente
  coherente p1→pN → respetar robots/rate → volcar crudo a `data/` (gitignored).
- **Gate:** páginas drenadas == esperadas; última página detectada explícita (no timeout).
- **Routing arsenal:** `is-antibot` fingerprintea → ABIERTA=curl_cffi · CF=camoufox/SeleniumBase
  · Akamai=BotBrowser+sensor (gate gasto). Banco de pruebas inicial: **AutoScout24.es** (abierto, JSON-LD dealer).

## FASE 3 — RECETA (`pipeline/recipe.py`) · F3-cont
- **Objetivo:** destilar la receta reutilizable (selectores/regex/endpoints/mapeo) y versionarla.
- **Pasos:** inferir estructura (regex/JSON-LD determinista > LLM) → mapear a campos canónicos
  (precio, año, km, VIN/ref, deep-link, foto) → verificar sobre muestra ciega → versionar.
- **Gate:** reproduce ≥ umbral de campos correctos, 0 campos críticos nulos.
- **Artefacto:** `countries/ES/.../recipe.yaml` versionada (el activo que re-scrapea sin crudo).

## FASE 4 — API/INGEST (`pipeline/ingest.py`) · IMPLEMENTADO (entidad) / inventario F3-cont
- **Objetivo:** ingerir inventario verificado con delta.
- **Pasos:** validar en borde (rechazar sin deep-link/campos clave) → delta: INSERT nuevo +
  cerrar desaparecido (status=gone+evento), UPDATE solo filas mutadas (Δprecio/Δfoto/Δkm) +
  evento → reconciliar conteo post-ingesta (VAM).
- **Gate:** conteo post-ingesta == lote por ≥2 vías; 0 filas inválidas; drift de esquema aborta.

## FASE 5 — BORRAR (`pipeline/evict.py`) · F3-cont ⚠ destructivo
- **Precondición DURA (3 gates):** ingesta TRUSTWORTHY (VAM≥2) + receta/config commiteadas +
  conteos cuadrados. Releídos en el momento del borrado.
- **Pasos:** watermark de disco → evicción LRU del crudo de dealers verificados → tombstone.json
  (prueba de vida, re-obtenible desde receta) → actualizar `state/capacity-ledger.json`.
- **Gate:** cualquier precondición roja → no se borra NADA.

## VERIFICAR (`pipeline/verify.py`) · IMPLEMENTADO (count quorum)
- Meta-fase transversal (§2 CLAUDE.md): toma un conteo/hallazgo, lo somete a N vías
  ortogonales (re-query, recuento crudo, hash lote, muestreo ciego), persiste
  `verification_verdict` con verdict TRUSTWORTHY/REFUTED/UNVERIFIED. Sin quórum → no avanza.
