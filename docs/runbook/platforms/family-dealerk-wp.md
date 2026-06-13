# family_dealerk_wp — DealerK (MotorK) WordPress
**Estado:** ✅ VALIDADO (verdict id=606, count=2.270, 2026-06-13)  ·  **Grupo:** Long-tail (familia CMS)

## Identidad
- source_key: `family_dealerk_wp` · kind del dealer: `compraventa` · source_group: `long_tail_web` · defense_tier: `t0_open` · ownership: directa (sin arista `platform_listing`) · members: 37 · producing: 34

## Data-layer (la fuente real)
- Engine: `curl_cffi` GET, `impersonate=chrome131`, server-rendered HTML. Stack WordPress + Elementor + plugin "tucoche" (DealerK/MotorK), multisite. Markup `vcard-*` **byte-idéntico** entre miembros → UN parser los lee todos.
- **Fingerprint (membership):** HTML lleva `dealerk` (spine) **Y** al menos uno de `tucoche` o `cdn.dealerk.es/dealer/datafiles/vehicle`.
- **Listing paths (en orden):** `/coches/segunda-mano/`, `/seminuevos/`, `/coches/`.

## Micro-acciones (cómo se scrapea, paso a paso)
1. Resolver dealer en DB por host de `website`.
2. GET del primer listing-path que devuelva cards.
3. Paginar `?page=1..N` hasta página sin cards (o `--max-pages`).
4. Por card `<div class="vcard …">`: `deep_link` = anchor PDP `…/coches/segunda-mano/…/<id>/`; `listing_ref` = `<id>` numérico; make/model = `vcard-main-info__make-model`; price = `vcard-price__price`; year/km/fuel = `vcard-consumption__title`; photo = primera imagen `cdn.dealerk.*`.

## Receta / config
- Conector: `pipeline/platform/family_dealerk_wholesale.py` · `FAMILY_KEY='family_dealerk_wp'` · STEALTH · t0_open · kind `compraventa` · `FAMILY_RECIPE` v1

## Validación (VAM)
- **verdict id=606 TRUSTWORTHY** · count=**2.270** own-site cars · div 0.0 · healthy/closed. `paths={'db_family_vehicles': 2270, 'harvested_pairs': 2270, 'cars_ingested_distinct': 2270}`.

## CLI (reproducible)
```bash
python -m pipeline.platform.family_dealerk_wholesale --from-db --limit 5
python -m pipeline.platform.family_dealerk_wholesale --dealers archiauto.com autochristian.com
```

## Trampas / notas
- La familia más grande de las firmadas (37 members, 34 productores). Markup `vcard-*` byte-idéntico = el multiplicador. Misma familia que Record Go (rentacar).
