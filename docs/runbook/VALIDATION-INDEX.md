# VALIDATION-INDEX — el ledger vivo

> LA bitácora. Cada unidad validada → `verification_verdict` id + count + CLI + fecha. **Regla
> dura:** una fila existe aquí SOLO si su `verdict id` es TRUSTWORTHY y se confirmó en la DB
> (`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`) esta sesión. Las 55 ids citadas en
> todo el runbook se cruzaron una a una contra la tabla viva: **todas existen, todos los
> `primary_value` coinciden al dígito**. Lo REFUTED / no validado vive en
> [NOT-VALIDATED.md](NOT-VALIDATED.md).
>
> Verificado **2026-06-13**. Ledger total vivo: **587 veredictos (577 TRUSTWORTHY, 10 REFUTED)**.
> Esta tabla lista las unidades-conector + las verdades de motor; el ledger completo incluye además
> 371 `entity_inventory` por-entidad no enumerados aquí (uno por punto de venta).

---

## Tier-1 marketplaces (6 · `platform_slice`)

| Unidad | verdict id | count | CLI | fecha |
|---|---:|---:|---|---|
| coches.net | **545** | 272.903 | `python -m pipeline.platform.coches_net_wholesale` | 2026-06-13 |
| milanuncios | **554** | 259.706 | `python -m pipeline.platform.milanuncios_wholesale --pages 100` | 2026-06-13 |
| wallapop | **592** | 565.128 | `python -m pipeline.platform.wallapop_wholesale --target 651000` | 2026-06-13 |
| coches.com (VO) | **551** | 91.066 | `python -m pipeline.platform.coches_com_wholesale --all` | 2026-06-13 |
| autocasion | **549** | 15.765 | `python -m pipeline.platform.autocasion_facet --makes all` | 2026-06-13 |
| motor.es | **558** | 49.009 | `python -m pipeline.platform.motor_es_wholesale --full` | 2026-06-13 |

### Segmentos Tier-1 (`platform_segment_slice` / `platform_segment`)

| Unidad | verdict id | count | tipo | fecha |
|---|---:|---:|---|---|
| coches.net new | **584** | 6.151 | platform_segment_slice | 2026-06-13 |
| coches.net km0 | **585** | 3.107 | platform_segment_slice | 2026-06-13 |
| coches.net renting | **587** | 1.212 | platform_segment_slice | 2026-06-13 |
| coches.com renting | **564** | 1.034 | platform_segment | 2026-06-13 |
| coches.com vn | **492** | 826 | platform_segment | 2026-06-13 |

---

## OEM-VO (14 · `platform_slice`)

| Portal | cdp_code | verdict id | count | CLI | fecha |
|---|---|---:|---:|---|---|
| spoticar | CDP-ES-00-D6X2282Y | **573** | 6.138 | `python -m pipeline.platform.spoticar_wholesale --pages 528` | 2026-06-13 |
| mercedes_benz | CDP-ES-00-A57R0YK8 | **515** | 4.792 | `python -m pipeline.platform.oem_mercedes_benz_wholesale --pages 401` | 2026-06-13 |
| toyota_lexus | CDP-ES-00-GNAJ5S16 | **572** | 3.834 | `python -m pipeline.platform.oem_toyota_lexus_wholesale --pages 80` | 2026-06-13 |
| audi | CDP-ES-00-NP3AWN4X | **482** | 3.798 | `python -m pipeline.platform.oem_audi_wholesale --pages 40` | 2026-06-13 |
| bmw | CDP-ES-00-ZXZD056M | **524** | 2.848 | `python -m pipeline.platform.oem_bmw_mini_wholesale --brand bmw` | 2026-06-13 |
| hyundai | CDP-ES-00-C2SVJWB5 | **569** | 1.994 | `python -m pipeline.platform.oem_hyundai_wholesale` | 2026-06-13 |
| volvo_jlr_suzuki | CDP-ES-00-T0G18J3M | **571** | 1.801 | `python -m pipeline.platform.oem_volvo_jlr_suzuki_wholesale --pages 20` | 2026-06-13 |
| nissan | CDP-ES-00-TDWVVTAF | **566** | 1.622 | `python -m pipeline.platform.oem_nissan_mazda_honda_wholesale --pages 104` | 2026-06-13 |
| kia | CDP-ES-00-YK54F18S | **570** | 1.519 | `python -m pipeline.platform.oem_kia_wholesale` | 2026-06-13 |
| seat_cupra | CDP-ES-00-3N995HG6 | **567** | 1.323 | `python -m pipeline.platform.oem_seat_cupra_wholesale --pages 14` | 2026-06-13 |
| renew | CDP-ES-00-DT59NK3D | **423** | 918 | `python -m pipeline.platform.renew_wholesale --pages 8` | 2026-06-13 |
| mini | CDP-ES-00-EV9ECTV7 | **527** | 678 | `python -m pipeline.platform.oem_bmw_mini_wholesale --brand mini` | 2026-06-13 |
| das_weltauto | CDP-ES-00-XWX9RHG7 | **428** | 552 | `python -m pipeline.platform.dasweltauto_wholesale --provinces 3 --pages 8` | 2026-06-13 |
| ford | CDP-ES-00-ZB6C77HC | **488** | 543 | `python -m pipeline.platform.oem_ford_wholesale --pages 1` | 2026-06-13 |
| **TOTAL OEM-VO** | — | **14/14** | **32.360** | — | — |

---

## Otros grupos (3 · `group_vam`)

