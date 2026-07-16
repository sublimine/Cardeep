# Graphify Integration for Cardeep — Design Spec

**Date:** 2026-07-15
**Status:** IMPLEMENTED (owner-confirmed via chat, "quiero que integres Graphify" +
follow-up "impecable, sin chapuzas" audit demand)
**Scope:** Cardeep project only, complementary to the existing Obsidian
second-brain vault (`docs/superpowers/specs/2026-07-13-obsidian-second-brain-vault-design.md`).
Not a replacement for it.

## Problem

The Obsidian second-brain vault (2026-07-13) indexes `docs/` and `plans/` —
decisions, context, prose. It has zero visibility into the actual **code
architecture**: what calls what, what depends on what, which modules are
structurally central. That gap is what Graphify closes: a tree-sitter-based
knowledge graph of the real codebase, queryable directly (`graphify query`)
and exportable into the same vault as browsable notes.

## Decisions

1. **Two complementary layers, one vault.** `docs/second-brain/` = knowledge
   (human/AI authored). `docs/second-brain/gf/` = code structure (machine
   generated from `pipeline/`, `services/`, `web/`, `scripts/`, `migrations/`,
   `tests/`; `portal/` excluded via `.graphifyignore` — same noise judgment
   already applied to the Obsidian docs layer for 185+ mirrored static pages).
2. **Package identity, verified before install.** PyPI package `graphifyy`
   (double-y) — the single-y name `graphify` is unclaimed and the subject of
   an open upstream issue (`safishamsi/graphify#280`, "possible name
   squatting"). Verified via `pip show` that Home-page/License/copyright match
   the real project (Safi Shamsi, MIT) before trusting the install.
3. **Default extraction mode: local AST only, forever, unless explicitly
   changed.** `--code-only`, no `--deep`, no LLM backend env var exported for
   extraction. Verified via the extraction log (`no LLM extraction`) that this
   held even with a stray `GEMINI_API_KEY` present in the shell environment.
   Secrets exclusion (`.env`, keys, certs, credential-named files) verified
   both by reading `detect.py`'s filter in source and by pattern-scanning the
   23MB output `graph.json` for credential/DSN/token patterns after the fact
   (zero hits, both times).
4. **Build artifacts, not source.** `graphify-out/` (raw graph.json,
   GRAPH_REPORT.md, cache) and `docs/second-brain/gf/` (exported Obsidian
   notes) are 100% regeneratable from the codebase and are gitignored — same
   treatment this repo already gives `data/`. Only the *tooling* that
   generates them (`.graphifyignore`, `.claude/hooks/fix_graphify_dotfiles.py`)
   is versioned.
5. **Automation split by cost.** `graphify hook install` wires a native git
   `post-commit` hook that rebuilds `graphify-out/graph.json` after every
   commit — cheap (AST-only, local, seconds). Re-exporting to Obsidian notes
   is deliberately **not** wired into that hook: it touches 26k+ files and
   forces Obsidian into a full reindex (in practice, requires a graceful
   restart to recover cleanly — see Known Issues), which is disruptive to run
   on every commit. It's a documented manual step instead (see `00-Home.md`).
6. **3-layer query rule**, appended to `CLAUDE.md`: `graphify query`/`explain`/
   `path` against `graph.json` first, the Obsidian vault second, raw source
   third — mirrors the pattern graphify's own docs recommend, adapted to this
   repo's existing MAPA DEL PROYECTO section rather than duplicating it.
7. **Community naming via `claude-cli` backend**, not a fresh API key. Graphify
   supports naming graph communities via an LLM (sends only up to 12 short
   node *labels* per community — function/class/variable names, never full
   source or docstrings, verified by reading `_community_label_lines` in
   `llm.py`). Chose the `claude-cli` backend (shells out to the already
   -authenticated local `claude` CLI) over repurposing the incidental
   `GEMINI_API_KEY` found in the shell environment, to stay inside the trust
   boundary the owner already accepts by using Claude Code at all, rather than
   silently routing data to a different vendor for a new purpose.

## Known issues found and fixed during the build (not caught by upstream)

- **Windows `MAX_PATH` (260 chars) crash.** `to_obsidian()`'s per-file cap
  (200 bytes on the filename stem) doesn't account for the target directory's
  own path length. First export crashed mid-run (20,759/26,217 notes written)
  on a label-derived filename that pushed the full path to exactly 260 chars.
  Fixed by shortening the target directory (`docs/second-brain/graphify/` →
  `docs/second-brain/gf/`), which recovers enough margin for the worst case
  (200-byte stem + `.md` + shortened prefix ≈ 256 chars, verified safe).
- **Obsidian hides ~9% of the corpus.** Graphify's `safe_name()` sanitizer
  doesn't strip a leading `.` from AST labels that are chained method calls
  (`.acquire()`), and Obsidian treats any dot-prefixed file as hidden (same
  convention as `.git/`/`.obsidian/`). 2,417 notes existed on disk and were
  individually fetchable by exact path (a misleading partial success signal)
  but were absent from Obsidian's own directory-listing API — meaning
  invisible in the file explorer, graph view, and search. Fixed with
  `.claude/hooks/fix_graphify_dotfiles.py`: renames the files and rewrites
  every `[[wikilink]]` that pointed at the old dotted name. First
  implementation was O(files × rename targets) — 26k × 2.4k — and had to be
  killed after 5+ minutes; rewritten as a single combined-alternation regex
  pass (17.5s). Verified fixed against Obsidian's live REST API listing
  directly, not just the filesystem — required a graceful Obsidian restart
  (never force-kill) to pick up the mass rename cleanly; a plain wait did not
  resolve it even after 10+ minutes (confirmed via flat memory usage that the
  REST plugin was genuinely stuck, not just slow).
- **Dataview dashboard contamination.** `planes-por-estado.md`'s query
  (`WHERE type`) would have matched all 26k+ graphify notes too (they also
  carry `type: "code"` frontmatter), burying the session/decision/plan notes
  it exists for. Fixed by matching explicit type values
  (`type = "session" OR type = "decision" OR type = "plan"`).
- **False alarm, caught and discarded**: an early self-audit script had a
  `.lstrip("./")` bug (strips any leading `.`/`/` characters, not the literal
  `"./"` prefix) that ate the genuine leading dot off real filenames,
  misreporting 2,296 files as unreadable. Verified against raw filesystem
  tools (`ls`, `find`) before concluding it was a tooling bug, not a data
  problem, and fixed the checker instead of chasing a phantom issue.

## Verification plan (all executed, not just planned)

- Security: read `security.py`, `detect.py`, `llm.py`, `install.py`,
  `hooks.py`, `querylog.py`, `cli.py` source directly rather than trusting
  README claims; independently pattern-scanned the actual generated
  `graph.json` for credential patterns (zero hits).
- Functional: deterministic wikilink-resolution audit (own script, not
  graphify's self-report) — 0 broken across 99,227 links, 100%.
- Live: verified against Obsidian's real REST API (not just the filesystem)
  for file listing, individual note fetch, and search — twice, before and
  after the dotfile fix, to prove the fix actually changed what the app sees.
- Automation: confirmed the post-commit hook fires and rebuilds without
  error on a real commit (not just read the hook's install log).
