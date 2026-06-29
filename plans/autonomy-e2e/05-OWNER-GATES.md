# Autonomy E2E — 5.1 · Dossier de gates PENDIENTE-OWNER (la frontera honesta)

> Qué corre solo y qué espera tu firma. Los gates **PARQUEAN, no detienen** (`gates.py`,
> `aparca-no-detiene`): el loop sigue, marca el ítem PENDIENTE-OWNER (consultable, 1.2) y continúa.

## LO QUE YA CORRE SOLO (construido + verificado en este proyecto)
- **Cerebro** (Punto 1): el loop de campaña ensamblado — `health_rollup` (SUPERVISA completo), gates
  consultables, ES `SEALED` en `:5433`.
- **Latido** (Punto 2): `scheduler` (APScheduler daemon, `heartbeat_tick` con circuit-breaker) +
  `lock_heartbeat` (single-producer) + `silence_watchdog` — 125 tests verdes.
- **Cuerpo** (Punto 3): `docker compose up -d` levanta pg → api (:8090) + autopilot (daemon),
  restart-unless-stopped, healthchecks. Imagen `cardeep-app` verificada.
- **Sentidos** (Punto 4): Ollama (`qwen2.5:7b`, env-config) + egress €0 (3194 free-proxies) + 56
  fuentes ES en `source_health`.
- **Invariantes mecánicos** (13/10): `vam_verified` + country-proof (entity+vehicle) vivos en `:5433`.

## LOS GATES QUE ESPERAN TU FIRMA
| Gate | Qué parquea | Cómo lo desbloqueas |
|------|-------------|---------------------|
| **HARVEST-PROD** | Arrancar la cosecha REAL: el daemon `autopilot` sin `--dry-run` lanza harvests contra las 56 fuentes (egress + carga real). Es el acto de **empezar a producir datos en vivo**. | `docker compose up -d autopilot`. Conservador primero: `docker compose run --rm autopilot python -m pipeline.ops.scheduler --dry-run` (ver qué cosecharía sin tocar nada). |
| **LEGAL / ToS** | Cosechar un país nuevo o una fuente cuyo ToS no esté firmado. El loop parquea en BOOTSTRAPPED. | Firmar el dossier legal del país/fuente → `CampaignAction.legal_cleared`. ES (incumbente) ya opera. |
| **GASTO (€>0)** | Rutas de pago (proxies premium, APIs de pago). €0 (free-proxies) está **OPEN** por defecto. | `export CARDEEP_BUDGET_AUTHORIZED=1` (`gates.BUDGET_ENV`) para la ruta concreta. |
| **PROD cutover** | Migraciones/triggers de serving-of-record. | **YA HECHO** (0070-0072 + ES SEALED aplicados a `:5433`, con backup + rollback). |

## CÓMO VER QUÉ ESTÁ PARQUEADO (consultable, 1.2)
```python
# {country_code: [gate, ...]} para cada campaña bloqueada PENDIENTE-OWNER
from pipeline.autopilot.state import pending_owner_gates  # async over an asyncpg conn
```
⇒ El sistema **no se detiene** en ningún gate: produce hasta la frontera, te dice exactamente qué
falta (consultable), y sigue con lo que sí puede. Encender la cosecha real es **un comando tuyo**.
