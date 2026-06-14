# HANDOFF — arranque de sesión fresca (2026-06-14)

> LEE ANTES DE TOCAR NADA: este archivo + `docs/design/ENTITY_RESOLUTION_ARCHITECTURE.md`
> (arquitectura canónica) + `docs/PROGRESO.md` (estado vivo) + `git log -15` + los counts de
> cardeep-pg :5433. El código en main y la DB mandan; la memoria puede estar stale.

## Estado del corte (limpio, nada a medias sin declarar)
Sistema vivo: ~1,69M anuncios frescos (100% vistos <48h) ≈ **1,44M coches físicos únicos** (vía B7);
~59,5k entities profesionales (P); API + latido (scheduler) + auto-reparación operativos.

## SELLADO y vivo (no tocar salvo bug)
- **B1** identidad · **B2** latido · **B3** auto-reparación + API — CERRADOS en main.
- **B4** geo (mecanismo) · **B5** cobertura (Overture +10.913 ventas, AS24 +41k coches) — en main.
- **B9 Post-Harvest Verification Gate** (`2018a79`): verificación de cobertura AUTOMÁTICA
  declared-vs-captured tras cada harvest → `source_coverage` (auditable de un vistazo) + verdict
  simétrico (sobre-cobertura REFUTED, fix del Director) + alerta origen-exacto + auto_repair.
  Verificado: wallapop 90,3% real, milanuncios REFUTED (declared infra-calculado, flageado). RUNBOOK §cobertura.
- **Dedup dealers B1** (`dealer-identity-det-v1`, vam_verified=TRUE): 42.259 dealers canónicos. v_canonical sirve.

## Overlays NO sellados (vam_verified=FALSE) — pendientes de gate/fix
- `vehicle-identity-det-v1` (B7, coches): 1,44M únicos. Riesgo residual a cuantificar antes de sellar:
  coches 0km/nuevos de stock (la firma make+model+year+km+price podría fundir 2 unidades distintas).
- `cross-source-dedup-v1` (688 OSM×digital): marginal — componer en B1∘β o descartar.
- `entity_resolution` (F1 β): S_obs=52.156. DOS FIXES antes de sellar (ver siguiente paso).

## SIGUIENTE PASO EXACTO — retomar aquí
Arquitectura canónica: `docs/design/ENTITY_RESOLUTION_ARCHITECTURE.md` (tesis del Owner, auditada y
validada por el Director; huella de inventario = clave DOMINANTE de β, identificadores casi-vacíos en digital).

1. **Cerrar F1 (β) antes de sellar** — `pipeline/identity/resolve_entities.py`:
   - (a) **GUARDA DE CADENAS**: la huella NO debe fusionar cuando el nombre lleva token de CIUDAD
     distinta (CLICARS Barcelona ≠ Valencia) o es cadena conocida con stock central (Clicars/Flexicar/
     OcasionPlus) → ahí exige identificador fuerte, no solo Jaccard≥0.30. BUG CAZADO: Clicars 4 ciudades
     fundido en 1 dealer (su province_code está mal, las 4 en 46, por eso el cross-province guard no las separó).
   - (b) **COMPONER B1 ∘ β**: hoy β opera sobre las 59.502 entities BRUTAS, independiente de B1. El
     numerador real de P = union-find de las aristas de AMBOS (B1 name+muni + β huella). Sembrar el
     union-find de resolve_entities con los clusters de `dealer-identity-det-v1`.
   - Re-correr → gate cero-sobre-fusión (revisar los clusters grandes por nombre, no solo por province) → sellar.
2. **F2** — calibrar φ (fracción-ocasión): DIRCE (`data/official/dirce_*.csv`) ∩ dealers β derivados
   vendiendo ocasión → φ medida. `N_prof ≈ φ·N_fiscal` con CI.
3. **F3** — Chao2 (`Ŝ = S_obs + Q₁²/2Q₂`) sobre mecanismos ORTOGONALES: fiscal (DIRCE) × comercial
   (canal) × geográfico (OSM acotado a P). NUNCA canal×canal (da suelo, no techo). + cierre contra
   saturación: `observado ≈ N̂` dentro del CI = evidencia de completitud.
4. **F0** (paralelo) — re-modelar los 329k particulares como LISTADOS, no entidades (salen del modelo P;
   dejan de inflar la base; siguen como inventario con dedup-α B7).

## Doctrina viva destilada de esta sesión
- VAM ≥2 vías ORTOGONALES; el `declared` de la propia fuente es la ÚNICA vía externa para cobertura.
- El gate del Director (Opus) caza lo que el agente no ve (Clicars sobre-fusión, milanuncios 360% TRUSTWORTHY
  falso). NUNCA sellar (vam_verified=TRUE) sin gate manual de muestra.
- Estratos no se prestan método: Canales (finito, "todos" verificable) / Profesionales (acotado+derivado,
  X% con CI) / Privados (cobertura-vía-listados, jamás de entidades).
- NO re-scrapear lo que ya está; el latido lo recosecha. El esfuerzo va a cobertura nueva + derivación + cierre.
- "Sellado" = medido con denominador (legal donde exista, estimado-declarado donde no) + numerador VAM-estable
  + cada gap confesado con causa. Desguace 52/52 (censo DGT). Venta 88% servido nacional (denominador estimado).
