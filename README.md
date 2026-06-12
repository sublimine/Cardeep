# Cardeep

Mapa vivo del mercado de coches de España: el 100% de los puntos de venta —
de la plataforma gigante al garaje de montaña — con todo su inventario en tiempo
real, servido por una API con delta completo (altas, bajas, cambios de precio y
de foto, historial íntegro).

**Estado:** fundación (F0) + censo de fuentes (F1) en curso. Ver [PLAN.md](PLAN.md)
para el plan maestro A→Z y [PROGRESO.md](PROGRESO.md) para la bitácora viva.

**Gobierno:** [CLAUDE.md](CLAUDE.md) — mandato y doctrina de operación.

## Principios
- **Cero confianza:** ningún número es bueno sin quórum ≥2 vías ortogonales (VAM).
- **Receta sobre crudo:** el activo es la receta versionada por dealer; el crudo
  es efímero y se evicta por capacidad con prueba (tombstone).
- **Tier-1 separado:** las plataformas con defensas duras viven aparte del
  long-tail en datos, código y operación.
- **Huella total:** recetas, estado y decisiones commiteadas en `main`; cualquiera
  puede retomar el proyecto desde este repo.
