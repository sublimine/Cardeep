---
type: reference
tags: [second-brain]
---

# Planes por estado (Dataview)

Consulta viva sobre notas **nuevas** creadas con las plantillas de
`docs/second-brain/templates/` (el corpus legacy no tiene frontmatter, no puede
aparecer aquí hasta que se le añada).

```dataview
TABLE type, status, date
FROM "docs/second-brain"
WHERE type
SORT date DESC
```
