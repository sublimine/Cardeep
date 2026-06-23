# DEPLOY — daemons durables (que CARDEEP no se caiga)

> Cómo hacer que los **tres procesos de larga vida** de CARDEEP sobrevivan a un crash,
> a un cierre de terminal y a un reinicio del host. Cubre el target final **Linux VPS
> (systemd)** y el **host actual Windows 11 (Task Scheduler / NSSM)**.
>
> Cada comando, puerto, lock y variable de entorno de aquí está **verificado contra el
> código** (con `archivo:línea`), no asumido. [DEPLOY.md](runbook/DEPLOY.md) levanta el
> sistema a mano (cold-start); este doc lo convierte en **servicios supervisados**.
>
> **Instalar cualquier cosa de este doc es un paso de OWNER que toca el host.** Las units
> systemd viven en `ops/systemd/*.service` como artefactos inertes: cero efecto en runtime
> hasta que se copian a `/etc/systemd/system/` y se habilitan. Coste: €0.

---

## 0. Los tres daemons (entrypoints reales)

| Daemon | Comando (verificado) | Naturaleza | Lock singleton |
|---|---|---|---|
| **API** | `uvicorn services.api.main:app --host … --port 8090` (`services/api/main.py:6`, dev default `127.0.0.1:8090` en `main.py:134`) | proceso bloqueante; cache en proceso, single-worker (`main.py:109`) | — (stateless; varias réplicas OK tras un proxy) |
| **Harvest** | `python -m pipeline.ops.scheduler` (`pipeline/ops/scheduler.py:22`) | `BlockingScheduler` + `SQLAlchemyJobStore` en PG (`scheduler.py:831,855`) | advisory `0x43415244` = **1128354372** (`scheduler.py:842-852`) |
| **Discovery** | `python -m pipeline.discover_schedule --serve` (`pipeline/discover_schedule.py:28`) | `BlockingScheduler` propio (`discover_schedule.py:230`) | advisory `0x43415244+1` = **1128354373** (`discover_schedule.py:50,240`) |

**Por qué un supervisor.** Los tres son **session-bound**: sin systemd/NSSM/Task Scheduler,
un reinicio del host o un cierre de la terminal los mata y no vuelven. El supervisor da
`Restart=always` (auto-recuperación ante crash/OOM) y arranque en boot.

**Por qué reiniciar NO duplica producción (la cicatriz AS24).** El harvest y el discovery
son **single-producer por diseño dentro del código**, no por el supervisor:

- Harvest toma un advisory lock de sesión `1128354372`; un segundo proceso hace
  `SystemExit("another cardeep scheduler already holds the singleton advisory lock …")`
  (`scheduler.py:846-852`).
- Discovery toma `1128354373`; un segundo proceso hace
  `SystemExit("another discovery scheduler holds the advisory lock …")`
  (`discover_schedule.py:240-242`).

El lock se **auto-libera** al cerrar la conexión en la salida limpia del proceso. Por eso
`Restart=always` jamás corre dos productores a la vez: el nuevo proceso toma el lock que el
muerto soltó. Si el anterior murió **en duro** (SIGKILL/OOM), el lock de sesión persiste
hasta que Postgres recolecta el backend muerto; durante esa ventana el reinicio reintenta.
La tabla `scheduler_lease` (migración `0054`) + el heartbeat de 2 min hacen esa ventana
**observable** (ver §4).

> El API NO tiene lock: es stateless respecto a la cadencia y puede correr en varias
> réplicas detrás de un proxy. El estado de los jobs vive en PG, no en el proceso.

---

## 1. Variables de entorno requeridas en prod

Los daemons leen `os.environ` con defaults de dev (modelo 12-factor; ver `.env.example`).
En **prod** hay que inyectar valores reales o los guards de seguridad fallan al arranque:

