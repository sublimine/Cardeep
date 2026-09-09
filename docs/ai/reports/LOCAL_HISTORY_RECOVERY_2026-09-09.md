# Local history recovery — 2026-09-09

## Scope

This record covers Cardeep only. It preserves Git objects that existed solely
in the older local clone without applying their changes to the canonical
working tree. No stash was popped, applied, dropped, or rewritten. No remote
was contacted, and no garbage collection or pruning was run.

## Archived unreachable tips

The following refs were created in the older clone under
`refs/archive/cardeep-stale-20260909/`:

| Archive ref suffix | Commit | Classification |
|---|---|---|
| `01-milanuncios-exhaustiveness-wip` | `03d1094e8a7baf22c70d69bddf01efda5b914b14` | source/test WIP |
| `02-ai-audits-wip` | `1bdaffc08625e7fe86e29b9d8328a44c5202af2f` | governance audit WIP |
| `03-source-exhaustiveness-autostash` | `25f147cf4eeace4e523f651d9ef808b73b28405d` | autostash |
| `04-rivr-landing-wip` | `56f4da250a3e04d012479b623630e12e16b549d5` | landing-page WIP |
| `05-inventory-assistant-notes-wip` | `64875f452641f66079dcd3dcbf2ed0d36621a9c5` | UI WIP |
| `06-source-exhaustiveness-autostash` | `b424d91f7b2c19e102f202f569b51ce19410e7ad` | autostash |
| `07-web-governance-wip` | `b52bd2c98da5a690dceeeb98705ccfb6bb24febd` | web/governance WIP |
| `08-design-system-audits-wip` | `cdd26d105ef484503a87e80da179d1ce3ab21600` | design-system/audit WIP |
| `09-source-exhaustiveness-autostash` | `e40ad3ebe917ecac74a6a9c23705946497334803` | autostash |

All nine refs resolved back to their expected commit IDs after creation.

## Stashes preserved without integration

The older clone's three stash entries were also given durable aliases under
`refs/archive/cardeep-stashes-20260909/`:

| Stash at recovery time | Archive ref suffix | Commit |
|---|---|---|
| `stash@{0}` | `stash-0-design-system` | `82997639d3ba6b4886abe1d32145f98314d8bbb3` |
| `stash@{1}` | `stash-1-web-governance` | `b52bd2c98da5a690dceeeb98705ccfb6bb24febd` |
| `stash@{2}` | `stash-2-rivr-landing` | `56f4da250a3e04d012479b623630e12e16b549d5` |

The latter two commits intentionally appear in both tables: they were stash
reflog entries and also two of the nine otherwise-unreachable tips. These refs
are preservation anchors, not approval to merge the changes.

## Independent bundle

An external, complete-history bundle was created in the Cardeep backups area:

- File: `cardeep-stale-local-history-20260909.bundle`
- Size: `87,433,254` bytes
- Heads: `12` archive refs
- SHA-256: `5ef240fbbc2223b8650bf85ba3874ae1632ec1b8359bd21c6191602688d24781`
- `git bundle verify`: exit `0`; reports a complete history and status `okay`

Verification can be repeated without modifying either repository:

```text
git bundle verify <Cardeep-backups>/cardeep-stale-local-history-20260909.bundle
git bundle list-heads <Cardeep-backups>/cardeep-stale-local-history-20260909.bundle
```

## Recovered audit documents

Four Cardeep-only historical reports were copied from the older clone into the
canonical repository:

- `docs/ai/audits/DEDUP_IDENTITY_AUDIT.md`
- `docs/ai/audits/DOCS_VS_CODE_AUDIT.md`
- `docs/ai/reports/GOVERNANCE_INSTALL_CHECK.md`
- `docs/ai/reports/RUNTIME_BASELINE.md`

Their dates and runtime claims remain historical snapshots, not assertions
about the current environment. Literal local-development credentials were
redacted from the recovered copies; the substantive findings were not changed.

## Explicit non-actions and pending decision

- No WIP, landing-page work, design-system work, or UI change from a stash or
  archive tip was applied to the canonical branch.
- Obsidian and Graphify configuration or generated artifacts were not changed.
- A future review must decide, tip by tip, whether any source/test/UI versions
  remain desirable. Until then, the archive refs and bundle are the authority
  for preservation; they are not merge candidates by default.
