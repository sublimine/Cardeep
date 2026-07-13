# Obsidian Second-Brain Vault for Cardeep — Design Spec

**Date:** 2026-07-13
**Status:** APPROVED (owner, chat approval "Si joder!")
**Scope:** Cardeep project only (`C:\Users\elias\projects\cardeep`). Not CARDEX, not a multi-project vault (may be extended later).

## Problem

Cardeep already carries a huge amount of institutional knowledge as plain markdown —
`docs/` (19 root files + 10 subfolders: architecture, generic-engine-bible, research,
recon, runbook, ai, design, frontend, archive, outputs, workflows), `plans/` (20 files +
6 subfolders), plus root-level `PROGRESO.md` (391 KB), `PLAN.md`, `RUNBOOK.md`,
`README.md`, `CLAUDE.md`. None of it is linked, graphed, tagged, or dashboarded — it is
read linearly or grepped. The owner wants a proper second brain on top of this corpus,
plus anything else that raises the ceiling further.

## Decisions (owner-confirmed via AskUserQuestion + design approval)

1. **Vault location = repo root.** `C:\Users\elias\projects\cardeep` becomes the
   Obsidian vault directly (new `.obsidian/` created there). No duplication, no
   symlink games, single source of truth, versioned in the same git history as the
   code.
2. **Full integration including the MCP bridge**, with an honest caveat surfaced and
   accepted: since Claude Code already reads/writes any file in this repo directly
   (no MCP needed for that), the bridge's real marginal value is (a) visibility into
   whatever note is open in the live Obsidian GUI, (b) heading/block-level surgical
   patch operations, (c) triggering native Obsidian actions (e.g. running a Dataview
   query through Obsidian's own engine). It does not change what already leaves the
   machine towards Anthropic's API when Claude Code reads a file — that already
   happens today with plain Read.

## Architecture

### 1. Vault scope — excluded paths

Obsidian's file explorer/search/graph indexing is restricted via
`.obsidian/app.json` → `userIgnoreFilters` (verified: this is the real key backing
Settings → Files & Links → Excluded files; confirmed against three independent
sources including Obsidian's own settings help page and a real Obsidian+Claude Code
integration writeup using the identical pattern for a code repo).

Excluded (present on disk, git-tracked as before, just not indexed by Obsidian):
`pipeline/`, `services/`, `web/`, `portal/` (185 mirrored static pages — pure noise),
`tests/`, `migrations/`, `scripts/`, `scratch/`, `data/`, `countries/`, `ops/`,
`state/`, `.claude/`, `.backups/`, `.github/`, `.hypothesis/`, `.playwright-mcp/`,
`.pytest_cache/`, `.runlogs/`, `.wf/`, log files (`_*.log`), `Dockerfile`,
`docker-compose.yml`, `pytest.ini`, `requirements*.txt`, `scratch_mn_*.py`.

Kept indexed (the actual knowledge corpus): `docs/`, `plans/`, `CLAUDE.md`,
`INSTALL.md`, `PLAN.md`, `PROGRESO.md`, `README.md`, `RUNBOOK.md`, plus the new
`docs/second-brain/` layer described below.

### 2. Plugins — verified versions, headless install

Verified 2026-07-13 against the official Obsidian community-plugins registry and
each project's real GitHub releases (see workflow run `wf_3bd5bd21-e0a` for full
agent transcripts/sources):

| Plugin | id | repo | version |
|---|---|---|---|
| Dataview | `dataview` | blacksmithgu/obsidian-dataview | release tag `0.5.70` (manifest.json internally still says `0.5.68` — a real, confirmed mainainer discrepancy, not a fetch error) |
| Templater | `templater-obsidian` | SilentVoid13/Templater | `2.23.1` |
| Local REST API with MCP | `obsidian-local-rest-api` | coddingtonbear/obsidian-local-rest-api | `4.1.7`+ (bundles its own MCP server in-process — no separate bridge needed) |

