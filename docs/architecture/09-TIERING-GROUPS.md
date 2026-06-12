# 09 · Tiering & Groups — la organización multi-eje (no "Tier-1 vs cola larga")

> El owner cazó el fallo: clasificar el mercado como un binario `is_tier1` vs long-tail es pobre.
> CARDEEP organiza cada fuente/entidad por **cuatro ejes ortogonales**, vivos en el esquema
> (migración 0016), no en prosa. La separación absoluta Tier-1 ↔ resto SIGUE — pero ahora con
> lógica y coherencia, como una jerarquía, no un interruptor.

## Eje 1 — DEFENSE TIER (`entity.defense_tier`) · granular, no binario
La dureza real de la defensa = qué herramienta del arsenal hace falta. Decide el routing del motor.

| Tier | Significado | Herramienta | Ejemplos ES (verificados) |
|---|---|---|---|
| **T0 open** | sin muro real | curl_cffi / sitemap / API abierta | AutoScout24, APIs OEM (Kia/MG/BYD…), DGT, OSM |
| **T1 soft** | WAF presente pero sirve | curl_cffi impersonate | **coches.net** (Imperva), autocasión (CF), coches.com (Imperva), motor.es |
| **T2 js_challenge** | hay que mintear cookie / pasar JS | **camoufox** warm-up | **milanuncios** (Imperva reese84), DataDome blando |
| **T3 hard_sensor** | sensor activo Akamai/Kasada/PX | nodriver / BotBrowser / Byparr | spoticar (Akamai) |
| **T4 spend_gated** | solo IP residencial de pago (tras agotar lo libre) | residencial + sensor | **NINGUNO en los gigantes ES** — probado: todos caen en T0-T3, €0 |

`is_tier1` queda como flag derivado de conveniencia (T2+ → tier1). La verdad granular vive en `defense_tier`.

## Eje 2 — GROUP / FAMILY (`entity.source_group` + `platform_meta.family`) · los "grupos"
Qué TIPO de operador/fuente es, por encima del `kind` de la entidad.

`marketplace_generalist` (wallapop, milanuncios) · `marketplace_motor` (coches.net, AS24, autocasión,
coches.com, motor.es) · `oem_vo_portal` (renew, DasWeltAuto, Spoticar, MB Certified) ·
`oem_dealer_network` (localizadores OEM) · `chain` (Flexicar, OcasionPlus, Clicars) ·
`rentacar_vo` (OK Mobility, Centauro) · `official_registry` (DGT, BORME, INE) ·
`association` (FACONAUTO, AEDRA, AMDA) · `directory` (Páginas Amarillas, OSM, FSQ) ·
`desguace_network` (AEDRA, DesguacesDirecto) · `long_tail_web` (la web propia del garaje de montaña).

**`family`** ata hermanos co-defendidos a UNA receta: `adevinta_schibsted` = coches.net + milanuncios +
fotocasa comparten infra → una familia de receta. (coches.net usa el gateway `web.gw.coches.net/search`
con `x-schibsted-tenant: coches`; milanuncios es server-rendered en la misma familia.)

## Eje 3 — ROLE (`entity.role`)
`platform` · `dealer_network` · `chain` · `standalone_pos` · `registry` · `directory`.
Una plataforma TIENE inventario (entidad de primera clase); un `standalone_pos` es el dealer atómico.

## Eje 4 — SEGMENT (`entity.kind`, ya existente)
concesionario_oficial · agente_oficial · compraventa · garaje · desguace · rent_a_car_vo · subasta ·
importador · oem_vo_portal · plataforma.

## Distribución VIVA (verificada en DB, 2026-06-12)
```
directory / standalone_pos        9.953   (OSM long-tail)
oem_dealer_network / standalone   1.362   (redes OEM)
desguace_network / standalone     1.292   (DGT CAT)
marketplace_motor / standalone      255   (dealers AS24)
marketplace_motor / platform          2   (AS24 t0_open · coches.net t1_soft·adevinta_schibsted)
```

## Cómo esto separa los Tier-1 "con lógica y coherencia"
- La separación física del repo (08) sigue: `platforms/_tier1/<name>/` ≠ long-tail.
- Pero el ENRUTADO y la operación ahora se deciden por `defense_tier` (qué motor) × `source_group`
  (qué receta-familia) × `role` — no por un sí/no. Un gigante abierto (AS24, T0) y un gigante con
  Akamai (spoticar, T3) son ambos "plataforma" pero se cosechan con tiers de motor distintos.
- La cobertura y el reporte se cortan por geo (provincia/comarca/ciudad) × segment × group:
  "100% de las compraventas de Valencia", "todas las plataformas T0-T1", "todos los desguaces".
