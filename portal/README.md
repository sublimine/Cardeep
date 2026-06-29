# cardeep · portal

The cardeep product frontend, materialized from the **Claude Design** project
"Cardeep" (`claude.ai/design/p/cd99ab8f-851c-47e9-90ee-da85cae146df`).

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

## Roadmap (so this becomes the real portal)
1. Port all 10 screens to standalone HTML (see PROGRESO.md).
2. Pull referenced assets (`assets/`, hero media) for the screens that use them.
3. Wire live census data via the API client `web/src/api/cardeep.ts` → `:8090`
   (`/stats`, `/geo/seal`, `/geo/{prov}/entities`, `/entities/{cdp}/inventory`, …).
   Today's figures are the design's prototype values — clearly placeholder until wired.
4. Promote this portal to the canonical frontend and retire the synthetic `web/`
   (which carries a dead census client + a fabricated-numbers landing).

## Source of truth
The Claude Design project is the design source; this folder is the running
implementation. Re-pull a screen with the `DesignSync` tool (`get_file`) when the
design changes, then re-port.
