# Obsidian Second-Brain Vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to
> implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Execution mode chosen: Inline** (not subagent-per-task). Rationale: this is one
> continuous sequential build against a single shared live vault (Obsidian app
> install → plugin files → shared `.obsidian/community-plugins.json` →
> `docs/second-brain/` content → git commit → app launch). There is no independent,
> parallelizable per-task unit of work here worth the overhead of a dedicated
> subagent per task, and several steps genuinely depend on the previous step's real
> output (e.g. can't enable a plugin before its files exist on disk).

**Goal:** Turn the Cardeep repo into a working Obsidian vault (second brain) with
Dataview, Templater, and an MCP bridge, plus a new additive `docs/second-brain/`
knowledge layer — fully wired and opened for the owner's live audit.

**Architecture:** Vault root = repo root. Three community plugins installed
headless (no in-app browser). New `docs/second-brain/` folder holds dashboards,
templates, and a Canvas system map, built on top of the existing `docs/`/`plans/`
corpus without reorganizing it. Spec: `docs/superpowers/specs/2026-07-13-obsidian-second-brain-vault-design.md`.

**Tech Stack:** Obsidian 1.12.7 (winget), Dataview 0.5.70, Templater 2.23.1,
obsidian-local-rest-api 4.1.7+, Claude Code MCP client.

---

### Task 1: Install Obsidian application

**Files:** none (system package install)

- [ ] **Step 1: Install via winget**

Run: `winget install --id Obsidian.Obsidian -e --accept-package-agreements --accept-source-agreements`

- [ ] **Step 2: Verify install**

Run: `winget list --id Obsidian.Obsidian`
Expected: a row showing `Obsidian.Obsidian` with a version (e.g. `1.12.7`).

---

### Task 2: Create vault skeleton with exclusions

**Files:**
- Create: `C:\Users\elias\projects\cardeep\.obsidian\app.json`

- [ ] **Step 1: Create `.obsidian/` directory**

Run: `mkdir -p "/c/Users/elias/projects/cardeep/.obsidian"`

- [ ] **Step 2: Write `app.json` with `userIgnoreFilters`**

```json
{
  "userIgnoreFilters": [
    "pipeline/",
    "services/",
    "web/",
    "portal/",
    "tests/",
    "migrations/",
    "scripts/",
    "scratch/",
    "data/",
    "countries/",
    "ops/",
    "state/",
    ".claude/",
    ".backups/",
    ".github/",
    ".hypothesis/",
    ".playwright-mcp/",
    ".pytest_cache/",
    ".runlogs/",
    ".wf/",
    "Dockerfile",
    "docker-compose.yml",
    "pytest.ini",
    "requirements.txt",
    "requirements-dev.txt",
    "scratch_mn_"
  ]
}
```

- [ ] **Step 3: Verify valid JSON**

Run: `python -c "import json; json.load(open(r'C:\Users\elias\projects\cardeep\.obsidian\app.json'))" && echo VALID`
Expected: `VALID`

---

### Task 3: Install Dataview headless

**Files:**
- Create: `.obsidian/plugins/dataview/main.js`
- Create: `.obsidian/plugins/dataview/manifest.json`
- Create: `.obsidian/plugins/dataview/styles.css`

- [ ] **Step 1: Create plugin folder**

Run: `mkdir -p "/c/Users/elias/projects/cardeep/.obsidian/plugins/dataview"`

- [ ] **Step 2: Download the three real release assets (tag 0.5.70)**

```bash
cd "/c/Users/elias/projects/cardeep/.obsidian/plugins/dataview"
curl -L -o main.js https://github.com/blacksmithgu/obsidian-dataview/releases/download/0.5.70/main.js
curl -L -o manifest.json https://github.com/blacksmithgu/obsidian-dataview/releases/download/0.5.70/manifest.json
curl -L -o styles.css https://github.com/blacksmithgu/obsidian-dataview/releases/download/0.5.70/styles.css
```

- [ ] **Step 3: Verify non-zero file sizes**

Run: `ls -la "/c/Users/elias/projects/cardeep/.obsidian/plugins/dataview"`
Expected: `main.js` ~2.3MB, `manifest.json` and `styles.css` non-zero.

---

### Task 4: Install Templater headless

**Files:**
- Create: `.obsidian/plugins/templater-obsidian/main.js`
- Create: `.obsidian/plugins/templater-obsidian/manifest.json`
- Create: `.obsidian/plugins/templater-obsidian/styles.css`

- [ ] **Step 1: Create plugin folder**

Run: `mkdir -p "/c/Users/elias/projects/cardeep/.obsidian/plugins/templater-obsidian"`

- [ ] **Step 2: Download the three real release assets (tag 2.23.1)**

```bash
cd "/c/Users/elias/projects/cardeep/.obsidian/plugins/templater-obsidian"
curl -L -o main.js https://github.com/SilentVoid13/Templater/releases/download/2.23.1/main.js
curl -L -o manifest.json https://github.com/SilentVoid13/Templater/releases/download/2.23.1/manifest.json
curl -L -o styles.css https://github.com/SilentVoid13/Templater/releases/download/2.23.1/styles.css
```

- [ ] **Step 3: Verify non-zero file sizes**

Run: `ls -la "/c/Users/elias/projects/cardeep/.obsidian/plugins/templater-obsidian"`
Expected: all three files present, non-zero size.

---

### Task 5: Install Local REST API with MCP headless

**Files:**
- Create: `.obsidian/plugins/obsidian-local-rest-api/main.js`
- Create: `.obsidian/plugins/obsidian-local-rest-api/manifest.json`
- Create: `.obsidian/plugins/obsidian-local-rest-api/styles.css` (if present in release)

- [ ] **Step 1: Create plugin folder**

Run: `mkdir -p "/c/Users/elias/projects/cardeep/.obsidian/plugins/obsidian-local-rest-api"`

- [ ] **Step 2: Resolve latest release tag, then download assets**

```bash
cd "/c/Users/elias/projects/cardeep/.obsidian/plugins/obsidian-local-rest-api"
curl -s https://api.github.com/repos/coddingtonbear/obsidian-local-rest-api/releases/latest > /tmp/rest-api-release.json
python -c "import json; r=json.load(open('/tmp/rest-api-release.json')); print(r['tag_name']); [print(a['browser_download_url']) for a in r['assets']]"
```
Expected: prints a tag `>= 4.1.7` and asset URLs for `main.js`/`manifest.json`
(and `styles.css` if it exists in that release).

- [ ] **Step 3: Download each printed asset URL into this folder with `curl -L -O`**

- [ ] **Step 4: Verify non-zero file sizes**

Run: `ls -la "/c/Users/elias/projects/cardeep/.obsidian/plugins/obsidian-local-rest-api"`

---

### Task 6: Enable all three plugins

**Files:**
- Create: `.obsidian/community-plugins.json`

- [ ] **Step 1: Write the enabled-plugins list**

```json
["dataview", "templater-obsidian", "obsidian-local-rest-api"]
```

- [ ] **Step 2: Verify valid JSON with exactly these 3 entries**

Run: `python -c "import json; d=json.load(open(r'C:\Users\elias\projects\cardeep\.obsidian\community-plugins.json')); assert d==['dataview','templater-obsidian','obsidian-local-rest-api']; print('OK')"`
Expected: `OK`

---

### Task 7: Build `docs/second-brain/dashboards/`

**Files:**
- Create: `docs/second-brain/dashboards/00-Home.md`
- Create: `docs/second-brain/dashboards/pendientes-owner-search.md`
- Create: `docs/second-brain/dashboards/planes-por-estado.md`

- [ ] **Step 1: Write `00-Home.md`**

```markdown
---
type: moc
tags: [second-brain]
---

# Cardeep — Home

## Arquitectura y motor
- [[docs/architecture/README|Architecture overview]]
- [[docs/architecture/SYSTEM-A-Z|System A-Z]]
- [[docs/architecture/13-API-AND-DELTA|API y delta]]
- [[docs/generic-engine-bible/00-MASTER|Generic Engine Bible — master]]
- [[docs/generic-engine-bible/COUNTRY-PROOF-BUILD|Country-proof build]]
- [[docs/generic-engine-bible/COUNTRY-2-READINESS|Country-2 readiness]]
- [[docs/MASTER_PLAN_CARDEEP_V2_2026-06-20|Master Plan V2]]

## Planes activos
- [[plans/autonomy-e2e/00-PLAN|Autonomy E2E]]
- [[plans/road-to-13/00-ROADMAP|Road to 13]]
- [[plans/country-autopilot/00-DESIGN|Country autopilot]]
- [[plans/cardeep-program/00-MASTER|Programa institucional A-Z]]

## Bitácora
- [[PROGRESO|PROGRESO.md — bitácora completa]]
- [[PLAN|PLAN.md]]
- [[RUNBOOK|RUNBOOK.md]]

## Segundo cerebro
- [[docs/second-brain/dashboards/pendientes-owner-search|Pendientes del owner]]
- [[docs/second-brain/dashboards/planes-por-estado|Planes por estado (Dataview)]]
- [[docs/second-brain/canvas/system-map|Mapa del sistema (Canvas)]]
```

- [ ] **Step 2: Write `pendientes-owner-search.md`**

```markdown
---
type: reference
tags: [second-brain]
---

# Pendientes del owner — búsquedas guardadas

Dataview no puede grepear de forma fiable los 391 KB de `PROGRESO.md` u otra prosa
libre del corpus legacy (no es data estructurada). Para ese corpus, usa la
búsqueda nativa de Obsidian (`Ctrl+Shift+F`) con estas queries exactas:

- `PENDIENTE-OWNER` — todo lo que espera una decisión/dato/infra del owner.
- `VERIFICADO` — afirmaciones marcadas como confirmadas contra código/DB real.
- `ASUMIDO` — afirmaciones no verificadas, a tratar con cautela.
- `HECHO 2026` — hitos cerrados por fecha.

Pulsa la estrella de "guardar" en el panel de resultados para fijarlas como
marcador permanente en la barra lateral.
```

- [ ] **Step 3: Write `planes-por-estado.md`**

````markdown
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
````

- [ ] **Step 4: Verify files exist**

Run: `ls "/c/Users/elias/projects/cardeep/docs/second-brain/dashboards/"`
Expected: the 3 files listed above.

---

### Task 8: Build `docs/second-brain/templates/`

**Files:**
- Create: `docs/second-brain/templates/session-log.md`
- Create: `docs/second-brain/templates/decision-record.md`
- Create: `docs/second-brain/templates/plan-doc.md`

- [ ] **Step 1: Write `session-log.md`**

```markdown
---
type: session
status: <% tp.system.suggester(["VERIFICADO", "ASUMIDO"], ["VERIFICADO", "ASUMIDO"]) %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [session-log]
---

# <% tp.system.prompt("Título de la sesión") %>

## Qué se hizo

## Decisiones

## Pendientes
```

- [ ] **Step 2: Write `decision-record.md`**

```markdown
---
type: decision
status: <% tp.system.suggester(["Propuesta", "Aceptada", "Rechazada", "Superada"], ["Propuesta", "Aceptada", "Rechazada", "Superada"]) %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [decision]
---

# <% tp.system.prompt("Título de la decisión") %>

## Contexto

## Decisión

## Consecuencias
```

- [ ] **Step 3: Write `plan-doc.md`**

```markdown
---
type: plan
status: <% tp.system.suggester(["Activo", "Pausado", "Cerrado"], ["Activo", "Pausado", "Cerrado"]) %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [plan]
---

# <% tp.system.prompt("Título del plan") %>

## Objetivo

## Fases

## Estado
```

- [ ] **Step 4: Verify files exist**

Run: `ls "/c/Users/elias/projects/cardeep/docs/second-brain/templates/"`

---

### Task 9: Build `docs/second-brain/canvas/system-map.canvas`

**Files:**
- Create: `docs/second-brain/canvas/system-map.canvas`

- [ ] **Step 1: Write the canvas JSON (verified JSON Canvas 1.0 schema)**

```json
{
  "nodes": [
    {"id":"n1","type":"text","text":"DISCOVER","x":-400,"y":-200,"width":250,"height":80},
    {"id":"n2","type":"text","text":"INGEST","x":0,"y":-200,"width":250,"height":80},
    {"id":"n3","type":"text","text":"SEAL","x":400,"y":-200,"width":250,"height":80},
    {"id":"n4","type":"file","file":"docs/architecture/00-TIER1-REGISTRY.md","x":-400,"y":-60,"width":300,"height":120},
    {"id":"n5","type":"file","file":"docs/architecture/02-SCRAPING-ENGINE.md","x":0,"y":-60,"width":300,"height":120},
    {"id":"n6","type":"file","file":"docs/architecture/05-VERIFICATION-VAM.md","x":400,"y":-60,"width":300,"height":120},
    {"id":"n7","type":"file","file":"docs/architecture/11-IDENTITY-RESOLUTION-AUTHORITY.md","x":0,"y":100,"width":300,"height":120},
    {"id":"n8","type":"file","file":"docs/generic-engine-bible/COUNTRY-PROOF-BUILD.md","x":400,"y":100,"width":300,"height":120},
    {"id":"n9","type":"file","file":"docs/generic-engine-bible/COUNTRY-2-READINESS.md","x":700,"y":100,"width":300,"height":120},
    {"id":"n10","type":"file","file":"docs/architecture/13-API-AND-DELTA.md","x":700,"y":-60,"width":300,"height":120}
  ],
  "edges": [
    {"id":"e1","fromNode":"n1","fromSide":"right","toNode":"n2","toSide":"left"},
    {"id":"e2","fromNode":"n2","fromSide":"right","toNode":"n3","toSide":"left"},
    {"id":"e3","fromNode":"n1","fromSide":"bottom","toNode":"n4","toSide":"top"},
    {"id":"e4","fromNode":"n2","fromSide":"bottom","toNode":"n5","toSide":"top"},
    {"id":"e5","fromNode":"n3","fromSide":"bottom","toNode":"n6","toSide":"top"},
    {"id":"e6","fromNode":"n5","fromSide":"bottom","toNode":"n7","toSide":"top"},
    {"id":"e7","fromNode":"n6","fromSide":"bottom","toNode":"n8","toSide":"top"},
    {"id":"e8","fromNode":"n8","fromSide":"right","toNode":"n9","toSide":"left"},
    {"id":"e9","fromNode":"n3","fromSide":"right","toNode":"n10","toSide":"left"}
  ]
}
```

- [ ] **Step 2: Verify valid JSON**

Run: `python -c "import json; json.load(open(r'C:\Users\elias\projects\cardeep\docs\second-brain\canvas\system-map.canvas'))" && echo VALID`

---

### Task 10: Commit spec + plan + vault to git

**Files:** all of the above, plus the spec doc from brainstorming.

- [ ] **Step 1: Review what will be committed**

Run: `cd "/c/Users/elias/projects/cardeep" && git status --short`

- [ ] **Step 2: Stage and commit**

```bash
cd "/c/Users/elias/projects/cardeep"
git add docs/superpowers/ docs/second-brain/ .obsidian/app.json .obsidian/community-plugins.json .gitignore
git commit -m "feat: add Obsidian second-brain vault (Dataview, Templater, MCP bridge)"
```

Note: plugin binaries (`main.js` etc.) are vendor releases, not project code — add a
`.gitignore` entry for `.obsidian/plugins/*/main.js` and `.obsidian/plugins/*/*.css`
style bundles is optional; default to committing them so the vault is fully
reproducible from git clone without re-downloading, unless repo size becomes a
concern (Dataview main.js ~2.3MB, Templater/REST API smaller — acceptable).

- [ ] **Step 3: Verify commit**

Run: `git log --oneline -1`

---

### Task 11: Launch Obsidian and hand off for owner audit

**Files:** none

- [ ] **Step 1: Launch Obsidian pointed at the vault**

Run (Windows): `start obsidian "obsidian://open?path=C%3A%5CUsers%5Celias%5Cprojects%5Ccardeep"` — if the URI handler isn't registered yet on first install, instead launch the app directly and use "Open folder as vault" pointed at `C:\Users\elias\projects\cardeep`.

- [ ] **Step 2: Declare the one real manual step to the owner**

Obsidian will very likely show a "Restricted Mode" banner (verified: this is a
real UI-only gate, no config bypass exists) — the owner clicks **"Turn on
community plugins"** once. This is the single non-automatable action in this
entire plan.

- [ ] **Step 3: After the owner unlocks plugins, retrieve the generated API key**

Run: `python -c "import json; print(json.load(open(r'C:\Users\elias\projects\cardeep\.obsidian\plugins\obsidian-local-rest-api\data.json'))['apiKey'])"`
Expected: a long hex/base64 string (only exists after the plugin has loaded once).

- [ ] **Step 4: Register the MCP server with Claude Code (user scope, no literal token on the command line)**

```bash
export OBSIDIAN_API_KEY="<value from step 3>"
claude mcp add --transport http obsidian http://127.0.0.1:27123/mcp/ --header "Authorization: Bearer ${OBSIDIAN_API_KEY}" --scope user
```

- [ ] **Step 5: Verify registration**

Run: `claude mcp list`
Expected: an `obsidian` entry pointing at `http://127.0.0.1:27123/mcp/`.

---

## Self-review notes

- Spec coverage: every section of the design spec (vault scope/exclusions, 3
  plugins, second-brain layer, MCP bridge, deliberate omissions) maps to a task
  above.
- No placeholders: every step has exact paths, exact commands, or exact file
  content.
- Task 5's exact asset URLs are resolved dynamically (via GitHub API call) rather
  than hardcoded, since the plugin's release naming wasn't pinned to a specific
  verified tag the way Dataview/Templater were — the plan resolves and prints the
  real URLs as part of execution, then downloads exactly those.
