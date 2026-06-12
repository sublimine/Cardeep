# T05 · Browser / Header / TLS Fingerprint Generation & Consistency

> Tooling audit. Domain: **fingerprint *generation* and *coherence*** — the layer that
> produces a self-consistent browser identity (UA / `Sec-CH-UA` / `Accept-*` headers,
> `navigator`, `screen`, WebGL/canvas/font values) and keeps every layer telling the
> *same* story. Sister docs own the transport/render engines: TLS impersonation
> (`curl_cffi`) and stealth browser (`camoufox`/Scrapling) are covered in
> `docs/architecture/02-SCRAPING-ENGINE.md`. This doc decides **what mints the values
> and asserts their consistency**, not what opens the socket.
>
> Anti-hallucination contract: every external claim is `[VERIFIED]` (repo/page fetched
> live via `gh api` or WebFetch on the date shown) or `[ASSUMED]` (inferred). All recency
> data fetched **2026-06-12**.

---

## 0. Scope and the three-layer model (read first — it kills 90% of the confusion)

A "fingerprint" is **not one thing**. Anti-bot vendors score three independent layers, and
a tool that nails one says nothing about the others. CARDEEP must keep all three coherent
*within a session* (Law #3 of the scraping engine). The generators audited here own
**Layer 2** and feed **Layer 3**; they do **not** touch **Layer 1**.

| # | Layer | What it is | Who owns it in CARDEEP | This doc? |
|---|---|---|---|---|
| 1 | **Network / TLS** | ClientHello → JA3/JA4, HTTP/2 SETTINGS + pseudo-header order, X25519MLKEM768 key share | `curl_cffi` (T0) · `camoufox`/BotBrowser native (T1/T2) | **No** (see §6) |
| 2 | **HTTP semantic** | `User-Agent`, `Sec-CH-UA*` client hints, `Accept` / `Accept-Language` / `Accept-Encoding`, `Sec-Fetch-*`, header *order* | **`browserforge` (generator)** | **YES** |
| 3 | **Browser JS surface** | `navigator.*`, `screen.*`, WebGL renderer/vendor, canvas noise, font enumeration, audio context, plugins, codecs | **`browserforge` generates values → `camoufox` injects them** | **YES (gen)** |

> The single highest-value property a fingerprint *generator* delivers is **cross-layer
> coherence**: a UA that says "Chrome 139 on Windows" must come with `Sec-CH-UA`
> `"Chromium";v="139"`, an `Accept-Language` matching the locale, a `navigator.platform`
> of `Win32`, a plausible Windows screen geometry, and a GPU string a Windows Chrome box
> would actually report — all drawn from a *joint* real-world distribution, never sampled
> independently. Independent sampling is the classic tell (a Linux GPU under a Windows UA).
> `browserforge` is purpose-built for exactly this (Bayesian generative network over real
> traffic). `[VERIFIED, daijro/browserforge README]`

CARDEEP's current choice (`requirements.txt`, commented arsenal block; `02-SCRAPING-ENGINE.md`
§6) is **`browserforge` for Layer 2 + feeding Layer 3, with `camoufox` doing Layer-3
injection and `curl_cffi` doing Layer 1.** `[VERIFIED, 02-SCRAPING-ENGINE.md:314,319,509-513]`
**This audit confirms that choice is correct and current — with two precise caveats** (§7).

---

## 1. Candidate scoreboard (recency — fetched 2026-06-12 via `gh api`)

