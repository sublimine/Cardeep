# GRUPO · Rent-a-car VO (`source_group='rentacar_vo'`) — veredicto 542 TRUSTWORTHY

> Rent-a-car que liquida su ex-flota VO directo. `kind='rent_a_car_vo'`, `role='chain'`,
> `defense_tier=t1_soft`. La empresa es el punto de venta y dueña de cada coche (single-operator).
> Conector único `pipeline/platform/group_rentacar_vo_wholesale.py`.

## Veredicto

| id | subject_key | primary_value | divergencia | verdict | created_at |
|---:|---|---:|---:|---|---|
| **542** | `rentacar_vo` | **166** | 0.0 | **TRUSTWORTHY** | 2026-06-13 00:37:03Z |

Caminos: pathA `source_group=rentacar_vo` = 166 == pathB `entity.kind=rent_a_car_vo` = 166.

> **Desfase veredicto↔DB viva (declarado).** El `primary_value=166` refleja el estado a 00:37Z (solo
> OK Mobility). Centauro + Record Go se añadieron después; conteo vivo del grupo = **215**
> (169+28+18). Re-emisión VAM al valor vivo: pendiente (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).

## Miembros validados (3)

| Operador | cdp_code | edges vivos | Ficha |
|---|---|---:|---|
| **OK Mobility** (PRIMARY, base del 542) | CDP-ES-07-KWGRMQ7B | 169 | [ok-mobility](../platforms/ok-mobility.md) |
| **Centauro** | CDP-ES-03-BMPR08V3 | 28 | [centauro](../platforms/centauro.md) |
| **Record Go** | CDP-ES-12-H26EC1KD | 18 | [record-go](../platforms/record-go.md) |

DB viva (cross-check): 3 entidades; owned=edges=union=**215**, div 0.0. Precio retail 100 % no-NULL.
Todos `defense_tier=t1_soft`, governor STEALTH default. Cobertura del veredicto: Centauro + Record Go
están dentro del 542 por su pathA (`source_group=rentacar_vo`).

**Fuera del runbook:** Sixt ES (sin storefront VO español), Europcar/2nd Move y Goldcar (ex-flota
solo vía plataforma B2B con registro → duplicaría). Ver [NOT-VALIDATED.md](../NOT-VALIDATED.md).
