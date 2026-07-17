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

**Local funciona sin configurar nada**: cada variable tiene un default en código que ya
apunta al `cardeep-pg` de Compose. El fichero `.env.example` es **referencia** y **NO se
auto-carga** (el código lee `os.environ` con defaults — modelo 12-factor). Para sobrescribir
en un deploy real, **exporta** las variables al entorno (dos DSN: async para API/pipeline,
sync para el scheduler):

```bash
export CARDEEP_DSN=postgres://USER:PASS@HOST:5433/cardeep                  # asyncpg (API + pipeline)
export CARDEEP_DB_URL=postgresql+psycopg2://USER:PASS@HOST:5433/cardeep    # psycopg2 (scheduler jobstore)
```

Si cambias la contraseña, hazlo en el paso 2 (`CARDEEP_DB_PASSWORD`) y en **ambas** DSN. La
capa de pago (`DECODO_PROXY`, `CAPSOLVER_KEY`) se deja vacía hasta autorización del owner.

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
pip install -r requirements-dev.txt  # pytest + pytest-asyncio + numpy (SOLO para tests)
python -m pytest -q                   # la suite (live, rolled-back contra cardeep-pg)
```

Las deps de test viven aparte (`requirements-dev.txt`) de las de runtime — no se instalan
en producción. Los tests que tocan DB hacen SKIP automático si `cardeep-pg` no es alcanzable,
así que una suite verde confirma que la conexión, el esquema y la lógica están vivos.

## 7. Servir la API

```bash
uvicorn services.api.main:app --host 127.0.0.1 --port 8090
```

`services/api/main.py` monta `app = FastAPI(...)` con routers para entities, vehicles,
geo, platforms y ops. Single-worker por diseño (cache en proceso). Probar:

```bash
curl http://127.0.0.1:8090/                       # raíz / health
```

## 8. Arrancar el motor (cadencia durable) — SUPERVISADO, nunca en primer plano

> ⚠️ **Incidente real (F0, 2026-07-17)**: el motor estuvo PARADO 18 días (29-jun → 17-jul) porque
> la única instrucción que existía aquí era el comando en primer plano de abajo — muere al cerrar
> la terminal, y su propio `silence_watchdog` (job DEL scheduler) murió con él, así que nadie lo
> vio. Ver `plans/cardeep-omni/00-marketplace-engine.md` F0/F1 y
> `plans/cardeep-omni/EJECUCION_00_F0-F2_2026-07-17.md` para la evidencia completa.

**Procedimiento correcto — Docker Compose supervisado (`restart: unless-stopped`)**:

```bash
docker compose -f docker-compose.yml build api           # imagen fresca desde main (borra drift)
docker compose -f docker-compose.yml up -d cardeep-pg     # si no estaba ya en compose
docker compose -f docker-compose.yml up -d autopilot      # el motor, supervisado por Docker
docker compose -f docker-compose.yml ps                   # Up / healthy
docker logs -f cardeep-autopilot                          # latido, jobs, cosecha en vivo
```

Sobrevive: cierre de terminal, crash del proceso Python (Docker lo reinicia solo), reinicio del
host (si Docker Desktop arranca con el sistema). Verificación de que está VIVO, por 2 vías
independientes (protocolo §7 de la carta 00): `scheduler_lease.last_heartbeat` avanzando en dos
lecturas separadas ≥30 min, Y `apscheduler_jobs.next_run_time` avanzando entre las mismas dos
lecturas:

```sql
SELECT holder, pid, last_heartbeat, now()-last_heartbeat AS age FROM scheduler_lease;
SELECT id, to_timestamp(next_run_time) FROM apscheduler_jobs ORDER BY next_run_time;
```

**Watchdog externo (F1, obligatorio, ya instalado en este host)**: la tarea programada de
Windows `CardeepEngineWatchdog` (`pipeline/ops/engine_watchdog.py`, cada 5 min) vive FUERA del
contenedor y de Docker — lee `scheduler_lease` directamente por el puerto publicado (5433) y
escribe `state/engine_watchdog.log` (canal externo, funciona incluso con la DB caída) además de
disparar una alerta `critical` (`origin='engine:heartbeat'`) si el latido lleva >30 min parado.
Verificar que está instalada: `Get-ScheduledTask -TaskName CardeepEngineWatchdog`. En un host
sin Windows Task Scheduler, portar el mismo script a cron/systemd-timer — la única condición dura
es que corra en un proceso/host distinto del scheduler que vigila.

**Comando manual en primer plano (SOLO para depurar, nunca para producción)**:

```bash
python -m pipeline.ops.scheduler                  # BlockingScheduler + SQLAlchemyJobStore en PG
python -m pipeline.ops.scheduler --dry-run        # qué fuentes están DUE ahora (no ejecuta nada)
python -m pipeline.ops.scheduler --check-silence  # fuentes calladas > 2× su intervalo (read-only)
```

Es **single-producer**: una sola instancia (advisory lock de Postgres lo impone). Persiste los
jobs en `cardeep-pg`, así que sobrevive a reinicios sin re-disparar — pero SOLO si algo (Docker,
systemd, NSSM) reinicia el PROCESO tras un crash. El single-producer por sí solo no da
supervisión; la da el supervisor externo de arriba.

---

## Orden canónico (resumen)

```
1 clone → 2 docker compose up -d cardeep-pg → 3 venv + pip install
→ 4 cp .env.example .env → 5 migrate.py up/verify → 6 pytest
→ 7 uvicorn (API)  +  8 scheduler (motor)
```

Pasos 1–6 = sistema construido y verificado. Pasos 7–8 = sistema **sirviendo y latiendo**.

## A dónde ir después

- **Operar (monitorizar / verificar / remediar)**: [OPERATE.md](OPERATE.md) — el runbook del día a día.
- **Qué se scrapea / validación por unidad**: [RUNBOOK.md](../../RUNBOOK.md) raíz (ledger).
- **Arquitectura**: [docs/architecture/](../architecture/) (00–11) y [docs/runbook/](.) (00-OVERVIEW…).
- **Stack de verificación**: [docs/architecture/10-VERIFICATION-STACK.md](../architecture/10-VERIFICATION-STACK.md).
- **Estado vivo / plan**: `PROGRESO.md`, `docs/SUPERPLAN.md`.
