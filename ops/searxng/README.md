# €0 SearXNG self-host — ungate discovery VECTOR 3 (`dork_municipal`)

A local, account-less SearXNG meta-search instance that lets the discovery
scheduler **auto-run** `dork_municipal` — the only vector that systematically
sweeps every Spanish municipality for dealer-**owned** domains that no
marketplace indexes.

> **Live coverage gap this closes** (queried `postgres://…@127.0.0.1:5433/cardeep`,
> 2026-06-23): `geo_municipality` = **8,132** municipalities, of which **2,632**
> have **0** entities. `dork_municipal` is the lever that reaches them.

---

## Why a SearXNG endpoint is required

`pipeline/sources/dork_municipal.py` fires 5 automotive search templates per
municipality (`_TEMPLATES`, dork_municipal.py:35-41). Its engine selection
(`_pick_engine`, dork_municipal.py:153-173) is:

1. If `CARDEEP_SEARXNG_URL` is set **and reachable** → use SearXNG JSON
   (`_search_searxng`, dork_municipal.py:109-119), calling
   `GET {base}/search?q=…&format=json&language=es-ES&safesearch=0`.
2. Otherwise → fall back to scraping **DuckDuckGo HTML** directly
   (`_search_ddg`, dork_municipal.py:122-139).

The DDG fallback is fine for a tiny manual probe, but an unbounded national
sweep (8,132 municipios × 5 templates ≈ **40k** direct requests) hammers DDG and
risks a ban. That is exactly why the discovery daemon **gates** auto-running this
vector behind `CARDEEP_SEARXNG_URL`:

```python
# pipeline/discover_schedule.py:77-83
"dork_municipal": DiscoveryJob(
    "dork_municipal", "dork_municipal", cadence_hours=2160, orthogonal=True,
    env={k: os.environ[k] for k in ("CARDEEP_SEARXNG_URL",) if k in os.environ},
    requires_env=("CARDEEP_SEARXNG_URL",)),   # GATE: no auto-run without SearXNG
```

`_gated()` (discover_schedule.py:120-130) refuses the AUTO tick unless the var is
present. SearXNG fronts and **rotates** the upstream engines, so the rate
pressure lands on the meta-search, not directly on Google/Bing/DDG — that is what
makes an automated sweep ban-safe.

**No application code changes are needed.** The adapter already speaks SearXNG
JSON natively. The only missing pieces are: a running instance + the env var.

---

## 1. Generate `settings.yml` (one-time)

A **default** SearXNG enables only the `html` output format and replies
**HTTP 403** to `?format=json` — which would silently knock the adapter back onto
the gated DDG fallback. Two settings make the JSON API usable by an automated
local consumer:

- `search.formats` must include **`json`** (default is `[html]` only).
- `server.limiter` must be **`false`** — the limiter blocks "bot-like"
  User-Agents and JSON requests. This is safe here because the instance is bound
  to `127.0.0.1` only and is consumed by exactly one local process.

Create `ops/searxng/settings.yml` (sits next to this file; the compose mounts the
directory at `/etc/searxng`):

```yaml
# ops/searxng/settings.yml — Cardeep local meta-search for dork_municipal.
# Localhost-only, single-consumer (the discover pipeline). NEVER expose publicly.
use_default_settings: true

server:
  bind_address: "0.0.0.0"        # inside the container; host-published only on 127.0.0.1:8888
  secret_key: "${SEARXNG_SECRET}" # injected at launch — never commit a real key
  limiter: false                  # local single-consumer → no bot/rate gate on the JSON API
  image_proxy: false

search:
  safe_search: 0
  formats:
    - html
    - json                        # REQUIRED: the adapter calls ?format=json (dork_municipal.py:114)
  default_lang: "es-ES"

ui:
  static_use_hash: true
```

> The image substitutes `${SEARXNG_SECRET}` from the container environment, which
> the compose file passes through from your shell.

---

## 2. Run the instance

From the repo root, inject a throwaway secret and bring it up (Git Bash / sh):

```bash
SEARXNG_SECRET=$(openssl rand -hex 32) \
  docker compose -f ops/searxng/docker-compose.searxng.yml up -d
```

PowerShell:

```powershell
$env:SEARXNG_SECRET = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
docker compose -f ops/searxng/docker-compose.searxng.yml up -d
```

Wait for the container to report **healthy** — the healthcheck specifically pings
the JSON API, so an unhealthy container means JSON is still 403 (re-check
`settings.yml`):

```bash
docker ps --filter name=cardeep-searxng
```

### Verify the JSON API the adapter depends on

```bash
curl -s 'http://127.0.0.1:8888/search?q=concesionario+coches+madrid&format=json' \
  | head -c 400
```

A JSON object with a `"results"` array = success. An HTML page or `403` = JSON
format is not enabled (fix `search.formats` in `settings.yml`, then
`docker compose -f ops/searxng/docker-compose.searxng.yml restart`).

---

## 3. Wire `CARDEEP_SEARXNG_URL` and ungate

The discovery daemon copies its own environment into the child process
(discover_schedule.py:166-167), so the env var must be present **in the daemon's
environment**.