| Tool | Role | Stars | Last code commit | Latest release | Data-model freshness | Status |
|---|---|---:|---|---|---|---|
| **`browserforge`** (daijro) | Py value generator (Layer 2 + Layer-3 values) | 1130 | **2026-02-26** (docs-only since) | PyPI **1.2.4 · 2026-02-03** | **data = `apify-fingerprint-datapoints` 0.13.0 · 2026-05-04** | **ALIVE ✅ — pick** |
| **`apify/fingerprint-suite`** (TS) | Upstream of browserforge; `header-generator` + `fingerprint-generator` + `fingerprint-injector` | 2389 | **2026-05-20** | npm **v2.1.83 · 2026-05-04** (monthly) | self (publishes the datapoints) | **ALIVE ✅ — pick if Node** |
| **`camoufox`** (daijro) | Layer-3 **injector** (Firefox C++), consumes browserforge fp | 9169 | **2026-06-10** (2 days ago) | **v150.0.2-beta.25 · 2026-05-11** | tracks Firefox 150 | **ALIVE ✅ (turbulent, see §7.2)** |
| **`fpgen`** (scrapfly/fingerprint-generator) | Py value generator; adds claimed TLS hints | 139 | **2025-03-22** (frozen ~14 mo) | model tag **2/2026 · 2026-02-18** | model refresh ~**every 11 mo** | ALIVE-ish — **fallback only** |
| **`pydoll`** (autoscrape-labs) | Chromium no-WebDriver automation (injector-side alt) | 6903 | 2026-05-24 | — | n/a (not a generator) | ALIVE (adjacent, §5) |
| **`hrequests`** (daijro) | All-in-one client w/ bundled fp | 1009 | **2024-12-01** (frozen 18 mo) | — | stale | **STALE — avoid** |
| **`fakebrowser`** (kkoooqq) | Puppeteer-era JS evasions + fp | — | core 2021–2022 | — | — | **💀 DEAD — archived 2025-03-03, repo now 404** |
| **FraudFox** (commercial) | Anti-detect browser | — | — | — | — | **💀 DEAD — deadpooled, unsupported 2026** |

Recency raw evidence (all `[VERIFIED]` via `gh api repos/<x>` / `gh api .../commits` /
PyPI JSON, 2026-06-12):

