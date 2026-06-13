# family_unreachable — Tier-1 browser-only (body-gate ciego al status)
**Estado:** ✅ VALIDADO (verdict id=498, count=246, 2026-06-13)  ·  **Grupo:** Long-tail (familia unreachable)

## Identidad
- source_key: `family_unreachable` · kind del dealer: `compraventa` · source_group: `long_tail_web` · **defense_tier: `t1_browser`** · ownership: directa · members: 1 · producing: 1

## Data-layer (la fuente real)
La mitad más dura: dominios marcados dead/walled por el probe Tier-0 (DNS muerto, 403/202/503, timeout). La señal definitoria — y la única receta — es la escalada que `pipeline/engine/fetch.py` documenta: **Tier-1 = Chromium real juzgado por el BODY RENDERIZADO, no por el status HTTP**, porque un miembro sirve un listado completo bajo un status 403 honeypot. Ese **body-gate ciego al status** es el multiplicador.
- **Miembro recuperado (único, ya cageado):** **hrmotor.com** (HR Motor, Lleida 25 / Madrid 28). Home: HTTP 403 + 287 KB de HTML real. Listing `/coches-segunda-mano/`: HTTP 200, 772 KB, cards `vercoche` byte-uniformes, paginación `/page/N/`. El body-gate lo lee; el status-gate (y el probe original) lo tiraba.
- Engine: headless Chromium (Playwright sync en thread dedicado, UA Chrome coherente + locale ES), driven a través del seam `asyncio.to_thread` del governor.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Arrancar Chromium headless (locale ES).
2. GET listing, juzgar por body renderizado (NO por status).
3. Parser `parse_hrmotor`: card `<div class="vercoche …">`, `deep_link` via `data-href="…/coches-segunda-mano/…-<hash12+>/"`, `listing_ref` = hash final.
4. Paginación `/page/N/`.

## Receta / config
- Conector: `pipeline/platform/family_unreachable_wholesale.py` · `FAMILY_KEY='family_unreachable'` · STEALTH · **defense_tier t1_browser** · `DEFAULT_MAX_PAGES=6` (proof-slice; soporta drain completo)

## Validación (VAM)
- **verdict id=498 TRUSTWORTHY** · count=**246** own-site cars (verificado directo en DB: `family_unreachable` own-site no-edge = 246) · div 0.0 · healthy/closed.

## CLI (reproducible)
```bash
python -m pipeline.platform.family_unreachable_wholesale --dealers hrmotor.com
python -m pipeline.platform.family_unreachable_wholesale --all
```

## Trampas / notas
- **Re-test stealth de las 92 unreachable (camoufox 135, body-gate ciego al status):** 1 recovered-free (hrmotor.com), 39 NXDOMAIN, 50 hard wall, 2 resolves-sin-listing (avolo.net HTTP 500, renaultleioa.es 0 precios). **Genuinamente dead = 89.** El stealth CONFIRMA el veredicto original para 91 de 92; cero recuperaciones nuevas. La familia queda en **1 dealer / 246 cars**.
- Las 89 muertas/walled y los 2 resolves-sin-listing van a [NOT-VALIDATED.md](../NOT-VALIDATED.md).
