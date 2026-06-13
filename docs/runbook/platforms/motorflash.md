# Motorflash — motorflash

**Estado:** ✅ VALIDADO (verdict id=619, count=187, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace / dealer-aggregator (DRENANDO — ver delta vivo)

> ⚠ **Slice en drenaje activo.** El verdict id=619 avala **187** aristas (sellado a 18:46Z). El conector
> sigue drenando en vivo (~1.000 dealers × ~50 coches ≈ 50k de techo); la DB viva marca **1.207+ aristas
> y subiendo** (`[VERIFICADO]` esta sesión, creciendo durante el muestreo). El número del runbook es el
> del verdict persistido (**187**); el vivo es cross-check `[VERIFICADO]`. La re-emisión VAM al valor
> de meseta queda **pendiente** hasta que el drenaje cierre (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md) §2).

## Identidad
- cdp_code: `CDP-ES-00-WN1DMGRN` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `aggregator` · data_surface: `json_ld`

## Data-layer (la fuente real)
- Índice de dealers: `robots.txt` declara `sitemap.concesionarios.xml` (~1.000 dealers, cada `/concesionario/{slug}/coches-segunda-mano/{id}/`).
- Endpoint dealer: cada página de dealer → H1 = nombre, 20 PDP links/página, paginado.
- Endpoint PDP: `GET /coche-segunda-mano/{make}-{model}-{slug}/ocasion/{id}-es/` → JSON-LD `Car` limpio (make/model/year/km/price/fuel/transmission/photo) + bloque `AutoDealer` (name + telephone). Sin wall (CloudFront, 200 a Chrome) → `t0_open`.
- Auth/headers: curl_cffi `chrome131` impersonate.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET `sitemap.concesionarios.xml`; extraer los ~1.000 dealers.
2. Por dealer: paginar su página de coches (20 PDP/página); recoger los deep-links PDP.
3. Por PDP: parsear el JSON-LD `Car` + `AutoDealer`. El tail `{id}-es` es el `listing_ref`.
4. Cagear per-dealer: cada DEALER es una entidad `compraventa` con **province NULL** (Motorflash oculta deliberadamente la dirección física del dealer); el coche → vehicle owned por su dealer; arista platform_listing plataforma↔vehicle. La provincia se rellena luego por cross-platform dedup contra la copia geo-anclada que AS24/coches.net ya minó.

## Receta / config
- Conector: `pipeline/platform/motorflash_wholesale.py` (`mf_platform_cdp_code()`, `dealer_cdp_code()`)
- Governor: host `www.motorflash.com` → **STEALTH** (no en `_HOST_RATE_CLASSES`)
- Parser/identidad: dedup `id` nativo del PDP · Cage: plataforma-entidad + dealer-compraventa (province NULL) + platform_listing + delta + recipe
- Naturaleza: el `00-TIER1-REGISTRY` lo marca como el mejor multiplicador de descubrimiento de dealers del universo marketplace ES (~38% de sus nombres de dealer ya existen geo-anclados en la DB).

## Validación (VAM)
- **verdict id=619 TRUSTWORTHY** · count=**187** aristas · `subject_type=platform_slice` · div 0.0 (paths `db_edges==db_join_vehicles==harvested_cageable`) · confirmado en DB viva esta sesión.
- Live actual: **1.207+ aristas, drenando** (`db_edges == db_join_vehicles == db_distinct_refs`, los tres iguales al instante de la lectura; el número crece). Delta vs verdict = **+1.020 y subiendo, sin re-VAM** → el delta NO está validado; solo 187 lo está.

## CLI (reproducible)
```bash
python -m pipeline.platform.motorflash_wholesale                 # drena todos los dealers
python -m pipeline.platform.motorflash_wholesale 50 10           # [max_dealers] [pages_per_dealer]
```

## Trampas / notas
- **Geo oculto (confesado):** Motorflash es lead-gen y oculta la dirección/ciudad del dealer en PDP y página de dealer; el dealer se cagea con province NULL y lo merge-a luego el cross-platform dedup por nombre. NUNCA se fabrica provincia.
- **Drenaje activo:** el slice no cumple aún la idempotencia "re-run = 0 nuevos" (sigue creciendo). El verdict avalado (187) es el sellado; el vivo es la frontera de re-VAM. Re-emitir el VAM cuando alcance meseta.
