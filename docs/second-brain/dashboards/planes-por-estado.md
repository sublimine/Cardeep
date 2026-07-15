---
type: reference
tags: [second-brain]
---

# Planes por estado (Dataview)

Consulta viva sobre notas **nuevas** creadas con las plantillas de
`docs/second-brain/templates/` (el corpus legacy no tiene frontmatter, no puede
aparecer aquí hasta que se le añada).

⚠ Filtrado por `type` explícito (session/decision/plan), no por "tiene type" —
las 26k notas autogeneradas de Graphify (`docs/second-brain/gf/`) también
llevan `type: code` en su frontmatter y contaminarían esta tabla si el filtro
fuera genérico (encontrado y corregido el 2026-07-15).

```dataview
TABLE type, status, date
FROM "docs/second-brain"
WHERE type = "session" OR type = "decision" OR type = "plan"
SORT date DESC
```