| Grupo | verdict id | count (sellado) | live (cross-check) | CLI | fecha |
|---|---:|---:|---:|---|---|
| chains | **541** | 37.319 | 39.201 | `python -m pipeline.platform.group_vo_chains_wholesale --members flexicar ocasionplus clicars carplus` | 2026-06-13 |
| rentacar_vo | **542** | 166 | 215 | `python -m pipeline.platform.group_rentacar_vo_wholesale --member all` | 2026-06-13 |
| subastas | **543** | 27 | 6.785 | `python -m pipeline.platform.group_subastas_wholesale` + `python scripts/cage_autorola_bca_subastas.py` | 2026-06-13 |

> Los miembros (Flexicar/OcasionPlus/Clicars/Carplus; OK Mobility/Centauro/Record Go;
> Ayvens/BCA/Autorola) están cubiertos por el verdict de grupo via pathA. El `count` es el sellado
> a 00:37Z (validación formal); el `live` es el cross-check vivo `[VERIFICADO]`. La re-emisión VAM
> al valor vivo está en [NOT-VALIDATED.md](NOT-VALIDATED.md).

---

## Long-tail (7 · `family_slice`)

| Familia | verdict id | count | members | producing | CLI | fecha |
|---|---:|---:|---:|---:|---|---|
| family_dealerk_wp | **606** | 2.270 | 37 | 34 | `python -m pipeline.platform.family_dealerk_wholesale --from-db` | 2026-06-13 |
| family_builder_wholesale | **598** | 1.224 | 9 | 2 | `python -m pipeline.platform.family_builder_wix_ueni_google_sites_basekit__wholesale --from-fingerprints` | 2026-06-13 |
| family_generic_custom | **597** | 1.029 | 10 | 10 | `python -m pipeline.platform.family_generic_custom_wholesale --all` | 2026-06-13 |
| family_dms_vendor_platforms | **596** | 799 | 27 | 22 | `python -m pipeline.platform.family_dms_vendor_platforms__wholesale --seeds` | 2026-06-13 |
| family_cms_wp | **535** | 518 | 13 | 13 | `python -m pipeline.platform.family_cms_wordpress_dominated__wholesale --from-db` | 2026-06-13 |
| family_framework_webbuilder | **525** | 358 | 7 | 4 | `python -m pipeline.platform.family_framework_next_astro_nuxt_angular__wholesale --from-db` | 2026-06-13 |
| family_unreachable | **498** | 246 | 1 | 1 | `python -m pipeline.platform.family_unreachable_wholesale --all` | 2026-06-13 |
| **TOTAL family-slice** | — | **6.444** | — | — | — | — |

---

## Verdades de motor (geo · VAM · API · dedup · global_count)

| Unidad | verdict id | subject_type | valor | fecha |
|---|---:|---|---|---|
| geo hierarchy (A==B comarca) | **581** | geo_hierarchy | 240.245 (Path A == Path B, 52/52 prov) | 2026-06-13 |
| API serves (todos los endpoints 200) | **583** | api_serves | all_endpoints_200 (`cardeep_api_8094`) | 2026-06-13 |
| vehicle_total | **577** | global_count | 1.332.980 (count* == Σ partición) | 2026-06-13 |
| entity_total | **578** | global_count | 309.148 | 2026-06-13 |
| platform_listing_total | **579** | global_count | 1.286.776 | 2026-06-13 |
| vehicle_event_total | **580** | global_count | 1.336.079 | 2026-06-13 |
| dedup watermark (partición 1:1) | **582** | dedup_watermark | 0 excess_edges | 2026-06-13 |
| cross-platform dedup (cota inferior) | **574** | cross_platform_dedup_watermark | 134.007 (SQL) ≈ 134.019 (Python) | 2026-06-13 |
| cross-platform dedup (previo) | **559** | cross_platform_dedup_watermark | 132.157 | 2026-06-13 |
| cross-platform dedup (previo) | **556** | cross_platform_dedup_watermark | 132.016 | 2026-06-13 |

> Los `global_count` listan el valor SELLADO en su barrido; el vivo es mayor por ingesta continua
> (la metodología 3-vías sigue exacta). Ver [01-ARCHITECTURE.md](01-ARCHITECTURE.md) §5/§8.

---

## Resumen del ledger

| Bloque | unidades-conector | verdict ids |
|---|---:|---|
| Tier-1 (slices + segmentos) | 6 + 5 | 545, 554, 592, 551, 549, 558, 584, 585, 587, 564, 492 |
| OEM-VO | 14 | 573, 515, 572, 482, 524, 569, 571, 566, 570, 567, 423, 527, 428, 488 |
| Otros grupos | 3 | 541, 542, 543 |
| Long-tail | 7 | 606, 598, 597, 596, 535, 525, 498 |
| Motor (geo/api/dedup/global) | 10 | 581, 583, 577, 578, 579, 580, 582, 574, 559, 556 |
| **TOTAL filas de este índice** | **45 unidades-conector + 10 de motor = 55 verdict ids** | — |

Las **55 ids** de este índice fueron confirmadas en la DB viva esta sesión (`SELECT … WHERE id =
ANY(...)`): 55 de 55 encontradas, cero faltantes, `primary_value` coincidente. El ledger completo
contiene 587 veredictos; los 371 `entity_inventory` por-entidad y los 10 REFUTED no se enumeran aquí
(los REFUTED están en [NOT-VALIDATED.md](NOT-VALIDATED.md)).
