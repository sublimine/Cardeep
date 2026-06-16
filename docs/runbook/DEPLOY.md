# DEPLOY — de máquina limpia a Cardeep corriendo (A→Z)

> El cold-start operativo. Cada comando aquí está **verificado contra el código**, no
> asumido. El [RUNBOOK.md](../../RUNBOOK.md) raíz cubre la *operación* (qué se scrapea,
> validación por unidad); este doc cubre el *bring-up* (cómo levantar el sistema).
>
> Coste: **€0**. Todo corre local. La capa de pago (proxies, captcha, harvest a escala)
> está apagada hasta autorización del owner — ver `.env.example`.

---

## 0. Requisitos

| Pieza | Versión | Verificación |
|---|---|---|
| Python | 3.11 | `python --version` → 3.11.x (los `.pyc` del repo son cpython-311) |
| Docker + Compose v2 | cualquiera reciente | `docker compose version` |
| git | cualquiera | `git --version` |

Sistema operativo: desarrollado en Windows 11 (PowerShell) y POSIX. Los comandos de DB
van por `docker exec`, así que el host es indiferente.

---

## 1. Clonar

```bash
git clone https://github.com/sublimine/Cardeep.git
cd Cardeep
```

## 2. Levantar la base de datos (el backbone)

PostgreSQL 16, puerto **5433** (no 5432, para no chocar con un PG local), volumen
nombrado `cardeep_pg_data` que persiste todo el censo:

```bash
docker compose up -d cardeep-pg
```

Verificar que está sano:

```bash
docker compose ps                      # STATUS debe decir "healthy"
docker exec cardeep-pg pg_isready -U cardeep -d cardeep   # → "accepting connections"
```

> El `docker-compose.yml` reproduce EXACTAMENTE el container vivo y **adopta el volumen
> existente** si ya lo tienes (cero pérdida de datos). En una máquina limpia lo crea vacío
> y las migraciones (paso 5) lo construyen entero.

## 3. Entorno Python

```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# POSIX:               source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` incluye `apscheduler[sqlalchemy]` — el extra es **obligatorio** para el
scheduler durable (jobstore en PG). Sin él, el motor de cadencia no arranca.

## 4. Configuración

```bash
cp .env.example .env
```

El default de `.env.example` ya apunta al `cardeep-pg` de Compose
(`postgres://cardeep:cardeep_dev_only@localhost:5433/cardeep`). Para un deploy real,
sobrescribe `CARDEEP_DB_PASSWORD` antes del paso 2 y ajusta el DSN. La capa de pago
(`DECODO_PROXY`, `CAPSOLVER_KEY`) se deja vacía hasta autorización.

## 5. Migraciones — construir el esquema

```bash
python scripts/migrate.py up        # aplica 0001 … 0040 en orden, idempotente
python scripts/migrate.py status    # lista aplicadas vs pendientes
python scripts/migrate.py verify    # valida que el esquema vivo == migraciones (drift = fallo)
```

`migrate.py` acepta: `up` (default), `status`, `verify`, `repair <versión...>`. La más
nueva es **0040** (`servable_price_floor`).

## 6. Smoke test — probar que todo respira

```bash
python -m pytest -q                  # la suite (live, rolled-back contra cardeep-pg)
```

Los tests que tocan DB hacen SKIP automático si `cardeep-pg` no es alcanzable, así que
una suite verde confirma que la conexión, el esquema y la lógica están vivos.

## 7. Servir la API

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8090
```

`services/api/main.py` monta `app = FastAPI(...)` con routers para entities, vehicles,
geo, platforms y ops. Single-worker por diseño (cache en proceso). Probar:

```bash
curl http://127.0.0.1:8090/                       # raíz / health
```

## 8. Arrancar el motor (cadencia durable)

```bash
python -m pipeline.ops.scheduler                  # BlockingScheduler + SQLAlchemyJobStore en PG
python -m pipeline.ops.scheduler --dry-run        # qué fuentes están DUE ahora (no ejecuta nada)
python -m pipeline.ops.scheduler --check-silence  # fuentes calladas > 2× su intervalo (read-only)
```

Es **single-producer**: una sola instancia. Persiste los jobs en `cardeep-pg`, así que
sobrevive a reinicios sin re-disparar (lo que da la propiedad "Cardeep no se cae").

---

## Orden canónico (resumen)

```
1 clone → 2 docker compose up -d cardeep-pg → 3 venv + pip install
→ 4 cp .env.example .env → 5 migrate.py up/verify → 6 pytest
→ 7 uvicorn (API)  +  8 scheduler (motor)
```

Pasos 1–6 = sistema construido y verificado. Pasos 7–8 = sistema **sirviendo y latiendo**.

## A dónde ir después

- **Operar / qué se scrapea**: [RUNBOOK.md](../../RUNBOOK.md) raíz (validación por unidad, ledger).
- **Arquitectura**: [docs/architecture/](../architecture/) (00–11) y [docs/runbook/](.) (00-OVERVIEW…).
- **Stack de verificación**: [docs/architecture/10-VERIFICATION-STACK.md](../architecture/10-VERIFICATION-STACK.md).
- **Estado vivo / plan**: `PROGRESO.md`, `docs/SUPERPLAN.md`.
