# Frontend spec — ARCHIVADO 2026-06-15

Material de la antigua carpeta `~/projects/cardeep-web` (que **NO era repo git**), archivado aquí
y eliminado del workspace por decisión del Owner (**D2, 2026-06-15**): *sin frontend por el
momento*, foco 100% backend/datos.

Preservado por el invariante «nada se pierde» (MISSION §3, ley #9). Cuando se retome el portal,
se parte de aquí — no se reactiva sin orden del Owner.

## Contenido
- `design-system-preview.html` — preview del sistema de diseño (tokens, color, tipografía).
- `packages/design/tokens.css` — design tokens (variables CSS).
- `proto/hero.html` — prototipo de la sección hero.

## Acoplamiento previsto (cuando aplique)
El portal consumiría la API FastAPI de `services/api/` (endpoints `/entities/{cdp}`,
`/inventory`, `/delta`, `/geo/{prov}/tree`). Backend soberano en `cardeep-pg :5433`.
