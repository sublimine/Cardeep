# Facilitea Coches — faciliteacoches

**Estado:** ✅ VALIDADO (verdict id=633, count=788, 2026-06-13)  ·  **Grupo:** Tier-1 marketplace / aggregator (miembro del conector conjunto faciliteacoches+RACC)

## Identidad
- cdp_code: `CDP-ES-00-9PXHGJBY` · kind: `plataforma` · source_group: `marketplace_motor` · defense_tier: `t0_open` · is_tier1: `FALSE` · family: `faciliteacoches` · data_surface: `next_data` (Next.js App Router / Vercel)

## Data-layer (la fuente real)
- Índice canónico: `GET https://faciliteacoches.com/peninsula-baleares/sitemap/coches-ficha.xml` (~21.989 URLs de PDP vivas 2026-06-13).
- Endpoint PDP: `GET https://www.faciliteacoches.com/es/es/ficha/{slug}-{id_mf}` → re-emite el MISMO objeto-coche RSC con `dealerData` + `shopData`.
- Auth/headers: curl_cffi `chrome131`, sin reto WAF (Vercel) → `t0_open`.
- Tope/partición: el SRP `/es/es/coches/ocasion/compra` resuelve por una promesa RSC server diferida (`?page=N` se ignora; pagina por server action no alcanzable por header). El drenaje canónico es PDP-by-PDP desde el sitemap.
- Esquema RSC: `dealerData` (grupo OEM/dealer — id_mf, name, slug, province, cp, city) + `shopData` (la tienda física donde está el coche — name/province/region/cp/city). El tail `id_mf` del slug PDP es el `listing_ref` estable.

## Micro-acciones (cómo se scrapea, paso a paso)
1. GET el sitemap `coches-ficha.xml`; extraer las URLs de PDP.
2. Por PDP: GET `/es/es/ficha/{slug}-{id_mf}`; parsear el objeto-coche RSC (dealerData + shopData + atributos).
3. Dedup por `id_mf` nativo.
4. Cagear per-SELLING-POINT: cada TIENDA física (shopData) es una entidad `compraventa` geo-resuelta; el coche → vehicle owned por su shop; arista platform_listing plataforma↔vehicle.

## Receta / config
- Conector: `pipeline/platform/faciliteacoches_racc_wholesale.py` (miembro `faciliteacoches`; `platform_cdp_code()`)
- Governor: host `www.faciliteacoches.com` → **STEALTH** (no en `_HOST_RATE_CLASSES`)
- Parser/identidad: dedup `id_mf` · Cage: plataforma-entidad + tienda-compraventa-geo + platform_listing + delta + recipe (modelo per-selling-point, como coches.net dealers / Flexicar)
- Naturaleza: AGREGADOR VO+renting de CaixaBank/ARVAL.

## Validación (VAM)
- **verdict id=633 TRUSTWORTHY** · count=**788** aristas · `db_edges=788 == db_join_vehicles=788 == db_distinct_refs=788` (div 0.0), confirmado en DB viva esta sesión.
- Live actual: 788 aristas (**delta 0 — cuadrado al coche**). El sitemap declara ~21.989 PDPs; los 788 son los drenados+cageados con verdict; el resto del índice queda como cola pendiente de drenaje (no validado).

## CLI (reproducible)
```bash
python -m pipeline.platform.faciliteacoches_racc_wholesale --pages 6
python -m pipeline.platform.faciliteacoches_racc_wholesale --members faciliteacoches --pages 8
```

## Trampas / notas
- El SRP NO es header-paginable (RSC server action); el drenaje obligatorio es PDP-by-PDP desde el sitemap.
- Cada coche lleva DOBLE atribución: `dealerData` (grupo) + `shopData` (tienda física). El owner es la tienda física (el punto de venta real).
- Conector conjunto con [RACC](racc.md): 788 (facilitea) + 96 (RACC) = 884 sobre los dos miembros; el índice de facilitea declara ~2.917/21.989 según la cola explorada.
