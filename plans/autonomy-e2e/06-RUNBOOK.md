# Autonomy E2E — 5.2 · Runbook: operar el sistema autónomo

> Arrancar, observar, parar y revertir Cardeep corriendo solo. Prerequisitos: Docker + el volumen
> `cardeep_pg_data` (prod) o uno limpio. Ollama corre en el HOST (`ollama serve`, modelo `qwen2.5:7b`).

## ARRANCAR (un comando)
```bash
ollama serve &                     # el host expone Ollama en :11434 (el daemon lo alcanza via host.docker.internal)
docker compose up -d               # pg (healthy) -> api (:8090) + autopilot (scheduler daemon)
```
- `api` sirve el censo en `http://127.0.0.1:8090` (FastAPI). `autopilot` es el latido (APScheduler
  `heartbeat_tick` cada 15 min: due-sources → harvest, single-producer via `scheduler_lease`).
- Ambos `restart: unless-stopped` → "Cardeep no se cae". Arranque ordenado por el healthcheck de pg.

### Arranque conservador (ver sin cosechar)
```bash
docker compose run --rm autopilot python -m pipeline.ops.scheduler --dry-run      # qué cosecharía
docker compose run --rm autopilot python -m pipeline.ops.scheduler --check-silence # fuentes silenciosas
```

## OBSERVAR
```bash
docker compose ps                                  # estado + health de los 3 servicios
curl -s http://127.0.0.1:8090/health               # api viva
docker compose logs -f autopilot                   # el latido en vivo
docker compose logs -f api
```
```sql
-- salud por país (el SUPERVISA completo, 1.1) y la frontera owner (1.2):
SELECT country_code, state, detail->'pending_owner_gates' FROM country_campaign;
SELECT count(*) FROM v_country_proof_violations;   -- DEBE ser 0 (invariante mecánico vivo)
SELECT count(*) FILTER (WHERE status='healthy'), count(*) FROM source_health WHERE country_code='ES';
```

## PARAR
```bash
docker compose stop                # detiene servicios, conserva contenedores + datos
docker compose down                # quita contenedores; el volumen cardeep_pg_data PERSISTE (datos a salvo)
```

## ROLLBACK / SEGURIDAD
- **Apagar solo la cosecha** (mantener la API sirviendo): `docker compose stop autopilot`.
- **Revertir los invariantes mecánicos** (si hiciera falta): ver `scripts/cutover_road13.sh` (rollback
  de una línea: DROP TRIGGER ×3 — additive/reversible).
- **Backup antes de cualquier cambio de esquema en prod**: el patrón está en `cutover_road13.sh`
  (`pg_dump` de las tablas afectadas → `.sql` con timestamp).
- El volumen `cardeep_pg_data` es la fuente de verdad; nunca se borra en `down` (sin `-v`).

## QUÉ FALTA PARA "100% AUTÓNOMO EN PROD"
Ver `05-OWNER-GATES.md`: encender `autopilot` contra `:5433` = el acto owner que arranca la cosecha
real. Todo lo demás (cerebro/latido/cuerpo/sentidos) está construido, verificado y pusheado.
