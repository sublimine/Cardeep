---
type: moc
tags: [second-brain]
---

# Cardeep — Home

## Arquitectura y motor
- [[docs/architecture/README|Architecture overview]]
- [[docs/architecture/SYSTEM-A-Z|System A-Z]]
- [[docs/architecture/13-API-AND-DELTA|API y delta]]
- [[docs/generic-engine-bible/00-MASTER|Generic Engine Bible — master]]
- [[docs/generic-engine-bible/COUNTRY-PROOF-BUILD|Country-proof build]]
- [[docs/generic-engine-bible/COUNTRY-2-READINESS|Country-2 readiness]]
- [[docs/MASTER_PLAN_CARDEEP_V2_2026-06-20|Master Plan V2]]

## Planes activos
- [[plans/autonomy-e2e/00-PLAN|Autonomy E2E]]
- [[plans/road-to-13/00-ROADMAP|Road to 13]]
- [[plans/country-autopilot/00-DESIGN|Country autopilot]]
- [[plans/cardeep-program/00-MASTER|Programa institucional A-Z]]

## Bitácora
- [[PROGRESO|PROGRESO.md — bitácora completa]]
- [[PLAN|PLAN.md]]
- [[RUNBOOK|RUNBOOK.md]]
- [[CLAUDE|CLAUDE.md]]
- [[INSTALL|INSTALL.md]]
- [[README|README.md]]

## Segundo cerebro
- [[docs/second-brain/dashboards/pendientes-owner-search|Pendientes del owner]]
- [[docs/second-brain/dashboards/planes-por-estado|Planes por estado (Dataview)]]
- [[docs/second-brain/canvas/system-map|Mapa del sistema (Canvas)]]

## Grafo de código (Graphify)
Capa complementaria: mientras `docs/`/`plans/` es el segundo cerebro (decisiones,
contexto, prosa), esto es el mapa **estructural real del código** — parseado
100% local con tree-sitter (AST puro, sin LLM), sin `.env`/secretos (excluidos
por diseño y verificado por escaneo de patrones el 2026-07-15). 25.737 nodos
código+SQL, 41.061 edges, 1.295 comunidades sobre `pipeline/`, `services/`,
`web/`, `scripts/`, `migrations/`, `tests/` (`portal/` excluido vía
`.graphifyignore`, mismo criterio que el resto del vault).

⚠ `docs/second-brain/gf/` y `graphify-out/` son **artefactos regenerados**, no
versionados (mismo tratamiento que `data/` — ver `.gitignore`). En un clon
nuevo estos enlaces aparecen rotos hasta ejecutar:
`graphify update . && graphify export obsidian --graph graphify-out/graph.json --dir docs/second-brain/gf`
(un `graphify hook install` deja esto automático tras cada commit).

- [[docs/second-brain/gf/graph.canvas|Grafo interactivo (Canvas, coloreado por comunidad)]]
- Consulta directa sin abrir Obsidian: `graphify query "<pregunta>"` / `graphify explain "<símbolo>"` / `graphify path "A" "B"` sobre `graphify-out/graph.json`

## Índice exhaustivo (corpus completo — .md + artefactos de datos, cero huecos verificados de forma determinista)

Los enlaces de arriba son una selección curada. Estos 20 hubs indexan **cada
archivo real** de `docs/` y `plans/` — de cualquier extensión, no solo `.md`
(generados desde el sistema de archivos, cero rutas inventadas, auditado con
`scripts` de resolución de wikilinks el 2026-07-15) — así el grafo conecta el
corpus entero, no solo una selección.

### docs/
- [[docs/second-brain/dashboards/hubs/docs-root|docs/ (raíz) — 19]]
- [[docs/second-brain/dashboards/hubs/docs-ai|docs/ai — 86]]
- [[docs/second-brain/dashboards/hubs/docs-architecture|docs/architecture — 92]]
- [[docs/second-brain/dashboards/hubs/docs-archive|docs/archive — 4]]
- [[docs/second-brain/dashboards/hubs/docs-design|docs/design — 4]]
- [[docs/second-brain/dashboards/hubs/docs-frontend|docs/frontend — 9]]
- [[docs/second-brain/dashboards/hubs/docs-generic-engine-bible|docs/generic-engine-bible — 25]]
- [[docs/second-brain/dashboards/hubs/docs-outputs|docs/outputs — 5]]
- [[docs/second-brain/dashboards/hubs/docs-recon|docs/recon — 16]]
- [[docs/second-brain/dashboards/hubs/docs-research|docs/research — 50]]
- [[docs/second-brain/dashboards/hubs/docs-runbook|docs/runbook — 61]]
- [[docs/second-brain/dashboards/hubs/docs-superpowers|docs/superpowers — 2]]
- [[docs/second-brain/dashboards/hubs/docs-workflows|docs/workflows — 16]]

### plans/
- [[docs/second-brain/dashboards/hubs/plans-root|plans/ (raíz) — 21]]
- [[docs/second-brain/dashboards/hubs/plans-autonomy-e2e|plans/autonomy-e2e — 5]]
- [[docs/second-brain/dashboards/hubs/plans-cardeep-program|plans/cardeep-program — 11]]
- [[docs/second-brain/dashboards/hubs/plans-country-autopilot|plans/country-autopilot — 4]]
- [[docs/second-brain/dashboards/hubs/plans-frontend-definitivo|plans/frontend-definitivo — 3]]
- [[docs/second-brain/dashboards/hubs/plans-intel-audit|plans/intel-audit — 127]]
- [[docs/second-brain/dashboards/hubs/plans-road-to-13|plans/road-to-13 — 4]]
