# coches.com — coches-com
**Estado:** ✅ VALIDADO (verdict id=551, count=91.066, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace

## Identidad
- cdp_code: `CDP-ES-00-XM91J1NZ` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t1_soft` · family: `—` · data_surface: `next_data`

## Data-layer (la fuente real)
- Endpoint: `GET https://www.coches.com/coches-segunda-mano/coches-ocasion.htm` (page 1: makes + counts) → `GET https://www.coches.com/coches-segunda-mano/{make-slug}.htm?page={1..N}`
- Headers: `Accept: text/html,application/xhtml+xml,...`, `Referer: https://www.coches.com/coches-segunda-mano/`. Carossa / Grupo coches.com (Imperva/Incapsula).
- Tope/partición: paginación profunda capada en **page 500 (= resultado 10.000)**; page 501 → 403 Imperva. La SRP sin filtro alcanza solo 10k de 92k → FACET por make.
- Extracción: regex `<script id="__NEXT_DATA__" ...>(.*?)</script>` → JSON → `props.pageProps.classifieds.classifiedList` (20 cards/req) + `.total`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET page-1 sin filtro → `seoData[key=="all-makes"]` = 93 makes con counts exactos (Σ counts == classifieds.total == 92.326; ninguna make ≥10k; max PEUGEOT 8.345).
2. Por cada make M: `pages = ceil(count/20)`, GET `?page=1..pages`, emitir cada card.
3. Make-slug: ASCII-fold → lowercase → drop `&` y `.` → spaces a `-` → colapsar `-` repetidos (`LYNK & CO`→`lynk-co`). Asserta `classifieds.total == seoData count` antes de drenar.
4. Dedup en `id`. Segmentos: `vo` (default), `km0`, `vn/catalog`, `renting` (XHR aparte).

## Receta / config
- Conector: `pipeline/platform/coches_com_wholesale.py` (`_SRP_ROOT = https://www.coches.com/coches-segunda-mano`, L97; segmentos `vo/km0/vn/catalog/renting/all`)
- Governor: host `www.coches.com` → **STEALTH override 1.0 req/s, burst 3, min_spacing 0.8** (governor.py L323). Imperva-fronted, surface frágil.
- Parser/identidad: dedup `id` (la URL canónica era la causa-raíz de fantasmas) · Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- **verdict id=551 TRUSTWORTHY** · count=**91.066** aristas únicas · `db_edges=91.066 == db_distinct_refs=91.066 == db_join_vehicles=91.066` (div 0.0), `dup_veh=0`, `phantom_groups=0`, `cleaned=20.432`, `root_cause=canonical_deep_link surface-stable identity`.
- **Historial:** id 548 fue REFUTED (111.498 con 20.432 fantasmas cross-surface, clave-identidad = URL); el fix dedup → id 551 TRUSTWORTHY.
- Renting: `platform_segment` `XM91J1NZ:renting` **id 564 = 1.034** (TRUSTWORTHY; id 560 fue REFUTED 1.035). VN: `XM91J1NZ:vn` **id 492 = 826**.
- Live actual: 92.088 aristas (delta +1.022, ingesta post-verdict).

## CLI (reproducible)
```bash
python -m pipeline.platform.coches_com_wholesale --all                       # drena todas las makes (VO)
python -m pipeline.platform.coches_com_wholesale --segment vo --concurrency 8
python -m pipeline.platform.coches_com_wholesale --segment renting
python -m pipeline.platform.coches_com_wholesale --limit 500                  # tope de prueba
```

## Trampas / notas
- **Encoding load-bearing:** `r.content.decode("utf-8")` (NO `r.text` — curl_cffi mojibakea acentos).
- La clave de identidad URL provocó 20.432 fantasmas (id 548 REFUTED); fix = listing-id canónico.
