# Cardeep

Mapa vivo del mercado de coches de España: el 100% de los puntos de venta —
de la plataforma gigante al garaje de montaña — con todo su inventario en tiempo
real, servido por una API con delta completo (altas, bajas, cambios de precio y
de foto, historial íntegro).

**Estado:** fundación (F0) + censo de fuentes (F1) en curso. Ver [PLAN.md](PLAN.md)
para el plan maestro A→Z y [PROGRESO.md](PROGRESO.md) para la bitácora viva.

**Gobierno:** [CLAUDE.md](CLAUDE.md) — mandato y doctrina de operación.

## Quickstart (€0, local)
De máquina limpia a sistema corriendo en 8 pasos verificados — ver
[docs/runbook/DEPLOY.md](docs/runbook/DEPLOY.md):

```bash
docker compose up -d cardeep-pg          # 1. DB (postgres:16 en :5433)
python -m venv .venv && pip install -r requirements.txt -r requirements-dev.txt   # 2. deps (+test)
cp .env.example .env                     # 3. config (opcional — local corre con defaults)
python scripts/migrate.py up             # 4. esquema (→0040)
python -m pytest -q                      # 5. smoke test
uvicorn services.api.main:app --host 127.0.0.1 --port 8090   # 6. API
python -m pipeline.ops.scheduler                     # 7. motor durable
```

## Principios
- **Cero confianza:** ningún número es bueno sin quórum ≥2 vías ortogonales (VAM).
- **Receta sobre crudo:** el activo es la receta versionada por dealer; el crudo
  es efímero y se evicta por capacidad con prueba (tombstone).
- **Tier-1 separado:** las plataformas con defensas duras viven aparte del
  long-tail en datos, código y operación.
- **Huella total:** recetas, estado y decisiones commiteadas en `main`; cualquiera
  puede retomar el proyecto desde este repo.

## Mapa del proyecto (para retomar)

| Quiero… | Ir a |
|---|---|
| Ver el backlog A→F clasificado y filtrable | [Issues en GitHub](https://github.com/sublimine/Cardeep/issues) (label por letra/estado/gate/área · 4 milestones) — se regenera con `python scripts/github_classify.py` |
| Entender el plan de sellado punto-por-punto | [`docs/SUPERPLAN.md`](docs/SUPERPLAN.md) §4 (fuente de verdad de las Sealing Units) |
| Ver el estado certificado A→F | [`docs/AUDIT_A-F_STATUS.md`](docs/AUDIT_A-F_STATUS.md) |
| Entender los workflows (E2E per-dealer + verificación) | [`docs/workflows/`](docs/workflows/README.md) — `e2e/` (descubrir→scrapear→receta→API→borrar) + `verification/` (VAM→ledger→Inquisición→gestionador) |
| Levantar el sistema de cero | [`docs/runbook/DEPLOY.md`](docs/runbook/DEPLOY.md) |
| Operarlo (monitor / verify / remediar) | [`docs/runbook/OPERATE.md`](docs/runbook/OPERATE.md) |
| Entender el stack de verificación (4 capas) | [`docs/architecture/10-VERIFICATION-STACK.md`](docs/architecture/10-VERIFICATION-STACK.md) |