```bash
export CARDEEP_SEARXNG_URL=http://127.0.0.1:8888
```

With it set, `_gated()` returns `None` (discover_schedule.py:120-130) and
`dork_municipal` becomes eligible for AUTO-run at its quarterly cadence
(`cadence_hours=2160`, discover_schedule.py:78). Confirm the gate cleared:

```bash
python -m pipeline.discover_schedule --dry-run
# the dork_municipal row should no longer show [GATE] / "GATED:needs CARDEEP_SEARXNG_URL"
```

> The discovery daemon is a **separate** producer from the harvest scheduler and
> holds its own advisory lock (`0x43415244 + 1`, discover_schedule.py:50). The
> ungate is inert unless that daemon (`python -m pipeline.discover_schedule
> --serve`) is actually running on the host.

---

## 4. Bounded, robots-respecting sweep (do NOT flood)

The whole point of the gate is to avoid a 40k-request flood. **Keep it bounded**
even with SearXNG fronting the engines. The adapter already honors these env
knobs — drive the sweep through them rather than unleashing all 8,132 at once:

| Env var | Default | File:line | Use |
|---|---|---|---|
| `CARDEEP_DORK_DELAY` | `1.0` (s/req) | dork_municipal.py:191 | Keep **≥ 1.0** — Nominatim-grade politeness; throttles how fast SearXNG itself is queried. |
| `CARDEEP_DORK_MAX_HITS_PER_QUERY` | `8` | dork_municipal.py:192 | Result cap per query. |
| `CARDEEP_DORK_LIMIT` | unset = full 8,132 | dork_municipal.py:184, 101-104 | Cap municipalities per run → a **verify-then-delete slice** (e.g. `500`). |
| `CARDEEP_DORK_MUNI` | unset | dork_municipal.py:185-186, 96-99 | Comma list of municipality **names** → target the zero-coverage set first. |

### Prioritize the 2,632 zero-coverage municipalities first

That set carries the highest marginal coverage. Pull the names and feed them in
name-batches via `CARDEEP_DORK_MUNI`:

```bash
python - <<'PY'
import asyncio, asyncpg
DSN = "postgres://cardeep:cardeep_dev_only@127.0.0.1:5433/cardeep"
async def main():
    c = await asyncpg.connect(DSN)
    try:
        rows = await c.fetch("""
            SELECT g.name FROM geo_municipality g
            WHERE NOT EXISTS (SELECT 1 FROM entity e WHERE e.municipality_code = g.code)
            ORDER BY g.code LIMIT 200""")
        print(",".join(r["name"] for r in rows))
    finally:
        await c.close()
asyncio.run(main())
PY
```

Then run a bounded, explicit slice (an explicit `--once <vector>` is operator
intent and bypasses the gate, discover_schedule.py:194-198 — but with SearXNG up
you are no longer hitting DDG):

```bash
CARDEEP_SEARXNG_URL=http://127.0.0.1:8888 \
CARDEEP_DORK_DELAY=1.0 \
CARDEEP_DORK_MUNI="<comma,separated,names,from,above>" \
  python -m pipeline.discover_schedule --once dork_municipal
```

Or a deterministic code-ordered slice without naming municipalities:

```bash
CARDEEP_SEARXNG_URL=http://127.0.0.1:8888 \
CARDEEP_DORK_DELAY=1.0 CARDEEP_DORK_LIMIT=500 \
  python -m pipeline.discover dork_municipal
```

Each slice geo-resolves hits to INE codes, mints a `cdp_code`, and upserts
idempotently (`pipeline/discover.py:77-114`); re-runs do not duplicate. The
adapter's `_BLOCK_SUBSTR` filter (dork_municipal.py:45-55) drops marketplaces,
directories, and socials so only candidate dealer-**owned** domains become
entities.

**Robots / rate posture:** the per-request `CARDEEP_DORK_DELAY ≥ 1.0` keeps
SearXNG itself queried politely; SearXNG rotates the upstream engines so no single
provider is hammered; bounded slices mean each scheduled tick is a small
verify-then-delete batch, never the full 40k flood the gate exists to prevent.
Do not lower the delay below 1.0 s and do not remove the gate's intent (no
unbounded auto-sweep).

---

## 5. Stop / tear down

```bash
docker compose -f ops/searxng/docker-compose.searxng.yml down
```

This stops and removes only the `cardeep-searxng` container. No volumes are
created, so nothing persists beyond `settings.yml` in this directory.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Container **unhealthy** | JSON API returns 403 | Add `json` to `search.formats` in `settings.yml`, then `restart`. |
| `--dry-run` still shows `[GATE]` on `dork_municipal` | `CARDEEP_SEARXNG_URL` not in the daemon env | `export CARDEEP_SEARXNG_URL=http://127.0.0.1:8888` in the daemon's shell/service. |
| Adapter logs `engine=ddg` | SearXNG not reachable at probe time (dork_municipal.py:159-163) | Confirm container is up and the curl JSON check (step 2) succeeds. |
| `compose up` errors on `SEARXNG_SECRET` | secret not exported | Inject `SEARXNG_SECRET=$(openssl rand -hex 32)` on the `up` command. |
