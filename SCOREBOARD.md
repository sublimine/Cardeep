# CARDEEP — MARCADOR VERIFICADO FINAL (cierre 2026-06-13)
> Cada número contado por el Director a mano con psycopg2 contra la DB viva (cardeep-pg :5433), VAM ≥2 caminos.
> DB en INGESTA VIVA: los absolutos suben entre snapshots. El bloque Tier-1 es de un snapshot único congelado.
> Parte de entrega honesto completo: `CIERRE_FINAL.md`. Sin git commit.

## Globales (snapshot único congelado)
| Métrica | Valor verificado |
|---|---|
| vehicle (total) | 1.030.185 |
| entity (puntos de venta + plataformas) | 207.934 |
| platform_listing (aristas) | 983.981 |
| vehicle_event (delta/historial) | 1.033.279 |
| available | 1.028.810 |
| provincias / municipios con entidades | 52/52 · 4.181 |
| plataformas | 22 |

> El total 1.030.185 NO es suma de grupos disjuntos: incluye 20.432 fantasmas de coches.com (REFUTED) y la
> capa long-tail no aditiva. La cifra deduplicada/sin-solape exige las correcciones de `CIERRE_FINAL.md §2`.

## Tier-1 marketplaces — VAM 3 caminos (snapshot congelado)
| Plataforma | aristas-distinct | distinct ref | Dealer | Particular | Veredicto |
|---|---|---|---|---|---|
| coches.net  | 272.903 | 272.884 | 155.086 | 117.817 | ✅ TRUSTWORTHY |
| milanuncios | 259.034 | 259.033 | 135.250 | 123.784 | ✅ TRUSTWORTHY |
| wallapop    | 224.596 | 224.577 | 157.255 |  67.341 | ✅ TRUSTWORTHY (faceto→651k en hueco) |
| coches.com  | 111.498 | **91.066** | 111.498 | 0 | ❌ REFUTED (18,3% cross-surface) |
| autocasion  | 16.225 | 16.225 | 16.225 | 0 | ✅ TRUSTWORTHY |
| motor.es    | 30.497 | 30.497 | 30.497 | 0 | ✅ TRUSTWORTHY |

Path A (aristas-distinct) == Path B (vehicle-ownership join) EXACTO en las 6 · 0 dup-explosion · 0 huérfanos.
**Tier-1 suma aristas: 914.753 · deduplicado: 894.282.** Veredictos: `verification_verdict` ids 545–550.
(Las filas 549/550 conservan el snapshot original autocasion=15.765 / motor.es=29.847; la DB drenó más desde entonces.)

## Grupos no-marketplace — VAM ≥2 caminos
| Grupo | Entidades | Vehículos | Veredicto |
|---|---|---|---|
| OEM-VO (14 portales) | 5.752 | 31.448 | ✅ TRUSTWORTHY (supera el viejo 22.222) |
| Cadenas (Flexicar/OcasionPlus) | 187 | 37.319 | ✅ TRUSTWORTHY (etiqueta impura: mezcla Arval/Ayvens leasing) |
| rentacar_vo (OK Mobility) | 1 | 166 | ✅ TRUSTWORTHY |
| subastas (Ayvens) | 2 | 27 | ✅ TRUSTWORTHY (gated; grueso tras login) |
| long_tail_families | 103 | 10.178 | ❌ REFUTED (no aditivo: 10.083 ya en otros grupos) |

**CORE-4 partición LIMPIA**: 0 solape entidad/vehículo · suma core-4 = 68.960. Veredictos: ids 540–544.
`platform.listing_counter` = NULL en las 22 (sin contador pre-calculado; todo derivado en vivo).

## OEM-VO detalle (14 portales, 31.448 coches, 5.752 entidades)
spoticar · audi · toyota_lexus · hyundai · volvo_jlr_suzuki · nissan_intelligent_choice · seat_cupra ·
kia · renew · das_weltauto · ford · bmw_premium_selection · mercedes_benz · mini_next.
(Los coches cuelgan de las entidades DEALER, no de las 14 filas plataforma que poseen 0 vehículos directos.)

## HUECOS declarados para el 100% absoluto (detalle en CIERRE_FINAL.md §2)
1. coches.com doble-conteo cross-surface 20.432 (REFUTED, fix dedup pendiente)
2. long_tail no aditivo-disjunto 10.083 (REFUTED, regla de partición pendiente)
3. wallapop faceto → 651k · 4. coches.net new/km0/renting Imperva ~10k (navegador)
5. coches.com renting XHR ~8.9k · 6. autocasion/motor.es segmentos VN/km0
7. kia geo-skip + OEM murados (Mazda/Honda/Suzuki sin data-layer) · 8. subastas con verja
9. long-tail `unreachable` (necesita Tier-2 residential proxy) · 10. bug print cp1252 (Σ) en conectores
11. organization VAM muerto (tabla vacía, org_id NULL) · 12. API: oem_vo_portal sin endpoint propio
13. auto_repair efectos con gasto scaffolded tras P10

## Regresiones corregidas
- ✅ trade_name vacío: 41 'particular' backfilled → POST=0 blank (verificado en vivo).
- ⚠️ coches.com / long_tail doble-conteo: detectados y flagged REFUTED en el ledger (fix pendiente).
- ✅ SCOREBOARD OEM-VO obsoleto (22.222 → 31.448 vivo) corregido aquí.

## "100%" honesto
- ✅ **100% del vector GRATUITO**: cerrado y verificado (5 Tier-1 limpias, core-4 partición limpia, API + S-HEALTH E2E).
- ❌ **100% ABSOLUTO de España**: requiere superar los huecos arriba (Tier-2 residential proxy / navegador
  anti-bot tras puerta de gasto P10). Declarado, no fingido.
