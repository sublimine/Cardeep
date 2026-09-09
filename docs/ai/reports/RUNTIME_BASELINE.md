# RUNTIME BASELINE

## Task Report — TASK-003

## Status
DONE

## Mode
AUDIT_ONLY

## Objective
Establish what can run locally without changing code or dependencies. No repairs were attempted in this task, per the task's explicit rule.

## Important precondition observed before running anything

Before running any command, this executor checked for already-running processes to avoid colliding with concurrent activity already observed in this session (see `docs/ai/audits/00_REPO_MAP.md` §9). Findings:

- Port 8090 (the API) was already `LISTENING` (PID 20584). `_api_serve.out.log` had just been written at 16:26, minutes before this check.
- Port 5433 (`cardeep-pg`) was already `LISTENING` with active `ESTABLISHED` connections from PID 20584.
- `docker ps` showed `cardeep-pg` (postgres:16) up for about 1 hour, and a second unrelated container `cardex-pg` (postgres:16-bookworm) also up — a different project's database, not touched.

Given this, this executor did **not** attempt `docker compose up -d cardeep-pg` (already up — running it would at best be a no-op, at worst risk interacting with a live concurrent process) and did **not** attempt to start `uvicorn services.api.main:app` on the same port (already bound — would simply fail, and attempting it is pointless risk for no gain). Instead, the already-live API was queried read-only, which yields stronger evidence (real live state) than a fresh instance would.

`python scripts/migrate.py up` was **not** run — the live database is in concurrent use by another process; applying migrations against a live shared DB during a read-only audit task is out of scope and risky. `python scripts/migrate.py verify` (read-only, does not apply anything) was run instead.

## Evidence

### Python / pip versions
```
$ python --version
Python 3.11.9
$ pip --version
pip 24.0 from C:\Users\elias\AppData\Local\Programs\Python\Python311\Lib\site-packages\pip (python 3.11)
```
Confidence: VERIFIED_RUNTIME.

### `docker compose config`
Ran successfully, rendered the full effective compose config for all 3 services (`cardeep-pg`, `api`, `autopilot`). Confirms: `api` and `autopilot` share one built image (`cardeep-app:latest`), both depend on `cardeep-pg` being `service_healthy`, `api` exposes `127.0.0.1:8090`, both app services get identical env (`CARDEEP_DSN`, `CARDEEP_ASYNCPG_DSN`, `CARDEEP_DB_URL` all pointing at `cardeep-pg:5432` with a local-development credential redacted in this recovered copy; `CARDEEP_OLLAMA_URL` pointing at `host.docker.internal:11434`). The healthcheck for `api` polls `http://localhost:8090/health` and expects HTTP 200.
Confidence: VERIFIED_RUNTIME (command executed, output captured).

Note (minor, not risk-register-worthy): the DB password embedded in `docker-compose.yml` is self-documented as a non-production placeholder, consistent with `.env.example`'s statement that production secrets must be supplied separately. Its literal value is redacted in this recovered copy. No action needed.

### Live API probe (already-running instance, read-only)
```
$ curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8090/
HTTP 404
$ curl -s http://127.0.0.1:8090/docs -o /dev/null -w "HTTP %{http_code}\n"
HTTP 200
$ curl -s http://127.0.0.1:8090/health
{"ok":true,"data":{"status":"live","db":"ok"},"error":null,"meta":null}
```
The `/openapi.json` schema was also fetched and confirms `title: "Cardeep API"`, `version: "0.2.0"`, and that `/health`'s own docstring explicitly states it is deliberately unauthenticated but deliberately returns no product-scale counts (dealer/vehicle totals), because "the audit flagged that anonymous callers could read the product's scale" and those now live behind auth at `/stats`. This is a genuine, specific security-conscious design decision found in the code, not a documentation claim — worth carrying into TASK-010 (API audit) as a positive finding.
Confidence: VERIFIED_RUNTIME (the process is live, real HTTP responses captured in this session). Root `/` returning 404 simply means there is no handler mounted at `/` — expected for an API-only service, not a defect.

