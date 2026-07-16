# cardeep · portal

> ⚠ **Not the running app.** The canonical frontend is [`web/`](../web) (React +
> Vite, `npm run dev` → `http://localhost:5173`). This folder is a **static
> design-reference sandbox** — screens get prototyped here first, then ported
> into real, API-wired components in `web/`. Nobody should point a user, a demo,
> or CI at anything under `portal/`.

Design source materialized from the **Claude Design** project "Cardeep"
(`claude.ai/design/p/cd99ab8f-851c-47e9-90ee-da85cae146df`).

## What this is
Each screen designed in Claude Design ships as a `*.dc.html` **Design Component**
(an `<x-dc>` template + a `DCLogic` class, mounted at runtime by `support.js` via
`window.React`/`window.ReactDOM`). Those globals are injected by the claude.ai/design
preview host, so a raw `.dc.html` does **not** run standalone.

The screen bodies, however, are **plain HTML + inline CSS + vanilla-JS DOM code** —
React adds nothing (the template is static, `renderVals()` returns `{}`). So each
screen is ported 1:1 to a **dependency-free standalone `.html`**:
- `<helmet>` link tags  → `<head>`
- `<x-dc>` inner markup  → `<body>`
- `DCLogic.componentDidMount()` body → a `DOMContentLoaded` `<script>`
- inter-screen links `X.dc.html` → `x.html`

No React, no `support.js`, no claude.ai coupling. Opens in any browser; deployable
as static files anywhere.

## Preview locally
```bash
cd portal
python -m http.server 8777
# open http://localhost:8777/analitica.html   (index.html = landing, once ported)
```

## Roadmap (superseded 2026-07-16 — kept for history, see note below)
~~1. Port all 10 screens to standalone HTML.~~ Done.
~~2. Pull referenced assets for the screens that use them.~~ Done.
~~3. Wire live census data via the API client `web/src/api/cardeep.ts` → `:8090`.~~
~~4. Promote this portal to the canonical frontend and retire `web/`.~~

**This plan was reversed in practice, not on paper.** Starting 2026-06-30
(`8614f69` — mirror the portal landing + marketplace into React), work went
the other way: portal screens were ported *into* `web/`, which kept the live
API wiring and became canonical. This README's roadmap said "retire `web/`"
for two weeks after that had already stopped being the plan — a stale doc, not
a fact. Corrected 2026-07-16 after the owner asked why several frontends
existed.

## What this folder is *for*, now
A design-reference sandbox: new Claude Design screens and the mirrored
TailAdmin/Spike template libraries (`app/`) live here as source material to
mine when building or restyling a page in `web/`. It also still previews
fine standalone (`python -m http.server 8777`) for eyeballing a design before
porting it — that's it.

## Source of truth
The Claude Design project (`claude.ai/design`) is the design source; **`web/`
is the running implementation.** Re-pull a screen here with `DesignSync`
(`get_file`) when the design changes, port what's needed into `web/`, then
leave the copy here as reference.
