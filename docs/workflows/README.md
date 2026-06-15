# Cardeep — Arquitectura de Workflows

El pipeline de produccion es codigo Python determinista (`pipeline/`) para todo lo masivo:
descubrir, scrapear, ingerir, delta, verificar. Los agentes LLM se reservan estrictamente
para dos casos que requieren inteligencia: caza de receta en plataformas Tier-1 y verificacion
adversarial (Inquisition). El gasto caro va solo a decidir; lo escalable corre en local a €0.

## Flujo completo

```
DESCUBRIR -> SCRAPEAR -> RECETA -> INGEST -> SERVE-API
                                       |
                                     DELTA
                                       |
                               VAM -> DEEP-LEDGER -> INQUISITION -> GESTIONADOR
                                       |
                                     BORRAR (POR CONSTRUIR)
```

## Indice de documentacion

| Carpeta | Documento | Modulo real | Estado | €0/Gasto |
|---|---|---|---|---|
| workflows/ | README (este) | — | IMPLEMENTADO | — |
| workflows/e2e/ | 00-LIFECYCLE-OVERVIEW.md | pipeline/ (global) | IMPLEMENTADO | €0 |
| workflows/e2e/ | 01-DISCOVER.md | pipeline/discover.py | IMPLEMENTADO | €0 |
| workflows/e2e/ | 02-SCRAPE.md | pipeline/engine/fetch.py + governor.py | IMPLEMENTADO | €0 |
| workflows/e2e/ | 03-RECIPE.md | pipeline/platform/ (44 conectores) | IMPLEMENTADO | €0 / Gasto Tier-1 |
| workflows/e2e/ | 04-INGEST.md | pipeline/ingest.py + delta.py + delta_guard.py | IMPLEMENTADO | €0 |
| workflows/e2e/ | 05-SERVE-API.md | services/api/main.py | IMPLEMENTADO | €0 |
| workflows/e2e/ | 06-DELTA.md | pipeline/delta.py + delta_guard.py | IMPLEMENTADO | €0 |
| workflows/e2e/ | 07-EVICT-DELETE.md | pipeline/evict.py | POR CONSTRUIR | €0 |
| workflows/verification/ | 00-VERIFICATION-OVERVIEW.md | pipeline/verify.py | IMPLEMENTADO | €0 |
| workflows/verification/ | WF-VAM.md | pipeline/verify.py | IMPLEMENTADO | €0 |
| workflows/verification/ | WF-DEEP-LEDGER.md | verdict_audit + chk_trustworthy_needs_quorum + ops/inquisition_schedule.py | IMPLEMENTADO | €0 |
| workflows/verification/ | WF-INQUISITION.md | pipeline/inquisition/ | IMPLEMENTADO | Gasto (lens C) |
| workflows/verification/ | WF-GESTIONADOR.md | pipeline/gestionador/ | IMPLEMENTADO | €0 |
| workflows/verification/ | WF-CADENCE.md | pipeline/ops/scheduler.py + inquisition_schedule.py | IMPLEMENTADO | €0 |
| workflows/ | AGENT-SKILL-TOOL-MATRIX.md | — (referencia cruzada) | REFERENCIA | — |

## Capas de verificacion

| Capa | Migracion | Modulo | Trigger | Estado |
|---|---|---|---|---|
| L1 VAM (count quorum) | 0004 | pipeline/verify.py | post-discover / post-ingest | IMPLEMENTADO |
| L2 Deep Ledger (quorum DB + hash-chain) | 0026 | verdict_audit + chk_trustworthy_needs_quorum + ops/inquisition_schedule.py | cadencia δ TTL | IMPLEMENTADO |
| L3 Gestionador (maquina de estados) | 0031 | pipeline/gestionador/ | post-ingest / post-inquisition | IMPLEMENTADO |
| L4 Inquisition V3 (adversarial, 5 lenses) | 0032 | pipeline/inquisition/ | bridge VAM / cadencia δ / manual | IMPLEMENTADO |

## Nota de metodo

Pipeline determinista para escala: cada entidad sigue el mismo grafo de estados sin variacion.
Inquisition y recipe-hunt con agentes: solo cuando se necesita razonar sobre casos ambiguos o
cazar configuraciones de plataformas con defensas duras.

## Estado harvest-gated

Los siguientes modulos estan construidos e integrados pero bloqueados por gasto de produccion
hasta que se autorice el presupuesto de harvest real:

- **Scraping real contra dealers**: fleet de 44 conectores en `pipeline/platform/` lista,
  pero no esta corriendo en produccion contra inventario real.
- **Lens C de Inquisition**: live re-fetch dentro del ciclo adversarial; requiere proxies
  premium o ancho de banda de produccion.
- **Heartbeat harvest real en scheduler**: `pipeline/ops/scheduler.py` tiene el hook
  configurado pero el harvest periodico no esta activado en produccion.

Lo que SI corre en €0 ahora mismo: discover (fuentes publicas), ingest de datos ya obtenidos,
VAM, deep-ledger, Inquisition sin lens C, Gestionador, API.