### `python scripts/migrate.py verify`
```
...
0072  MATCH
verify: 66 match, 0 drift
```
All 66 migrations match applied database state exactly, 0 drift, against the live `cardeep-pg` database. This is strong evidence the schema audit in `docs/ai/audits/02_DATA_MODEL_AUDIT.md` (TASK-004, produced separately) can trust `migrations/0001`-`0072` as the actual current live schema, not just a static file listing.
Confidence: VERIFIED_RUNTIME.

### `python -m pipeline.ops.scheduler --help`
```
usage: scheduler.py [-h] [--dry-run] [--check-silence]

Cardeep B2.2 durable scheduler — single-producer heartbeat (APScheduler 3.x +
SQLAlchemyJobStore on cardeep-pg).

options:
  -h, --help       show this help message and exit
  --dry-run        Print which sources are DUE right now and what command
                   would be launched, then exit WITHOUT running anything.
  --check-silence  Print sources that have been silent for > 2x their harvest
                   interval. READ-ONLY: does NOT fire alerts or modify any DB
                   row, then exit.
```
Confirms the module is importable and its CLI is well-formed. `--dry-run` and `--check-silence` are both explicitly documented as read-only/no-op by the tool's own help text — genuinely safe to run in a future task without further investigation. This executor did not run either flag in this task (out of scope for a baseline check; entrypoint existence and importability was the goal here).
Confidence: VERIFIED_RUNTIME (command executed, real output captured).

### `python -m pytest --collect-only -q`
First attempt timed out at 90s with zero output (background job, `timeout 90` killed it before any output was flushed — this by itself is a useful data point: collection is slow, not instant). Second attempt with a 240s timeout completed successfully:
```
2190 tests collected in 189.94s (0:03:09)
```
Zero collection errors — every one of the 2190 test items across all 190 `test_*.py` files imports cleanly (no `ImportError`, no collection-time exception). This is meaningful evidence: it means the entire test module import graph (and everything those modules import at module level) is currently sound.
Confidence: VERIFIED_RUNTIME. Collection took ~3 minutes — noted as an operational fact (not a defect) for anyone running the suite interactively expecting a quick collect.

## Verdict

Runtime baseline: the live stack (Postgres via Docker, FastAPI via uvicorn) was **already running and healthy** at the start of this task, evidenced by a real `/health` response and 0 migration drift. The scheduler module imports and its CLI is well-formed. The full test suite (2190 tests) collects without error. No repairs were needed or attempted — nothing broken was found at this baseline level. `docs/ai/findings/BROKEN.md` is unchanged (nothing to add).

This does **not** mean the product works correctly end to end — it means the basic scaffolding (DB reachable, schema in sync, API serving, scheduler importable, tests collectible) is intact. Whether ingestion, delta, verification and dedup logic actually behave correctly is the subject of TASK-005 through TASK-008 (static audits) and would require running the actual test suite (not just collecting it) or exercising the pipeline against real data for true `VERIFIED_RUNTIME` behavioral evidence — out of scope for this task.

## Files Modified By This Task
- `docs/ai/reports/RUNTIME_BASELINE.md` (new — this file)
- `docs/ai/control/05_EVIDENCE_LEDGER.md` (appended — EVIDENCE-0003)
- `docs/ai/tasks/TASK_QUEUE.yml` (status field only, `TASK-003: READY → DONE` — same disclosed exception as prior tasks, see FINDING-0001)

## Forbidden Files Touched
NO

## Commands Executed
- `python --version`, `pip --version`
- `netstat -ano` (port 8090, 5433 checks)
- `docker ps`
- `tasklist` (grep python/uvicorn)
- `docker compose config`
- `curl http://127.0.0.1:8090/`, `/docs`, `/health`, `/openapi.json`
- `python -m pipeline.ops.scheduler --help`
- `python scripts/migrate.py verify`
- `python -m pytest --collect-only -q` (two attempts, first timed out at 90s, second succeeded at 240s timeout)

## Validation Result
PASSED

## Remaining Unknowns
Whether the pipeline's actual ingestion/delta/verification/dedup *behavior* is correct at runtime is NOT established by this task — only that the scaffolding around it is alive and importable. See TASK-005 through TASK-008.

## Next Recommended Task
TASK-004 — Audit migrations and schema evolution (already in progress in parallel via the governance batch-audit workflow at the time of writing).