- `browserforge`: `pushed 2026-02-26`, last 8 commits Feb 2026 are README/sponsor edits;
  last **data-model** commit `2025-03-10` ("Use apify_fingerprint_datapoints package
  instead of file downloads"). PyPI history: 1.2.4 (2026-02-03), 1.2.3 (2025-01-29),
  1.2.1 (2024-12-11)… `[VERIFIED]`
- `apify-fingerprint-datapoints` (PyPI): latest **0.13.0 uploaded 2026-05-04T09:08**.
  `[VERIFIED, pypi.org/pypi/apify-fingerprint-datapoints/json]`
- `apify/fingerprint-suite`: releases v2.1.83 (2026-05-04), v2.1.82 (2026-04-01),
  v2.1.81 (2026-03-01) — **monthly**. Last commit 2026-05-20. `[VERIFIED]`
- `camoufox`: last commit `2026-06-10T06:49Z`, release `v150.0.2-beta.25` (2026-05-11),
  255 open issues, 9169 stars. `[VERIFIED]`
- `fpgen` (scrapfly): last **code** commit `2025-03-22`; release tags `model-3/2025`,
  `model-4/2025` (2025-04-02), `model-2/2026` (2026-02-18) → model refresh ~yearly, code
  frozen. `[VERIFIED]`
- `fakebrowser`: `gh api repos/kkoooqq/fakebrowser` → **HTTP 404**; web search confirms
  **archived 2025-03-03**, Puppeteer-era (2021–2022). `[VERIFIED]`

---

## 2. The pick — `browserforge` (value generator) + `camoufox` (injector)

### What it solves
`browserforge` is the Python re-implementation of Apify's `fingerprint-suite`. It exposes
two generators backed by a **Bayesian generative network trained on real-world traffic**,
so output frequencies match the wild (browser/OS/device mix), and — critically — the
fields are **jointly sampled and therefore internally coherent**. `[VERIFIED, README]`

- **`HeaderGenerator`** → `User-Agent`, `Sec-CH-UA` (with brand versions), `Sec-CH-UA-Mobile`,
  `Sec-CH-UA-Platform`, `Accept`, `Accept-Language`, `Accept-Encoding`,
  `Upgrade-Insecure-Requests`, `Sec-Fetch-Site/Mode/User/Dest`, in **browser-correct
  order**. This is the entire **UA / sec-ch-ua / Accept coherence** requirement of this
  task, solved by one call. `[VERIFIED, README]`
- **`FingerprintGenerator`** → `screen` (dims/colorDepth/pixelRatio/offsets), `navigator`
  (`userAgent`, `userAgentData`, `platform`, languages, `deviceMemory`,
  `hardwareConcurrency`), **WebGL `videoCard` {renderer, vendor}**, **fonts**,
  audio/video codecs, plugins, battery, multimedia devices. These are the **canvas/WebGL/
  font spoof *values*** the task asks for. `[VERIFIED, README]`

### Strengths
- **Coherence is the product**, not a bolt-on (joint distribution; matches `navigator`↔UA↔
  `Sec-CH-UA`↔screen↔GPU). Directly satisfies Law #3 of `02-SCRAPING-ENGINE.md`.
- **Data is current to 2026-05** via `apify-fingerprint-datapoints` 0.13.0 — the
  recency that matters (fresh Chrome/Firefox majors in the distribution) lives in the
  **monthly-updated** datapoints package, *not* in browserforge's own commit cadence.
  This is the single most important nuance of this audit: **browserforge looks "quiet"
  (docs-only commits in 2026) but its fingerprint corpus is May-2026 fresh.** `[VERIFIED]`
- **0.1–0.2 ms/fingerprint** — irrelevant cost at CARDEEP's scale. `[VERIFIED, README]`
- Already the native fingerprint source `camoufox` uses by default → **zero integration
  friction** with CARDEEP's existing Tier-1. `[VERIFIED, camoufox.com/python/browserforge]`
- Pure-Python, MIT-ish, Py 3.8–3.14, no native build. `[VERIFIED, PyPI]`

### Weaknesses (and the honest caveats)
- **`browserforge`'s own fingerprint *injection* is DEPRECATED** — the README says
  verbatim: *"Fingerprint injection in BrowserForge is deprecated. Please check out
  Camoufox instead."* `[VERIFIED, README]` → Use browserforge **only as a value
  generator**; never use its `inject_*` Playwright/Pyppeteer helpers. The injector job is
  camoufox's (§3).
- **It does NOTHING at Layer 1.** README makes *"no mention of TLS, JA3, or JA4."*
  `[VERIFIED]` JA3/JA4 rotation is `curl_cffi`'s job (§6) — do not expect this tool to
  fix a Python-shaped ClientHello.
- camoufox selectively drops some browserforge fields when its own data lags
  (*"some properties from BrowserForge fingerprints will not be passed to Camoufox"* due
  to outdated camoufox-side data). `[VERIFIED, camoufox.com/python/browserforge]` →
  monitor the actually-applied fingerprint, don't assume 1:1.

---

## 3. Division of responsibility (the architecture this audit endorses)

```
                       ┌──────────────────────────────────────────────┐
   one harvest         │  Session identity object (Law #3 coherence)   │
   session opens  ───▶ │  generated ONCE, asserted, reused everywhere  │
                       └───────────────┬───────────────┬───────────────┘
                                       │ Layer 2/3      │ Layer 1
                          ┌────────────▼────────┐   ┌───▼──────────────────┐
                          │ browserforge        │   │ curl_cffi            │
                          │ HeaderGenerator +   │   │ impersonate="chrome" │
                          │ FingerprintGenerator│   │ JA3/JA4 + H2 + PQ KS │
                          │ → UA, Sec-CH-UA,    │   │ (X25519MLKEM768)     │
                          │   Accept-*, screen, │   └──────────────────────┘
                          │   navigator, WebGL, │            T0 drain
                          │   fonts (VALUES)    │
                          └──────────┬──────────┘
                            T1 needs render?
                                     │ fingerprint=fg.generate()
                          ┌──────────▼──────────┐
                          │ camoufox (INJECTOR) │  writes values into Firefox C++ →
                          │ canvas/WebGL/font/  │  no JS-patch leak, no CDP leak
                          │ navigator JS APIs   │
                          └─────────────────────┘
```

**Rule of the split:** `browserforge` is the *single source of truth for the identity's
values*. At **T0** those values become `curl_cffi` request headers (UA/Sec-CH-UA/Accept).
At **T1** the *same* `browserforge` fingerprint object is handed to `camoufox`, which
injects the Layer-3 JS surface. The TLS major (curl_cffi `impersonate`) must be pinned to
match the UA major browserforge emitted — this is the **coherence invariant asserted at
session open, fail-closed** already specified in `02-SCRAPING-ENGINE.md §6`. `[VERIFIED]`

---

## 4. JA3 / JA4 rotation — explicit clarification (task sub-question)

The task asks about "JA3/JA4 rotation" inside the fingerprint-generation domain. **No
fingerprint *generator* (browserforge, fpgen, apify-suite) rotates JA3/JA4** — JA3/JA4 is
a *property of the TLS stack actually used*, not of a header/value generator. `[VERIFIED:
browserforge README has no TLS/JA3/JA4; apify-suite generates headers+JS, not ClientHello.]`

Correct ownership in CARDEEP (already designed, cross-referenced here so this doc is
self-contained):

- **Rotation/coherence of JA3/JA4** = `curl_cffi` `impersonate="chrome"` (rides the Chrome
  release train; the whole ClientHello is impersonated so JA4 follows), with the
  **X25519MLKEM768 post-quantum key share mandatory and monitored**.
  `[VERIFIED, 02-SCRAPING-ENGINE.md §8]`
- **What browserforge must guarantee** is only that the **UA major it emits == the Chrome
  major curl_cffi impersonates == the `Sec-CH-UA` major** — the cross-layer match. The
  *rotation* happens by bumping the `impersonate` target on Chrome's ~6-week cadence and
  letting browserforge sample UAs consistent with it. **Generator and TLS rotate together
  or you self-flag.** `[VERIFIED, 02-SCRAPING-ENGINE.md §5,§8]`

`fpgen` advertises "TLS fingerprints" among its datapoints, but that is **descriptive data
about what a JA3 *should* look like**, not an engine that emits that ClientHello on the
wire — it cannot replace `curl_cffi`. `[VERIFIED, scrapfly/fingerprint-generator README]`

---

## 5. Rejected / dead / adjacent — with reasons (no corpses recommended)

- **`fakebrowser` (kkoooqq) — 💀 DEAD.** `gh api` → **404**; **archived 2025-03-03**,
  read-only then removed. Puppeteer-stealth-era (2021–2022) JS evasion patches — exactly
  the *injection-by-JS-patch* approach modern detectors (CDP/Canvas-noise heuristics)
  catch. Even when it existed it was an *injector*, not a coherent value generator. **Do
  not use.** `[VERIFIED]`
- **FraudFox — 💀 DEAD.** Commercial anti-detect browser, **deadpooled / unsupported in
  2026** (pixelscan). Irrelevant to a code pipeline anyway. `[VERIFIED, websearch]`
- **`hrequests` (daijro) — STALE, avoid.** Last push **2024-12-01** (18 mo). Bundles an
  older fingerprint path; superseded by the browserforge+camoufox split from the same
  author. `[VERIFIED]`
- **`fpgen` / `scrapfly/fingerprint-generator` — FALLBACK ONLY.** Alive as a model artifact
  (model tag 2/2026) but **code frozen since 2025-03-22** and **data refresh ~yearly** vs
  browserforge's monthly datapoints. Broader single-call datapoint coverage (claims TLS +
  audio + intl in one object) is its one edge, but the slow data cadence is disqualifying
  for a system whose whole thesis is "current-Chrome floor." Keep as a **secondary value
  source / cross-check oracle**, not the primary. `[VERIFIED]`