| Variable | La lee | Forma | Notas |
|---|---|---|---|
| `CARDEEP_ENV` | `pipeline/config_guard.cardeep_env()` | `prod` | Activa el fail-fast de DSN y el API-key obligatorio. Default `dev` = comportamiento actual idéntico. |
| `CARDEEP_DSN` | API (`services/api/deps.py:15`) + harvest (`scheduler.py:62`) | `postgres://USER:PASS@DBHOST:5432/cardeep` | asyncpg. En harvest es la **forma keyword** `host=… port=… dbname=… user=… password=…`. |
| `CARDEEP_DB_URL` | harvest jobstore (`scheduler.py:57`) | `postgresql+psycopg2://USER:PASS@DBHOST:5432/cardeep` | psycopg2 / SQLAlchemy. Obligatorio para el jobstore durable. |
| `CARDEEP_ASYNCPG_DSN` | harvest (`scheduler.py:68`) + discovery (`discover_schedule.py:42`) | `postgresql://USER:PASS@DBHOST:5432/cardeep` | asyncpg URL. Discovery cae a `CARDEEP_DSN` si falta. |
| `CARDEEP_DSN_KW` | discovery lock conn (`discover_schedule.py:235`) | `host=DBHOST port=5432 dbname=cardeep user=USER password=PASS` | psycopg2 keyword form de la conexión que sostiene el advisory lock. |
| `CARDEEP_API_KEY` | `services/api/deps.py` `require_api_key` | clave fuerte | En prod, **sin clave** ⇒ los endpoints de datos devuelven 503 (fail-closed). `/health` sigue abierto. |
| `CARDEEP_LEASE_TTL_MIN` | ambos schedulers | `6` (default) | TTL de lease-stale = 3× el heartbeat (2 min). |
| `CARDEEP_CORS_ORIGINS` | API (`main.py:114`) | `https://tu-frontend` | Opcional; default apunta a Vite local. |

> Con `CARDEEP_ENV=prod`, `config_guard.assert_safe_dsn` **rechaza** cualquier DSN que aún
> lleve la credencial de dev `cardeep_dev_only` (o `localhost`/`127.0.0.1`), con
> `RuntimeError`. Verifica el DSN de prod **antes** de poner `CARDEEP_ENV=prod`: si tu
> Postgres legítimo de prod viviera en `localhost` (p. ej. socket local), eso dispararía un
> falso positivo — usa la IP/host real o un nombre DNS, no `localhost`.

Estos valores van en un **EnvironmentFile** fuera del repo. En Linux:
`/etc/cardeep/cardeep.env` (modo `0600`, owner `cardeep`). **Nunca** commitees un `.env` real.

```ini
# /etc/cardeep/cardeep.env  — chmod 0600, NO en el repo
CARDEEP_ENV=prod
CARDEEP_DSN=postgres://cardeep:REAL_STRONG_PASS@10.0.0.5:5432/cardeep
CARDEEP_DB_URL=postgresql+psycopg2://cardeep:REAL_STRONG_PASS@10.0.0.5:5432/cardeep
CARDEEP_ASYNCPG_DSN=postgresql://cardeep:REAL_STRONG_PASS@10.0.0.5:5432/cardeep
CARDEEP_DSN_KW=host=10.0.0.5 port=5432 dbname=cardeep user=cardeep password=REAL_STRONG_PASS
CARDEEP_API_KEY=GENERA_UNA_CLAVE_FUERTE
CARDEEP_LEASE_TTL_MIN=6
```

> Para el harvest, `CARDEEP_DSN` debe ir en **forma keyword** (`host=… password=…`), porque
> `scheduler.py:62` lo pasa a `psycopg2.connect`. El API y el pipeline esperan la **URL**
> `postgres://…`. Son dos formas del mismo destino; mantenlas consistentes. Si te resulta
> ambiguo compartir un único `CARDEEP_DSN`, usa EnvironmentFiles separados por unit.

---

## 2. Linux VPS — systemd (target final)

Las units están en el repo: `ops/systemd/cardeep-api.service`, `cardeep-harvest.service`,
`cardeep-discovery.service`. Asumen `WorkingDirectory=/opt/cardeep`, venv en
`/opt/cardeep/.venv`, usuario de servicio `cardeep`. Ajusta las rutas a tu layout.

### 2.1 Pre-requisitos en el host

