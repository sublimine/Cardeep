# GRUPO · Tier-1 marketplaces

> Los gigantes C2C+PRO. `source_group ∈ {marketplace_motor, marketplace_generalist}`,
> `kind='plataforma'`, `defense_tier=t1_soft`. Cada plataforma es una fila `entity` con su
> `cdp_code` (sentinel provincia `00` = nacional) y receta propia. Aislamiento absoluto del resto
> de grupos. Detalle por conector en `platforms/<slug>.md`.

## Modelo

- **Platform-as-entity:** cada marketplace es un nodo servido, codeado, monitorizado y portador de
  receta — no un canal de config. La fila gemela `platform` lleva `data_surface`, `is_tier1`,
  `website_waf`.
- **Doble membresía:** `vehicle.entity_ulid` = dealer vendedor; el coche EN la plataforma es una
  arista `platform_listing`. El mismo coche físico en coches.net + wallapop = 1 `vehicle`, 2 aristas.
- **El particular (C2C):** wallapop/milanuncios llevan vendedores particulares sin entidad dealer.
  Se modela como **bucket per-platform** (sentinel `c2c_private`, una entidad sintética por
  plataforma que posee todos sus coches C2C), no per-seller. El split dealer/particular vive en el
  `evidence` de cada verdict.

## Miembros validados (6)

El número del runbook es el del **verdict persistido** (único valor con VAM registrado). La DB viva
ha drenado por encima en varias plataformas (ingesta sin re-VAM); ese `live_edges` es columna
informativa **delta**, nunca el número validado.

| Plataforma | cdp_code | data_surface | governor | verdict id | **verdict_N** | live_edges | delta | Ficha |
|---|---|---|---|---:|---:|---:|---:|---|
| coches.net | CDP-ES-00-TKRV45RP | internal_api | STEALTH→JSON_API | **545** | **272.903** | 274.138 | +1.235 | [coches-net](../platforms/coches-net.md) |
| milanuncios | CDP-ES-00-E382JYEH | internal_api | STEALTH | **554** | **259.706** | 259.706 | 0 (exacto) | [milanuncios](../platforms/milanuncios.md) |
| wallapop | CDP-ES-00-EMRH0TWQ | app_api | JSON_API | **592** | **565.128** | 575.353 | +10.225 | [wallapop](../platforms/wallapop.md) |
| coches.com | CDP-ES-00-XM91J1NZ | next_data | STEALTH (1.0) | **551** | **91.066** | 92.088 | +1.022 | [coches-com](../platforms/coches-com.md) |
| autocasion | CDP-ES-00-QY06GW0B | graphql | JSON_API+STEALTH | **549** | **15.765** | 107.612 | **+91.847 ⚠** | [autocasion](../platforms/autocasion.md) |
| motor.es | CDP-ES-00-HSV4XZ2H | json_ld | STEALTH (0.7) | **558** | **49.009** | 49.009 | 0 (exacto) | [motor-es](../platforms/motor-es.md) |

**Lectura honesta:**
- **milanuncios (554) y motor.es (558)** están cuadrados al coche: verdict == live. Máxima confianza.
- **coches.net (545), wallapop (592), coches.com (551)** tienen delta pequeño-medio (ingesta viva
  post-verdict); el validado es el `verdict_N`, el live es la frontera de re-VAM pendiente.
- **autocasion (549)** tiene delta **+91.847**: el verdict avala solo **15.765**; los ~107k vivos
  vinieron de harvests sin re-VAM → **NO validado** (ver [NOT-VALIDATED.md](../NOT-VALIDATED.md)).

**Segmentos coches.net (`platform_segment_slice` TRUSTWORTHY):** new=6.151 (id 584), km0=3.107 (id
585), renting=1.212 (id 587). Σ VN = 10.470, 100 % dealer-owned. coches.com renting=1.034 (id 564),
vn=826 (id 492).