Headless install method (no in-app plugin browser): download each plugin's
`main.js` + `manifest.json` + `styles.css` release assets straight into
`.obsidian/plugins/<id>/`, then list all three ids in
`.obsidian/community-plugins.json`.

**Known one-time manual gate (verified real, no config bypass found):** Obsidian
ships new vaults in "Restricted Mode" which ignores `community-plugins.json`
entirely until the human clicks "Turn on community plugins" once inside the app.
No documented `app.json`/`community-plugins.json` flag was found that pre-sets this
— multiple Obsidian forum threads and the official help docs confirm it is a
UI-only toggle. This click happens during the final "open Obsidian for owner audit"
step, not before.

### 3. New additive layer — `docs/second-brain/`

Nothing existing is reorganized. New folder only:

- `docs/second-brain/dashboards/00-Home.md` — Map of Content linking into
  `docs/architecture/`, `docs/generic-engine-bible/`, `plans/` by phase, and
  `PROGRESO.md`.
- `docs/second-brain/dashboards/pendientes-owner-search.md` — a documented saved
  search (not Dataview — the legacy corpus is unlabeled prose, Dataview cannot
  reliably grep 391 KB of free text as structured data) for `PENDIENTE-OWNER`,
  `VERIFICADO`, `ASUMIDO` markers already used throughout the corpus.
- `docs/second-brain/dashboards/planes-por-estado.md` — a live Dataview `TABLE`
  query over **new** notes going forward (frontmatter-driven; cannot retroactively
  query untagged legacy files).
- `docs/second-brain/templates/session-log.md`, `decision-record.md`,
  `plan-doc.md` — Templater templates, frontmatter schema mirrors the existing
  Claude auto-memory taxonomy (`type: project|feedback|decision`,
  `status: VERIFICADO|ASUMIDO`, `date`, backlinks).
- `docs/second-brain/canvas/system-map.canvas` — built-in Canvas (no plugin), a
  visual node map of the discover→ingest→seal spine and VAM/country-proof
  invariants, linking to real existing files (verified paths, not invented ones).

### 4. MCP bridge wiring

- Plugin: `obsidian-local-rest-api` (see table above), same headless method.
- API key + self-signed TLS cert are generated in-process the first time the
  plugin actually loads (i.e. after the Restricted Mode click) — there is no
  standalone daemon, Obsidian must be running for any MCP call to succeed.
- Registration command (loopback only, verified from the plugin's own README +
  Claude Code's MCP docs):
  ```
  claude mcp add --transport http obsidian http://127.0.0.1:27123/mcp/ \
    --header "Authorization: Bearer ${OBSIDIAN_API_KEY}"
  ```
  Using **user/local scope** (not project scope) so the key is never committed to
  git. Known Claude Code issue (anthropics/claude-code#60909): `claude mcp add`
  with a literal `--header` value echoes the token to stdout — mitigated by using
  `${OBSIDIAN_API_KEY}` env-var expansion instead of a literal key on the command
  line.
- Security: loopback-only (`bindingHost=127.0.0.1`), no telemetry found in the
  compiled plugin bundle. Does **not** reduce or increase what already leaves the
  machine via normal Claude Code usage of this repo.

### 5. Deliberately NOT installed

- **Obsidian Git** (auto-commit plugin): skipped — Claude Code already owns git
  commits here per the project's Conventional Commits convention; a second
  auto-committer would race/interleave noisily. Plain `git` already versions
  `docs/second-brain/`.
- **Excalidraw**: skipped — built-in Canvas already covers the visual-map need
  without adding a plugin (minimalism).

## Verification plan

- Automated: confirm each plugin folder has the 3 real downloaded files with
  non-zero size, `community-plugins.json` is valid JSON containing exactly the 3
  ids, `app.json` `userIgnoreFilters` is valid JSON with the exclusion list,
  `docs/second-brain/` files exist and internal links resolve to real paths.
- Manual (owner): Obsidian is launched pointed at the vault at the end of the
  build for the owner to audit directly — this is the closing step, not just a
  status claim.