```bash
# Usuario de servicio sin login y árbol del repo
sudo useradd --system --home /opt/cardeep --shell /usr/sbin/nologin cardeep
sudo git clone https://github.com/sublimine/Cardeep.git /opt/cardeep
sudo chown -R cardeep:cardeep /opt/cardeep

# venv + deps de runtime (NO las de dev en prod)
sudo -u cardeep python3 -m venv /opt/cardeep/.venv
sudo -u cardeep /opt/cardeep/.venv/bin/pip install -r /opt/cardeep/requirements.txt

# Esquema al día — INCLUYE la 0054 (scheduler_lease) que habilita el heartbeat/TTL.
# migrate.py lee CARDEEP_DSN; es operator-run, no un servicio, así que se ejecuta a mano:
sudo -u cardeep CARDEEP_DSN="postgres://cardeep:REAL_STRONG_PASS@10.0.0.5:5432/cardeep" \
  /opt/cardeep/.venv/bin/python -m scripts.migrate up
sudo -u cardeep CARDEEP_DSN="…" /opt/cardeep/.venv/bin/python -m scripts.migrate status
```

> El EnvironmentFile lo consumen los **servicios**. `migrate.py` no es un servicio
> (`scripts/migrate.py:9` lo documenta como operator-run), así que para él pasas el DSN
> inline o haces `set -a; . /etc/cardeep/cardeep.env; set +a` en una shell de operador.

### 2.2 EnvironmentFile

```bash
sudo install -d -m 0750 -o root -g cardeep /etc/cardeep
sudo install -m 0640 -o root -g cardeep /dev/null /etc/cardeep/cardeep.env
sudoedit /etc/cardeep/cardeep.env      # pega el bloque de §1
```

### 2.3 Instalar y habilitar las units

```bash
sudo install -m 0644 /opt/cardeep/ops/systemd/cardeep-api.service       /etc/systemd/system/
sudo install -m 0644 /opt/cardeep/ops/systemd/cardeep-harvest.service   /etc/systemd/system/
sudo install -m 0644 /opt/cardeep/ops/systemd/cardeep-discovery.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable --now cardeep-api.service
sudo systemctl enable --now cardeep-harvest.service
sudo systemctl enable --now cardeep-discovery.service
```

### 2.4 Verificar

```bash
systemctl status cardeep-api cardeep-harvest cardeep-discovery
journalctl -u cardeep-harvest -f          # log del scheduler en vivo

# El /health es UNAUTENTICADO (main.py:34, deps.py:26 — require_api_key NO se aplica),
# así que la sonda pasa aunque CARDEEP_API_KEY sea obligatorio para los datos:
curl -fsS http://127.0.0.1:8090/health

# Confirma que el harvest tomó SU lock singleton (un solo productor):
journalctl -u cardeep-harvest | grep "Acquired singleton scheduler advisory lock"
```

> Un log `another cardeep scheduler already holds the singleton advisory lock` al arrancar
> NO es un bug: es la garantía single-producer actuando. Significa que ya hay un harvest
> vivo (o un holder muerto cuyo backend Postgres aún no fue recolectado — ver §4).

### 2.5 Por qué cada unit es como es (decisiones, no copia-pega)

- `Type=simple` en los tres: ninguno hace fork ni `sd_notify`; uvicorn y `BlockingScheduler`
  bloquean en primer plano.
- `Restart=always` + `RestartSec=10`: auto-recupera crash/OOM. Seguro porque los locks
  impiden doble producción (§0).
- `KillSignal=SIGTERM` + `TimeoutStopSec=30` en harvest/discovery: SIGTERM hace que el
  `BlockingScheduler` salga limpio y **libere** el advisory lock, así un `restart` normal no
  deja huérfano el lock.
- `EnvironmentFile=/etc/cardeep/cardeep.env`: lleva `CARDEEP_ENV=prod` + DSNs reales +
  `CARDEEP_API_KEY`, de modo que los guards (`config_guard.assert_safe_dsn`, `require_api_key`)
  quedan satisfechos en boot. Si el path está mal o falta `CARDEEP_ENV`, los daemons corren
  en modo **dev** (guards no-op) — los propios guards fallan ruidosamente en cuanto se pone
  `CARDEEP_ENV=prod`.
