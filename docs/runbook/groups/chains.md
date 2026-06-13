# GRUPO · Cadenas VO (`source_group='chain'`) — veredicto 541 TRUSTWORTHY

> Cadenas nacionales de VO con muchos puntos físicos. `kind='cadena'` (plataforma) /
> `kind='compraventa'` (sucursal); `role='chain'` / `standalone_pos`. Todas `t0_open` (sin WAF),
> `is_tier1=FALSE`. Conector único `pipeline/platform/group_vo_chains_wholesale.py`.

## Veredicto

| id | subject_key | primary_value | divergencia | verdict | created_at |
|---:|---|---:|---:|---|---|
| **541** | `chains` | **37.319** | 0.0 | **TRUSTWORTHY** | 2026-06-13 00:37:03Z |

Caminos: pathA `source_group=chain (join entity)` = 37.319 == pathB `entity_source source_key ~
'^group_vo_chains'` = 37.319; disjunto de oem_vo/rentacar_vo/subasta a nivel vehículo (0 owners
cruzados).

> **Desfase veredicto↔DB viva (declarado).** El veredicto se selló a 00:37Z (37.319). Drenes
> posteriores commiteados ampliaron a **39.201** vivos. El runbook reporta 37.319 como validación
> formal; el conteo vivo (39.201) es cross-check `[VERIFICADO]`. Re-emisión VAM al valor vivo:
> pendiente (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).

## Miembros validados (4)

| Cadena | cdp_code | edges vivos | atribución | Ficha |
|---|---|---:|---|---|
| **Flexicar** | CDP-ES-00-FYECEGD5 | 23.874 | per-branch (186 sucursales) | [flexicar](../platforms/flexicar.md) |
| **OcasionPlus** | CDP-ES-00-SWN09H0C | 13.445 | chain-as-owner | [ocasionplus](../platforms/ocasionplus.md) |
| **Clicars** | CDP-ES-00-QCMVM26T | 1.470 | chain-as-owner | [clicars](../platforms/clicars.md) |
| **Carplus** | CDP-ES-00-4YVMXZ3T | 412 | chain-as-owner | [carplus](../platforms/carplus.md) |

DB viva (cross-check): 189 entidades `chain`; owned=edges=union=**39.201**, divergencia 0.0. Precio
retail 100 % no-NULL. `source_key` en DB: `group_vo_chains_flexicar` (186 ent.), `_carplus` (1),
`_clicars` (1), `_ocasionplus` (1).

**Governor:** `services.flexicar.es` → JSON_API; `www.ocasionplus.com` → STEALTH override 1.0/3/0.8;
`www.clicars.com` / `www.carplus.es` → STEALTH default 0.7.

**Fuera del runbook:** Aurgi, GpsAutos, Crandon (citados como futuros `chain`, sin probe ni aristas).