- **`pydoll` (autoscrape-labs) — ADJACENT, not a generator.** Chromium-without-WebDriver
  automation, alive (2026-05-24). Relevant only as a **Chromium-side injector alternative**
  if a target fingerprints Firefox/camoufox specifically (the same fallback slot
  `02-SCRAPING-ENGINE.md §2` already lists `patchright`/`nodriver`/`zendriver` for). Does
  not mint coherent header/fp *values*. `[VERIFIED]`
- **Anti-detect browsers (Multilogin / GoLogin / AdsPower)** — commercial, GUI/profile
  oriented, per-profile pricing, no clean programmatic fingerprint-generation API for a
  headless fleet. Wrong shape for CARDEEP. `[VERIFIED, websearch]`

---

## 6. The fallback pick

**Primary:** `browserforge` (values) + `camoufox` (injection) + `curl_cffi` (TLS). ✅

**Fallback A — if Node enters the stack or browserforge's Python data path ever stalls:**
use **`apify/fingerprint-suite`** directly (`header-generator` + `fingerprint-generator` +
`fingerprint-injector`). It is browserforge's **upstream**, **2.4k stars, monthly releases
(v2.1.83, 2026-05-04), last commit 2026-05-20** — strictly fresher code cadence than the
Python port, and it *publishes the very datapoints browserforge consumes*. Cost: it's
TypeScript, so it only makes sense if a Node worker already exists. `[VERIFIED]`

**Fallback B — secondary value source / cross-check:** `fpgen`. Use to **independently
re-derive a fingerprint and diff** against browserforge's (an anti-monoculture oracle for
the verification layer), or for its one-call TLS-hint datapoints when sketching a recipe.
Never as the sole generator (yearly data cadence). `[VERIFIED]`

**Injector fallback — if camoufox's turbulence bites (see §7.2):** a Chromium-stealth
injector (`patchright` / `nodriver` / `zendriver` / `pydoll`) fed the *same* browserforge
values, switching the impersonated family from Firefox to Chromium. Already anticipated in
`02-SCRAPING-ENGINE.md §2`. `[VERIFIED]`