- API `--host 0.0.0.0` (no `127.0.0.1` del dev): en prod va detrás de proxy/firewall. Mantén
  el host firewalleado y termina TLS en el proxy; el API habla HTTP plano.
- Hardening (`NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=full`, `ProtectHome`): defaults
  seguros; relájalos solo si una feature lo necesita.

### 2.6 Watchdog opcional (readiness real del API)

uvicorn no hace `sd_notify`, así que `Type=notify` no aplica directo. Si quieres una puerta
de readiness dura, añade una unit oneshot que sondee `/health` tras el arranque:

```ini
# /etc/systemd/system/cardeep-api-ready.service  (oneshot, opcional)
[Unit]
After=cardeep-api.service
Requires=cardeep-api.service
[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for i in $(seq 1 30); do curl -fsS http://127.0.0.1:8090/health && exit 0; sleep 2; done; exit 1'
[Install]
WantedBy=multi-user.target
```

---

## 3. Host actual Windows 11 — Task Scheduler / NSSM

El host de desarrollo es **Windows 11** (verificado: `env Windows 11`). Aquí systemd no
existe; las dos rutas supervisadas son **NSSM** (recomendado, reinicio nativo) y el
**Programador de tareas** nativo (sin instalar nada). En PowerShell.

> Antes de cualquiera de las dos: exporta las mismas variables de §1. En Windows, NSSM y
> Task Scheduler reciben el entorno como pares `NOMBRE=valor`. En dev local puedes dejar
> `CARDEEP_ENV` sin poner (= `dev`) y el sistema corre igual que hoy.

### 3.1 Opción A — NSSM (recomendado)

