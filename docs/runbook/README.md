# CARDEEP RUNBOOK — arquitectura del sistema de documentación
> La guía maestra de **TODO lo que funciona**, validado. Regla dura: **nada entra aquí sin
> veredicto `verification_verdict` TRUSTWORTHY o conector probado en vivo.** Cero maquillaje.
> Esta es la **bitácora viva**: cada cierre E2E (plataforma, receta, config, herramienta) se
> registra con la plantilla de abajo. Código/comandos en inglés, prosa en español.

---

## 1 · Arquitectura del runbook (estructura canónica)

```
docs/runbook/
├── README.md                ← (este) índice + arquitectura + plantilla + protocolo
├── 00-OVERVIEW.md           ← cómo se scrapea el país END-TO-END (DESCUBRIR→SCRAPEAR→RECETA→API→DELTA)
├── 01-ARCHITECTURE.md       ← motor: governor · fetch · schema · geo (país/provincia/comarca/ciudad)
│                              · cdp_code · VAM · S-HEALTH · API · dedup watermark
├── 02-GROUP-SEPARATION.md   ← la lógica que separa Tier-1 / OEM-VO / cadenas / rentacar / subastas / long-tail
├── 03-DISCOVERY.md          ← fase DESCUBRIR: arneses de hallazgo de puntos de venta (association-mining · geo-sweep)
├── 04-TERRITORIAL.md        ← fase F8 SELLO: censo vs cobertura (INE DIRCE + Overture POI ortogonal), gap-map honesto
├── groups/<grupo>.md        ← un capítulo por GRUPO (resumen + tabla de sus miembros validados)
├── platforms/<slug>.md      ← un fichero por CONECTOR validado (plantilla §3, uniforme)
├── VALIDATION-INDEX.md      ← LEDGER vivo: unidad → verdict id → count → CLI → fecha
└── NOT-VALIDATED.md         ← apéndice: lo intentado/aspiracional/roto que NO entra al runbook
```

**Principio de arquitectura:** *una entrada = un fichero*, *toda entrada con la MISMA plantilla*,
*todo número con su prueba*. Navegable de arriba (overview) a abajo (un conector) sin ambigüedad.
Alta cohesión (un fichero = un conector), bajo acoplamiento (los grupos referencian, no copian).

---

## 2 · Eje de clasificación (cómo se separan los grupos)

| Grupo | `source_group` | `kind` entidad-plataforma | Naturaleza |
|---|---|---|---|
| Tier-1 marketplaces | `marketplace_motor` / `marketplace_generalist` | `plataforma` | gigantes C2C+PRO |
| OEM-VO | `oem_vo_portal` | `oem_vo_portal` | VO certificado de marca |
| Cadenas | `chain` | `cadena` | cadenas nacionales VO |
| Rent-a-car VO | `rentacar_vo` | `rent_a_car_vo` | ex-flota |
| Subastas | `official_registry` | `subasta` | remarketing B2B/B2C |
| Long-tail | `long_tail_web` | `compraventa`/`concesionario_oficial` | web propia |

Tier-1 separado **absolutamente** del resto (eje `defense_tier` t0_open..t4_spend_gated independiente).

---

## 3 · PLANTILLA UNIFORME por conector (copiar para cada entrada nueva)

```markdown
# <Plataforma> — <slug>
**Estado:** ✅ VALIDADO (verdict id=<N>, count=<M>, <fecha>)  ·  **Grupo:** <grupo>

## Identidad
- cdp_code: `CDP-ES-00-XXXX` · kind: `<kind>` · source_group: `<sg>` · defense_tier: `<t>` · family: `<f>`

## Data-layer (la fuente real)
- Endpoint: `<METHOD url>`  ·  Auth/headers: `<...>`  ·  Tope/partición: `<...>`
- Esquema de petición: `<json/params>`

## Micro-acciones (cómo se scrapea, paso a paso)
1. ...  2. ...  3. ...   (enumeración exacta y reproducible)

## Receta / config
- Conector: `pipeline/platform/<file>.py`  ·  Governor: `<STEALTH|JSON_API|bespoke rate>`
- Parser/identidad: `<deep_link/dedup key>`  ·  Cage: plataforma-entidad + dealer + platform_listing + delta + recipe

## Validación (VAM)
- Caminos ortogonales: `<edges == join == distinct_ref>` = <M>  ·  verdict id=<N> TRUSTWORTHY  ·  fecha

## CLI (reproducible)
`CARDEEP_DSN=... python -m pipeline.platform.<file> <flags>`

## Trampas / notas
- ...
```

---

## 4 · Protocolo de BITÁCORA VIVA (de aquí en adelante, obligatorio)

Cada vez que se cierre algo **end-to-end y validado**:
1. Crear/actualizar `platforms/<slug>.md` con la plantilla §3 (solo si VAM TRUSTWORTHY).
2. Añadir una fila a `VALIDATION-INDEX.md`: `<unidad> | verdict id | count | CLI | fecha`.
3. Referenciarlo desde su `groups/<grupo>.md`.
4. Si se intentó y NO se validó → va a `NOT-VALIDATED.md` con la evidencia del bloqueo, nunca al runbook.
5. Commit `docs(runbook): <unidad> validada` → GitHub main.

**Definición de "validado y funcional":** existe fila `verification_verdict` TRUSTWORTHY **Y** el conector
re-ejecuta idempotente (re-run = 0 nuevos) **Y** el número concuerda por ≥2 caminos DB. Si falta una, NO entra.
