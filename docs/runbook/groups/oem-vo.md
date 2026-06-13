# GRUPO · OEM-VO (`kind='oem_vo_portal'`)

> La TERCERA especie: un **fabricante-dueño publicando el stock certificado de ocasión de su PROPIA
> red de concesionarios oficiales**. No es marketplace, no es clasificados generalistas, no hay
> particulares. Exactamente **14** entidades-portal. Detalle por portal en `platforms/<slug>.md`.

## Cómo se separa — la regla de propiedad

- **Los coches son de los concesionarios, no del portal.** Cada `vehicle.entity_ulid` apunta a su
  concesionario oficial vendedor (`kind='compraventa'`). El PORTAL tiene **0 coches directos**.
- **El coche EN el portal es una arista** `platform_listing`. Membresía plural: el mismo coche puede
  llevar una arista OEM-VO y una de coches.net sin cambiar de dueño.
- **Aislar los portales:** `entity.kind='oem_vo_portal'` → 14 filas (filtrar por `source_group`
  devuelve también los miles de dealers poseídos).

## Disjunción `[VERIFICADO]`

- **Coches:** Σ de los 14 conteos = **32.360** == `COUNT(DISTINCT vehicle_ulid)` sobre las 14
  aristas = **32.360**. Cero coches compartidos (cada marca publica solo su marca).
- **Dealers:** `COUNT(DISTINCT)` sobre las 14 aristas = **5.755** concesionarios distintos (la suma
  por-portal es 5.758 → solape mínimo de 3 dealers bajo >1 programa).

## Miembros validados (14)

`cars` = `COUNT(*) platform_listing` == `COUNT(DISTINCT vehicle)` (idénticos). Cada `verdict id` es
la fila `platform_slice` TRUSTWORTHY más reciente, `primary_value == cars`.

| Portal | cdp_code | Cars | Dealers | defense_tier | is_tier1 | family | verdict id | Ficha |
|---|---|--:|--:|---|:--:|---|--:|---|
| **spoticar** | CDP-ES-00-D6X2282Y | 6.138 | 136 | t1_soft | TRUE | stellantis_vo | **573** | [spoticar](../platforms/spoticar.md) |
| **mercedes_benz** | CDP-ES-00-A57R0YK8 | 4.792 | 4.749 | t0_open | FALSE | mercedes_benz_vo | **515** | [mercedes-benz](../platforms/mercedes-benz.md) |
| **toyota_lexus** | CDP-ES-00-GNAJ5S16 | 3.834 | 129 | t0_open | FALSE | toyota_lexus_vo | **572** | [toyota-lexus](../platforms/toyota-lexus.md) |
| **audi** | CDP-ES-00-NP3AWN4X | 3.798 | 56 | t0_open | FALSE | audi_vo | **482** | [audi](../platforms/audi.md) |
| **bmw** | CDP-ES-00-ZXZD056M | 2.848 | 51 | t1_soft | TRUE | bmw_group_vo | **524** | [bmw](../platforms/bmw.md) |
| **hyundai** | CDP-ES-00-C2SVJWB5 | 1.994 | 63 | t1_soft | TRUE | hyundai_vo | **569** | [hyundai](../platforms/hyundai.md) |
| **volvo_jlr_suzuki** | CDP-ES-00-T0G18J3M | 1.801 | 98 | t1_soft | TRUE | volvo_jlr_suzuki_vo | **571** | [volvo-jlr-suzuki](../platforms/volvo-jlr-suzuki.md) |
| **nissan** | CDP-ES-00-TDWVVTAF | 1.622 | 41 | t0_open | FALSE | nissan_intelligent_choice | **566** | [nissan](../platforms/nissan.md) |
| **kia** | CDP-ES-00-YK54F18S | 1.519 | 63 | t1_soft | FALSE | kia_vo | **570** | [kia](../platforms/kia.md) |
| **seat_cupra** | CDP-ES-00-3N995HG6 | 1.323 | 87 | t1_soft | TRUE | seat_cupra_vo | **567** | [seat-cupra](../platforms/seat-cupra.md) |
| **renew** | CDP-ES-00-DT59NK3D | 918 | 115 | t0_open | FALSE | renault_group | **423** | [renew](../platforms/renew.md) |
| **mini** | CDP-ES-00-EV9ECTV7 | 678 | 83 | t1_soft | TRUE | bmw_group_vo | **527** | [mini](../platforms/mini.md) |
| **das_weltauto** | CDP-ES-00-XWX9RHG7 | 552 | 56 | t1_soft | FALSE | vw_group | **428** | [das-weltauto](../platforms/das-weltauto.md) |
| **ford** | CDP-ES-00-ZB6C77HC | 543 | 31 | t1_soft | TRUE | ford_vo | **488** | [ford](../platforms/ford.md) |
| **TOTAL** | — | **32.360** | **5.755** | — | — | — | **14/14 TRUSTWORTHY** | — |

## Convergencia VAM

Cada veredicto guarda 3 rutas en `independent_values`: `harvested_cageable` (verdad del harvest),
`db_edges` (escritura), `db_join_vehicles` (lectura). En los 14: `db_edges == db_join_vehicles ==
primary_value` **exacto**. La `divergence` solo aparece en `harvested_cageable` (snapshot de la API
ligeramente por detrás tras re-runs), toda dentro de tolerancia → TRUSTWORTHY (rango 0,0 a 0,0407
para spoticar).

## Receta común (una, no un fork)

Los 14 conectores espejan `spoticar_wholesale.py` / `oem_toyota_lexus_wholesale.py`: mismo modelo de
doble membresía, misma jaula bulk, mismo cableado governor/health/VAM. Engine `curl_cffi
chrome131`. Governor: solo 3 hosts OEM-VO en JSON_API (`es.renew.auto`, `scs.audi.de`,
`kiaokasion.net`); el resto hereda STEALTH. GEO: `ZIP[:2]` → provincia INE (autoritativo), fallback
`lat/lon`. Encoding: la mayoría sirve mojibake latin-1 (`s.encode('latin-1').decode('utf-8')`);
excepciones UTF-8 limpio: `seat_cupra`, `mercedes_benz` (`utf-8-sig` BOM).

**Fuera del runbook (sin data-layer limpia):** Mazda (TLS timeout), Honda (sin JSON), Suzuki
(directorio per-dealer diferido). Ver [NOT-VALIDATED.md](../NOT-VALIDATED.md).