NSSM convierte cada daemon en un servicio Windows con reinicio automático. Descarga
`nssm.exe` (https://nssm.cc) y, como Administrador:

```powershell
# Rutas (ajusta a tu máquina)
$PY   = "C:\Users\elias\projects\cardeep\.venv\Scripts\python.exe"
$UVI  = "C:\Users\elias\projects\cardeep\.venv\Scripts\uvicorn.exe"
$ROOT = "C:\Users\elias\projects\cardeep"

# --- API ---
nssm install cardeep-api $UVI "services.api.main:app --host 127.0.0.1 --port 8090"
nssm set cardeep-api AppDirectory $ROOT
nssm set cardeep-api AppExit Default Restart
nssm set cardeep-api AppEnvironmentExtra "CARDEEP_ENV=prod" "CARDEEP_DSN=postgres://cardeep:REAL@HOST:5433/cardeep" "CARDEEP_API_KEY=CLAVE_FUERTE"
nssm set cardeep-api AppStdout "$ROOT\.runlogs\nssm-api.out.log"
nssm set cardeep-api AppStderr "$ROOT\.runlogs\nssm-api.err.log"

# --- HARVEST (recuerda: CARDEEP_DSN en forma KEYWORD para psycopg2) ---
nssm install cardeep-harvest $PY "-m pipeline.ops.scheduler"
nssm set cardeep-harvest AppDirectory $ROOT
nssm set cardeep-harvest AppExit Default Restart
nssm set cardeep-harvest AppEnvironmentExtra "CARDEEP_ENV=prod" "CARDEEP_DB_URL=postgresql+psycopg2://cardeep:REAL@HOST:5433/cardeep" "CARDEEP_DSN=host=HOST port=5433 dbname=cardeep user=cardeep password=REAL" "CARDEEP_ASYNCPG_DSN=postgresql://cardeep:REAL@HOST:5433/cardeep"

# --- DISCOVERY ---
nssm install cardeep-discovery $PY "-m pipeline.discover_schedule --serve"
nssm set cardeep-discovery AppDirectory $ROOT
nssm set cardeep-discovery AppExit Default Restart
nssm set cardeep-discovery AppEnvironmentExtra "CARDEEP_ENV=prod" "CARDEEP_ASYNCPG_DSN=postgresql://cardeep:REAL@HOST:5433/cardeep" "CARDEEP_DSN_KW=host=HOST port=5433 dbname=cardeep user=cardeep password=REAL"

# Arrancar los tres
nssm start cardeep-api
nssm start cardeep-harvest
nssm start cardeep-discovery
```

`AppExit Default Restart` = el equivalente Windows de `Restart=always`. NSSM además aplica un
backoff de reinicio configurable (`AppThrottle`, `AppRestartDelay`). Verificar:

```powershell
nssm status cardeep-harvest
Get-Content "$ROOT\.runlogs\nssm-api.err.log" -Tail 30
Invoke-WebRequest http://127.0.0.1:8090/health -UseBasicParsing   # 200 OK = vivo
```

Para quitar un servicio: `nssm stop cardeep-harvest; nssm remove cardeep-harvest confirm`.

### 3.2 Opción B — Programador de tareas nativo (sin instalar nada)

Una tarea por daemon, arranque en boot como SYSTEM, con reinicio ante fallo. El entorno se
inyecta envolviendo el comando en un `cmd /c set …`:

```powershell
$ROOT = "C:\Users\elias\projects\cardeep"
$PY   = "$ROOT\.venv\Scripts\python.exe"

# HARVEST como ejemplo (replica para api y discovery cambiando el ExecStart y las env)
$cmd = "cmd /c `"set CARDEEP_ENV=prod&& set CARDEEP_DB_URL=postgresql+psycopg2://cardeep:REAL@HOST:5433/cardeep&& set CARDEEP_DSN=host=HOST port=5433 dbname=cardeep user=cardeep password=REAL&& set CARDEEP_ASYNCPG_DSN=postgresql://cardeep:REAL@HOST:5433/cardeep&& cd /d $ROOT&& $PY -m pipeline.ops.scheduler`""

schtasks /Create /TN "cardeep-harvest" /TR $cmd /SC ONSTART /RU SYSTEM /RL HIGHEST /F
```

El reinicio ante fallo del Programador de tareas se configura mejor por XML / la GUI
(pestaña *Settings* → "If the task fails, restart every: 1 minute, up to 3 attempts" y
"If the running task does not end… restart"), porque `schtasks /Create` no expone esos
flags de reintento directamente. Para producción de verdad en Windows, **NSSM es la ruta
recomendada** por su reinicio nativo robusto.

> El single-instance lo sigue garantizando el advisory lock en PG (§0), no Windows: si por
> error arrancas la tarea Y el servicio NSSM del mismo daemon, el segundo hace `SystemExit`
> y se apaga solo. No hay riesgo de doble producción.

---

## 4. Semántica de Lease TTL (distinguir holder muerto de holder sano)

El advisory lock es el **mutex duro**; nunca se hace `pg_advisory_unlock` del lock de otra
sesión (cross-session = inseguro). El problema operativo: si un holder muere **en duro**, su
lock de sesión persiste hasta que Postgres recolecta el backend, y durante esa ventana un
reinicio no puede arrancar. Para hacerlo **observable** se añadió (migración `0054`):

- Tabla `scheduler_lease(lock_key, holder, pid, started_at, last_heartbeat)`.
- Un job interval (~2 min) en cada scheduler que hace `UPSERT last_heartbeat=now()` sobre la
  **misma** conexión autocommit que ya sostiene el lock (€0, sin conexión nueva).
- Antes de intentar el `pg_try_advisory_lock`, si el lock está tomado, se lee el lease: si
  `now() - last_heartbeat > TTL` (`TTL = 3× heartbeat`, env `CARDEEP_LEASE_TTL_MIN`, default
  6 min), se loguea `CRITICAL "stale lease detected, prior holder presumed dead"` y se
  reintenta el lock.

Diagnóstico de operador:

```sql
-- Estado de los leases de los schedulers (1128354372 harvest, 1128354373 discovery)
SELECT lock_key, holder, pid, started_at, last_heartbeat,
       now() - last_heartbeat AS staleness
FROM scheduler_lease
ORDER BY lock_key;
```

| Lectura | Significado | Acción |
|---|---|---|
| `staleness` < 2 min | holder **sano**, latiendo | nada |
| `staleness` > TTL (6 min) | holder presuntamente **muerto** (crash duro) | el reinicio retomará el lock cuando Postgres recolecte la sesión; observa el log `stale lease detected` |
| sin fila para el lock_key | nadie corre, o DB sin la `0054` aplicada | arranca el daemon; si la tabla falta, aplica la migración (ver abajo) |

> **El lease es best-effort y NO reemplaza el lock.** No toma el control instantáneamente:
> la "auto-liberación" real es *observable + reintento en el próximo arranque*, no un takeover
> inmediato. El código de heartbeat va envuelto en `try/except`, así que una DB **sin la 0054
> aplicada** arranca igual (comportamiento idéntico, lease inerte) logueando un warning. Si ves
> ese warning, la feature de TTL está INERTE hasta aplicar la migración:
>
> ```bash
> CARDEEP_DSN="postgres://cardeep:REAL@HOST:5432/cardeep" python -m scripts.migrate up
> ```

---

## 5. Operar los servicios (cheatsheet)

| Acción | Linux (systemd) | Windows (NSSM) |
|---|---|---|
| Estado | `systemctl status cardeep-harvest` | `nssm status cardeep-harvest` |
| Log en vivo | `journalctl -u cardeep-harvest -f` | `Get-Content .runlogs\nssm-*.log -Wait` |
| Reiniciar | `systemctl restart cardeep-harvest` | `nssm restart cardeep-harvest` |
| Parar | `systemctl stop cardeep-harvest` | `nssm stop cardeep-harvest` |
| Liveness API | `curl -fsS http://127.0.0.1:8090/health` | `iwr http://127.0.0.1:8090/health` |
| ¿Single-producer? | `journalctl -u cardeep-harvest \| grep "Acquired singleton"` | revisa el `.err.log` |
| Fuentes calladas | `python -m pipeline.ops.scheduler --check-silence` (read-only) | igual |

Para el día a día (salud de fuentes, breakers, alertas, delta), el runbook operativo es
[runbook/OPERATE.md](runbook/OPERATE.md). Este doc solo cubre **mantener los daemons vivos**.

---

## 6. Riesgos y avisos (no sobre-prometer)

- **El TTL no es takeover instantáneo.** Un holder muerto en duro retiene el lock de sesión
  hasta que Postgres recolecta el backend (keepalive/idle del servidor). El lease solo lo hace
  **observable**; no forzamos unlock cross-session (sería inseguro). "Auto-release" = observable
  + reintento, no toma inmediata.
- **`CARDEEP_API_KEY` ausente en prod = 503 en TODOS los endpoints de datos** (incluido
  `/stats`). Es fail-closed intencional. `/health` sigue abierto para que las sondas de
  liveness pasen. Si el API devuelve 503 tras poner `CARDEEP_ENV=prod`, casi seguro falta la
  clave.
- **`localhost` en el DSN de prod dispara el fail-fast.** Si tu Postgres real vive en
  `localhost` (socket/proxy local), usa el host/IP real para no chocar con el guard, o revisa
  el guard antes de flipear `CARDEEP_ENV=prod`.
- **Units/tareas mal configuradas corren en modo dev silenciosamente.** Si el EnvironmentFile
  no carga o falta `CARDEEP_ENV=prod`, los guards quedan no-op. Mitigación: las units fijan
  `EnvironmentFile=/etc/cardeep/cardeep.env`; los guards fallan ruidosamente en cuanto
  `CARDEEP_ENV=prod` está presente.
- **La 0054 debe aplicarse para que el heartbeat/TTL escriba.** Sin ella el código arranca
  igual (try/except), pero la feature de TTL está inerte y se loguea un warning. No asumas
  TTL activo sin haber corrido `migrate.py up`.
- **Instalar cualquier unit/tarea es un paso de OWNER que toca el host.** Los ficheros del repo
  (`ops/systemd/*.service`, este doc) son inertes y reversibles hasta que se instalan.

---

## Ver también

- [runbook/DEPLOY.md](runbook/DEPLOY.md) — cold-start A→Z a mano (clone → DB → venv → migrate → API + scheduler).
- [runbook/OPERATE.md](runbook/OPERATE.md) — operar el día a día (salud, breakers, alertas, delta).
- `ops/systemd/*.service` — las units inertes referenciadas aquí.
- `.env.example` — referencia de variables (defaults de dev).
- `migrations/0054_scheduler_heartbeat.sql` — tabla `scheduler_lease` (heartbeat/TTL).