---

## 7. Verdict: is CARDEEP's current choice good enough?

**YES. `browserforge` is the correct, current, bulletproof pick for the value-generation
layer — keep it.** It is the de-facto standard, actively data-fed (2026-05), coherence-first,
and already the native fingerprint source of the Tier-1 browser CARDEEP runs. Nothing in
the live 2026 ecosystem beats it for *Python fingerprint generation*; the only fresher thing
is its own TypeScript upstream, which only helps if you're in Node. **No replacement
warranted.** Two caveats to wire into the engine, not reasons to switch:

### 7.1 Pin the data, not just the package
browserforge's *recency lives in `apify-fingerprint-datapoints`*, which it pulls as a
dependency. **Action:** pin `apify-fingerprint-datapoints` explicitly in `requirements.txt`
(currently transitive) and add it to the §8 "~6-week Chrome-cadence" refresh job from
`02-SCRAPING-ENGINE.md` — a stale datapoints pin silently ages every UA the fleet emits.
Treat a datapoints update like a Chrome-floor bump. `[VERIFIED gap: requirements.txt:521
lists `browserforge` with no datapoints pin.]`

### 7.2 camoufox is the real fragility, not browserforge
The **injector** (camoufox), not the generator, is the weak link. Public reporting notes a
**maintenance gap and fingerprint-consistency regressions** on its base-Firefox version,
and the repo carries **255 open issues** and ships **beta** tags (`v150.0.2-beta.25`) —
though it *is* actively committing again (last commit 2026-06-10). `[VERIFIED]` And camoufox
itself warns *some browserforge properties aren't applied* when its data lags. `[VERIFIED]`
**Action:** (a) after launching a camoufox session, **read back the applied fingerprint and
assert it still matches the session identity** (fail-closed, same invariant as TLS↔UA);
(b) keep the Chromium-stealth injector fallback (§6) warm; (c) track camoufox's Firefox-base
version as a monitored health signal exactly like the curl_cffi Chrome floor.

### 7.3 One-line bottom line
> **Generate with `browserforge` (pin its datapoints), inject with `camoufox` (verify the
> applied FP, keep a Chromium-stealth fallback), impersonate TLS with `curl_cffi`. Assert
> UA-major == Sec-CH-UA-major == TLS-major == injected-navigator-major at session open,
> fail-closed. `fakebrowser` is a corpse; `fpgen`/`apify-suite` are fallbacks.**

---

## 8. Sources (web-verified / `gh api`-verified 2026-06-12)

- browserforge repo, README, commits — github.com/daijro/browserforge ·
  raw.githubusercontent.com/daijro/browserforge/main/README.md · `gh api repos/daijro/browserforge`
- browserforge PyPI history — pypi.org/project/browserforge/
- **apify-fingerprint-datapoints** freshness (0.13.0, 2026-05-04) — pypi.org/pypi/apify-fingerprint-datapoints/json
- apify/fingerprint-suite (header-generator + fingerprint-generator + fingerprint-injector),
  v2.1.83 monthly — github.com/apify/fingerprint-suite · `gh api repos/apify/fingerprint-suite/releases`
- camoufox repo (v150.0.2-beta.25, 255 issues, last commit 2026-06-10), browserforge
  integration + "properties not passed" caveat, maintenance-gap/regression reporting —
  github.com/daijro/camoufox · camoufox.com/python/browserforge · camoufox.com/fingerprint/ ·
  roundproxies.com/blog/camoufox · `gh api repos/daijro/camoufox`
- fpgen / scrapfly fingerprint-generator (code frozen 2025-03-22, model 2/2026) —
  github.com/scrapfly/fingerprint-generator · `gh api repos/scrapfly/fingerprint-generator`
- fakebrowser archived 2025-03-03, repo now 404 — `gh api repos/kkoooqq/fakebrowser` (404) ·
  websearch (github topics / issue history)
- FraudFox deadpooled 2026 — pixelscan.net/blog/fraudfox-why-its-no-longer-supported
- hrequests / pydoll recency — `gh api repos/daijro/hrequests` · `gh api repos/autoscrape-labs/pydoll`
- CARDEEP internal `[VERIFIED]` facts — `docs/architecture/02-SCRAPING-ENGINE.md` (§5,§6,§8,
  Layer/Session model), `requirements.txt` (arsenal block).
