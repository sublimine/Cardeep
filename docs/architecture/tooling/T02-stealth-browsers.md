# T02 · Stealth / Undetected Browsers — Live 2026 Audit

> Tooling audit for CARDEEP's **Tier-1 render engine** (the stealth browser that passes
> JS/sensor challenges when `curl_cffi` at Tier-0 hits a wall). Scope is the
> *automation-control-plane + browser-stealth* layer only: camoufox, patchright, nodriver,
> zendriver, SeleniumBase UC/CDP, BotBrowser, rebrowser-patches, and the undetected lineage.
> TLS/JA3 impersonation (Tier-0 `curl_cffi`), fingerprint generation (`browserforge`), and
> Tier-2 sensor generation (Hyper Solutions) are out of scope — see T01 / T05 / `02-SCRAPING-ENGINE.md §2`.
>
> Anti-hallucination: every external fact is `[VERIFIED]` (repo/page fetched live on
> 2026-06-12) or `[ASSUMED]`. Dead/abandoned tools are flagged explicitly. Recency is
> ruthless: any tool not shipped in 12+ months is suspect and called out.
>
> **Anchor to existing doctrine:** `02-SCRAPING-ENGINE.md §1 (law 1: target the data layer),
> §2 (tier ladder), §4 (per-defense table)`. The stealth browser is *render-to-unlock*, not
> the bulk-drain engine — "promote to unlock, demote to drain."

---

## 0. TL;DR verdict

CARDEEP's documented Tier-1 pick — **Scrapling `StealthyFetcher`, described as "camoufox-driven"**
(`02-SCRAPING-ENGINE.md §2 Tier-1`, `requirements.txt`) — is **half-right and now factually
stale on the engine**:

1. **Scrapling itself is the right wrapper** and is the *most actively maintained* tool in
   this whole audit (v0.4.9, 2026-06-07). `[VERIFIED]` Keep it.
2. **But `StealthyFetcher` no longer drives camoufox.** As of Scrapling **v0.3.13** the engine
   was swapped from camoufox to **patchright** ("replaced by patchright for many reasons…
   101% faster, less memory, more stable"). `[VERIFIED, scrapling.readthedocs.io/stealthy]`
   The doc's "camoufox-driven StealthyFetcher" claim is wrong for current Scrapling.
3. **The `camoufox` pip package CARDEEP pins (`camoufox[geoip]`) is itself stale:** PyPI
   `camoufox 0.4.11`, last published **2025-01-29** — ~16 months old. `[VERIFIED, pypi]` The
   Firefox-fork *binary* still ships (v150, 2026-05) but the original maintainer is on a
   medical hiatus and dev has forked out to CloverLabsAI. `[VERIFIED]`

**Recommendation:** adopt a **two-engine, CDP-first** Tier-1, not a single Firefox-fork:

- **Primary control plane: `patchright` (channel=chrome)** — the bulletproof, drop-in
  Playwright-API stealth engine, shipping monthly, that CARDEEP gets *for free* through
  Scrapling's current `StealthyFetcher`. Use Scrapling as the wrapper; patchright is the
  body. `[VERIFIED]`
- **Fallback control plane: `nodriver`** (or its community fork **`zendriver`**) — pure-CDP,
  no-Playwright-shim driver that wins the cases patchright loses (Cloudflare Turnstile-hard,
  Google, sites that fingerprint the Playwright protocol handshake). `[VERIFIED, 2 independent
  2026 benchmarks]`
- **Hard-target render of last resort (Tier-2, spend-gated): `BotBrowser`** (patched Chromium,
  `.enc` profiles) for Akamai/Kasada/DataDome-with-sensor — keep it exactly where the doc
  already puts it. `[VERIFIED]`
- **DROP from any recommendation: `rebrowser-patches`** — effectively abandoned (last release
  2025-05-09, ~13 months) and bottom-of-table in both 2026 benchmarks. It is a corpse for our
  purposes. `[VERIFIED]`
- **camoufox** stays a *secondary* Firefox-shaped option for the narrow case where a target
  specifically fingerprints/penalizes Chromium and rewards Firefox — but it is no longer the
  default, given the hiatus + the stale pip wrapper + a measured perf/consistency regression.

---

## 1. The detection model these tools actually fight (why CDP-first wins in 2026)

Anti-bot in 2026 scores **four independent layers** into one trust score; you must pass *all*
`[VERIFIED, webscrapingapi / scrapfly 2026]`:

1. **TLS / JA3-JA4** (incl. the X25519MLKEM768 post-quantum key share) — owned by **Tier-0
   `curl_cffi`**, not the browser. Out of scope here but it is *why* CARDEEP renders only to
   unlock, then drains on Tier-0.
2. **Automation-protocol fingerprint** — the *shape of the control channel*. This is the layer
   that splits the field in 2026: Playwright/CDP issues a recognizable handshake (e.g.
   `Runtime.enable`, the Playwright bidi/Juggler shape, console-domain enables) at startup.
   Patched Playwright forks *reduce* it; **a pure-CDP driver removes it** because there is no
   Playwright in the loop. `[VERIFIED, ianlpaterson 2026]`
3. **JS-layer fingerprint** — `navigator.webdriver`, WebGL/Canvas/Audio, screen geometry,
   `hardwareConcurrency`, WebRTC leaks. camoufox patches these in C++ *before JS sees them*;
   Chromium tools patch in JS/flags. `[VERIFIED]`
4. **Behavioral + IP reputation** — mouse motion (DataDome scores ~31 motion signals),
   datacenter-vs-residential. Browser choice does **not** solve this; residential proxies +
   humanlike motion do (Tier-2). `[VERIFIED, scrapfly datadome 2026]`

**Load-bearing consequence:** the single biggest 2026 stealth gain is at **layer 2**, and it
favours **direct-CDP drivers (nodriver/zendriver, SeleniumBase CDP Mode)** over even
patched-Playwright (patchright). The benchmarks below confirm this — but they *disagree on the
margin*, which is why CARDEEP needs both a patched-Playwright primary (ergonomics, Scrapling
integration) and a pure-CDP fallback (raw bypass on the hard Cloudflare/Turnstile cases).

---

## 2. Candidate-by-candidate (alive/dead · what it solves · strengths/weaknesses)

All metrics `[VERIFIED]` by fetching the repo/PyPI/docs on **2026-06-12** unless marked.

### 2.1 Scrapling (the wrapper CARDEEP already names) — ✅ ALIVE, very active

- **What it is:** an adaptive scraping *framework* wrapping fetchers: `Fetcher` (HTTP),
  `StealthyFetcher` (stealth browser), `DynamicFetcher` (plain Playwright). Provides adaptive
  CSS-selector self-healing (relied on in `02-SCRAPING-ENGINE.md §9.3`).
- **Recency:** **v0.4.9, 2026-06-07** ("maintenance update, community fixes"); v0.4 line
  Feb–Jun 2026; very large following. `[VERIFIED, github.com/D4Vinci/Scrapling/releases]`
- **The fact that changes our doc:** `StealthyFetcher` **dropped camoufox for patchright at
  v0.3.13** — "used a custom version of Camoufox as an engine before version 0.3.13, which was
  replaced by patchright for many reasons"; result is "**101% faster**, less memory, ~400 LOC
  shorter, more stable." `[VERIFIED, scrapling.readthedocs.io/en/latest/fetching/stealthy.html]`
  It still "bypasses all types of Cloudflare's Turnstile/Interstitial," CDP runtime leaks,
  WebRTC leaks, isolates JS, removes Playwright fingerprints. `[VERIFIED]`
- **Verdict:** **keep as the wrapper.** It gives CARDEEP patchright + adaptive selectors +
  the data-layer-capture ergonomics in one dependency, and it is the best-maintained thing
  here. Camoufox is still reachable through it for the Firefox case (docs give the opt-in).

### 2.2 patchright — ✅ ALIVE, monthly releases — **PRIMARY PICK**

- **What it solves:** drop-in **undetected Playwright** (Python + Node). Patches the Playwright
  control-plane leaks: **`Runtime.enable` leak** (runs JS in isolated ExecutionContexts),
  **`Console.enable` leak**, `navigator.webdriver` flag leaks, command-flag leaks, closed
  shadow-root access. `[VERIFIED, github.com/Kaliiiiiiiiii-Vinyzu/patchright]`
- **Recency:** **v1.60.0, 2026-06-03**; tracks Playwright versioning closely; ~3.5k stars; only
  **5 open issues**; active maintainer (Vinyzu). `[VERIFIED]`
- **Strengths:** zero-rewrite for any Playwright code; runs real Chrome via `channel="chrome"`;
  best ergonomics-per-stealth ratio; benchmark **100.0 Cloudflare bypass** in techinz, and 25/3/3
  (OK/gated/blocked) in ianlpaterson — mid-pack but *no full-blocks on the production anti-bot
  sites it was tuned for*. `[VERIFIED]`
- **Weaknesses:** it is still **Playwright-shaped at the protocol layer**, so it *loses the
  hardest CDP-fingerprinting targets* a pure-CDP driver passes (ianlpaterson: Patchright
  blocked on `google-search`, took the Cloudflare-medium interstitial where nodriver passed
  clean). Detectable in headless on some targets — run headed/xvfb. `[VERIFIED]`
- **Verdict:** **primary Tier-1 control plane**, used *via Scrapling `StealthyFetcher`* so
  CARDEEP also gets adaptive selectors and the unlock-then-drain capture pattern.

### 2.3 nodriver — ✅ ALIVE, active (no formal releases) — **FALLBACK PICK**

- **What it solves:** official successor to `undetected-chromedriver` by the same author. Drives
  Chrome over **plain CDP, fully async, no Selenium/chromedriver/Playwright**. Built-in helpers
  for Cloudflare verification and iframe detection. `[VERIFIED, github.com/ultrafunkamsterdam/nodriver]`
- **Recency:** **4.4k stars, 166 commits on main, 6 open PRs, only 8 open issues**; actively
  developed — **but "No releases published"** (install tracks `main`/PyPI `nodriver`). The
  no-tagged-release model is a *minor* supply-chain caveat (pin a commit). `[VERIFIED]`
- **Strengths:** **wins both 2026 benchmarks on raw Cloudflare/Turnstile bypass** — ianlpaterson:
  **28 OK / 3 gated / 0 blocked, the only tool with zero blocked cells across 31 targets**;
  passes `google-search`, `canadianinsider`, `medium` where Patchright/Camoufox are gated or
  blocked. "Chrome 148 over plain CDP passes Cloudflare-Turnstile pages where six Chromium and
  Firefox stealth approaches fail the same page." `[VERIFIED]`
- **Weaknesses:** **heaviest resource footprint** in techinz (1389 MB / 47.4% CPU) — it drives a
  full real Chrome; **not a Playwright API** (own async API → a second code path vs Scrapling);
  no tagged releases. `[VERIFIED]`
- **Verdict:** **fallback control plane** for the specific sources where patchright is gated/
  blocked (the router escalates per-source, `02-SCRAPING-ENGINE.md §3/§9.4`). Worth the second
  code path precisely because it clears walls the primary cannot.

### 2.4 zendriver — ✅ ALIVE, released, community-governed fork of nodriver

- **What it is:** a **fork of nodriver** created because the upstream "restricts contributions";
  adds features, bugfixes, ruff/mypy, real semver releases. Same pure-CDP stealth model.
- **Recency:** **v0.15.3, 2026-03-12**; 1.3k stars; **69 open issues** (higher than nodriver,
  reflects more community surface). `[VERIFIED, github.com/stephanlensky/zendriver]`
- **Strengths:** **tagged, pinnable releases** (fixes nodriver's supply-chain caveat); more open
  to PRs; same CDP-direct bypass class as nodriver (benchmark zendriver-chrome 70.0 in techinz —
  below nodriver's 80.0, but same architecture and the gap is config/version drift, not design).
  `[VERIFIED]`
- **Weaknesses:** slightly behind nodriver on the raw Cloudflare score in techinz; fork-lag risk
  vs upstream Chrome bumps; larger open-issue backlog. `[VERIFIED]`
- **Verdict:** **drop-in alternative to nodriver** — prefer it *if* CARDEEP wants pinnable
  semver releases over tracking nodriver's `main`. Functionally interchangeable as the fallback.

### 2.5 SeleniumBase (UC Mode / CDP Mode) — ✅ ALIVE, extremely active

- **What it solves:** batteries-included test+scrape framework. **UC Mode** = undetected-
  chromedriver-style (renames CDP console vars, launches Chrome then attaches, disconnects
  chromedriver during sensitive actions). **CDP Mode** (newer) = drives via CDP through MyCDP,
  "stealthier than WebDriver," now the recommended stealth path; `--cft` makes Chrome-for-Testing
  stealthy; calling `sb.open()` from UC Mode now activates CDP Mode. `[VERIFIED, seleniumbase.io
  cdp_mode; pypi]`
- **Recency:** **4.49.10 on PyPI, published 2026-06-12 (today)**; maintainer mdmintz ships almost
  daily. One of the most actively maintained projects in the entire space. `[VERIFIED, pypi.org/
  project/seleniumbase]` *(Note: a GitHub releases snapshot mis-rendered this as "June 2024";
  PyPI is authoritative — June 2026.)*
- **Strengths:** widely-cited as "the most reliable **free** solution for Cloudflare Turnstile in
  2026"; mature, huge docs, handles xvfb, proxies, captcha-click flows; CDP Mode gives much of
  nodriver's stealth with a friendlier API. `[VERIFIED]`
- **Weaknesses:** **UC Mode is detectable in headless** (must run headed/xvfb — a real ops cost
  at scale); heavier abstraction than nodriver; for a pure render-to-unlock role it brings more
  framework than CARDEEP needs given Scrapling is already the wrapper. `[VERIFIED]`
- **Verdict:** **strong alternative fallback** and a sanity reference. If CARDEEP did *not*
  already standardize on Scrapling, SeleniumBase CDP Mode would be a top-2 pick. Given Scrapling
  is the wrapper, keep SeleniumBase as a **documented escape hatch** (its Turnstile-clicking and
  xvfb tooling are best-in-class for the awkward interactive cases), not the default.

### 2.6 camoufox — ⚠️ ALIVE but HIATUS + stale pip wrapper + perf regression

- **What it solves:** Firefox fork with **C++-level fingerprint spoofing** (WebGL, AudioContext,
  `hardwareConcurrency`, screen geometry, WebRTC spoofed *before JS runs*); headless, scriptable
  via Playwright/Juggler; `[geoip]` extra aligns locale/timezone to proxy. The *only* Firefox-
  shaped option here — value is non-zero precisely because most targets over-tune for Chromium.
  `[VERIFIED, github.com/daijro/camoufox, camoufox.com/stealth]`
- **Recency (split signal — read carefully):**
  - Browser **binary** fork: **v150.0.2, 2026-05-11**, 9.2k stars, **234 open issues**. ALIVE.
  - **Pinned hiatus notice:** "*a year gap in maintenance due to a personal situation… Camoufox
    has gone down in performance due to the base Firefox version and newly discovered fingerprint
    inconsistencies.*" Original maintainer (daijro) hospitalized since 2025-03; primary dev
    **relocated to `github.com/CloverLabsAI/camoufox`** + VulpineOS; daijro repo now just "merges
    checkpoint releases." `[VERIFIED]`
  - **The Python package CARDEEP would install is the stale part:** PyPI **`camoufox 0.4.11`,
    2025-01-29 (~16 months old)**. The maintained path is the `cloverlabs-camoufox` PyPI package /
    CloverLabs fork. `[VERIFIED, pypi]`
- **Strengths:** unique Firefox fingerprint surface; C++ patches are deeper than JS patches;
  excellent on Google/JSON-LD targets in ianlpaterson (Camoufox passed `google-search`).
- **Weaknesses:** **the hiatus + the self-admitted perf/consistency regression + a 16-month-stale
  pip wrapper** make it a *risky default* for a system that must not fall (`02-SCRAPING-ENGINE.md`
  opening mandate). Was blocked on `dev.to` (only tool blocked there) in ianlpaterson; mid-pack
  25/3/3. Heavier than HTTP, Firefox base lags Chrome's anti-bot-relevant features.
- **Verdict:** **demote from primary to secondary.** Keep ONLY for the narrow Firefox-rewarding
  target, and if used, pin the **`cloverlabs-camoufox`** package, not stock `camoufox`. Do **not**
  describe StealthyFetcher as "camoufox-driven" anymore (§4 fix).

### 2.7 BotBrowser — ✅ ALIVE, active — keep as Tier-2 render of last resort

- **What it solves:** patched **Chromium** with encrypted `.enc` **profiles** that pin a coherent
  cross-OS fingerprint; launched via `--bot-profile`. Broadest claimed coverage: **Cloudflare,
  Akamai, Kasada, Shape, DataDome, PerimeterX, hCaptcha, FunCaptcha, Imperva, reCAPTCHA,
  ThreatMetrix, Adscore.** `[VERIFIED, github.com/MiddleSchoolStudent/BotBrowser]`
- **Recency:** **149.0.7827.59, 2026-06-09**; 2.5k stars; 4 open issues; 692 commits. ALIVE,
  tracking current Chromium. `[VERIFIED]`
- **Strengths:** deepest anti-bot reach of any open engine; profile model gives the cross-OS
  coherence law-#3 wants; the right hammer for Akamai/Kasada render when sensor-minting (Hyper)
  isn't enough.
- **Weaknesses:** **freemium** — MIT core but the strong profiles/features are Pro/ENT tiers
  (`02-SCRAPING-ENGINE.md` already flags it Tier-2, spend-gated); a binary, not a pip dep; heavier
  ops. `[VERIFIED]`
- **Verdict:** **leave exactly where the doc has it** — Tier-2 render-of-last-resort behind the
  spend gate. This audit *confirms* that placement; no change.

### 2.8 rebrowser-patches — ❌ DEAD-for-our-purposes (do NOT recommend)

- **What it was:** Puppeteer/Playwright patches for the **`Runtime.enable` leak** + script-name
  masking. Historically important — it *popularized* the Runtime.enable fix that patchright now
  ships natively. `[VERIFIED, github.com/rebrowser/rebrowser-patches]`
- **Recency:** **last release v1.0.19, 2025-05-09 (~13 months); 33 open issues; base it patches
  pinned to Playwright 1.52.0 / Puppeteer 24.8.1 (April–May 2025).** Not keeping up with upstream.
  `[VERIFIED]`
- **Benchmark:** **bottom of the table, tied with vanilla Playwright** (ianlpaterson: 24 OK / 2 /
  **5 blocked**, identical block set to unpatched). Its one trick is now subsumed by patchright.
  `[VERIFIED]`
- **Verdict:** **CORPSE for CARDEEP.** Everything it does, patchright does, maintained and better.
  Remove from consideration. (Not "dead software" in the abstract — but dead as a *recommendation*:
  stale, superseded, and benchmark-equivalent to no patch at all.)

### 2.9 The undetected lineage (`undetected-chromedriver`, `puppeteer-extra-stealth`) — ❌ legacy

- `undetected-chromedriver`: superseded by the same author's **nodriver** (explicitly the
  "recommended successor"). `[VERIFIED]` Use nodriver/zendriver instead.
- `puppeteer-extra-plugin-stealth`: repeatedly described as deprecated/outpaced for modern
  Cloudflare in 2026 sources. `[VERIFIED, websearch]` Not recommended.
- **Verdict:** legacy; do not start here in 2026.

---

## 3. Benchmark cross-read (two independent 2026 datasets, and why they disagree)

| Tool | techinz Cloudflare score `[VERIFIED]` | ianlpaterson OK/Gated/Blocked of 31 `[VERIFIED]` | Maint. recency | Class |
|---|---|---|---|---|
| **nodriver** | 80.0 | **28 / 3 / 0** (winner, 0 blocked) | active, no tags | pure-CDP |
| **zendriver** | 70.0 | (same architecture as nodriver) | v0.15.3 2026-03 | pure-CDP (fork) |
| **patchright** | **100.0** | 25 / 3 / 3 | v1.60.0 2026-06 | patched-Playwright |
| **camoufox** | 90.0 | 25 / 3 / 3 (blocked on dev.to) | v150 2026-05, hiatus | Firefox C++ |
| **SeleniumBase** | (UC/CDP, not isolated) | — | 4.49.10 2026-06-12 | UC + CDP |
| **CloakBrowser** (ref) | 90.0 | 26 / 3 / 2 | n/a (commercial) | patched Chromium |
| **curl_cffi** (Tier-0 ref) | — | 26 / 3 / 2 | active | HTTP only |
| **vanilla Playwright** | 60.0 | 24 / 2 / 5 | n/a | baseline |
| **rebrowser-playwright** | — | 24 / 2 / 5 (= vanilla) | **2025-05, stale** | DEAD-rec |

**Why they disagree (and the lesson for CARDEEP):** techinz crowns **patchright (100)**;
ianlpaterson crowns **nodriver (0 blocked)**. The split is **target-mix and config dependent** —
patchright tops *production anti-bot panels it's tuned for*; nodriver tops *raw Cloudflare-
Turnstile + Google + content sites* because it removes the layer-2 protocol shape. This is exactly
the empirical reality `02-SCRAPING-ENGINE.md §3` already encodes ("cost-effectiveness grounded in
`browsers-benchmark`, never on fame"). **Therefore CARDEEP must not pick one winner — it must run
`is-antibot` per source and route to whichever engine clears that defense**, with patchright as the
ergonomic default and nodriver as the escalation. The router/self-tuning machinery in §3/§9.4 is
the right home for this; this audit just fixes *which engines* sit behind it.

> Caveat `[VERIFIED]`: both benchmarks are point-in-time and partly synthetic (CreepJS/JS panels
> ≠ live Spanish targets). Treat them as priors; CARDEEP's own `browsers-benchmark` run against the
> actual census targets (`SOURCES_ES.md`) is the binding evidence, per existing doctrine.

---

## 4. Concrete changes this audit forces on existing CARDEEP docs/config

Grounded fixes against `02-SCRAPING-ENGINE.md` and `requirements.txt` — nothing abstract:

1. **§2 Tier-1 text + §6 table: "camoufox-driven StealthyFetcher" → "patchright-driven
   StealthyFetcher (camoufox optional, Firefox-only case)."** Scrapling swapped the backend at
   v0.3.13; the doc describes a state two minor-lines out of date. `[VERIFIED]`
2. **§2 Tier-1 fallback list: promote `nodriver`/`zendriver` from "drop-in CDP alternative" to
   the *named escalation engine* for patchright-blocked sources** — they demonstrably clear
   Cloudflare-Turnstile/Google cases patchright is gated on. `[VERIFIED]`
3. **`requirements.txt`: change the Tier-1 pins** (see §5). Drop the bare `camoufox[geoip]` as the
   default; pin `patchright` (CARDEEP gets it transitively via Scrapling, but pin for
   reproducibility) and add `nodriver` (or `zendriver`) for the fallback path. If camoufox is kept,
   pin **`cloverlabs-camoufox`**, not the 16-month-stale stock `camoufox`. `[VERIFIED]`
4. **Tier-2 §2 / §4 BotBrowser: no change** — audit confirms it as render-of-last-resort.
5. **Never reference `rebrowser-patches`** in any recipe/tier — it is stale and benchmark-equal to
   no patch. `[VERIFIED]`

---

## 5. Sample CONFIG (drop-in for the new `pipeline/fetch/` engine, §10 of the engine doc)

`requirements.txt` — Tier-1 block (replaces the camoufox-default line):

```text
# Tier-1 — stealth browser / render  (control-plane = patched-Playwright primary + pure-CDP fallback)
scrapling>=0.4.9             # wrapper: StealthyFetcher(patchright) + adaptive selectors  [VERIFIED 2026-06-07]
patchright>=1.60.0           # PRIMARY control plane (undetected Playwright, channel=chrome) [VERIFIED 2026-06-03]
nodriver                     # FALLBACK control plane: pure-CDP, no Playwright shim          [VERIFIED active; pin a commit — no tags]
# zendriver>=0.15.3          # ALT fallback if you want pinnable semver releases instead of nodriver main [VERIFIED 2026-03-12]
# seleniumbase>=4.49.10      # ESCAPE HATCH: CDP Mode + Turnstile-click + xvfb tooling        [VERIFIED 2026-06-12]
# cloverlabs-camoufox        # SECONDARY (Firefox-only targets) — maintained fork, NOT stock camoufox 0.4.11 (stale 2025-01) [VERIFIED]
```

Tier-1 router engine selection (extends `02-SCRAPING-ENGINE.md §3 route()` — engine, not just tier):

```python
# pipeline/fetch/tiers/tier1.py  — render-to-unlock, then hand cookies down to Tier-0 (curl_cffi)
from enum import Enum

class Engine(Enum):
    PATCHRIGHT = "patchright"   # default: drop-in Playwright API, monthly-maintained
    NODRIVER   = "nodriver"     # escalation: pure-CDP, clears Turnstile-hard / Google / CDP-FP gates
    CAMOUFOX   = "camoufox"     # niche: target rewards Firefox fingerprint (use cloverlabs fork)

# Per-source default; the router/self-tuner (§9.4) overwrites from observed bypass evidence.
ENGINE_FLOOR = {
    "cloudflare": Engine.PATCHRIGHT,   # patchright clears most; escalate to nodriver on Turnstile-hard
    "datadome":   Engine.NODRIVER,     # interstitial only here; full sensor wall is Tier-2 (Hyper+residential)
    "geetest":    Engine.PATCHRIGHT,   # browser + 2Captcha/CapSolver slider solver (§5 engine doc)
    "none":       Engine.PATCHRIGHT,   # only reached if a JS render is needed despite no anti-bot
}
ESCALATION = {Engine.PATCHRIGHT: Engine.NODRIVER}   # on typed block/gate, promote control plane

def make_stealthy(engine: Engine, proxy=None, geo="ES"):
    """Render-to-unlock. ALWAYS headed/xvfb (UC/CDP detectable headless); ALWAYS es-ES locale."""
    if engine is Engine.PATCHRIGHT:
        from scrapling.fetchers import StealthyFetcher   # patchright-backed since v0.3.13  [VERIFIED]
        return StealthyFetcher(
            headless=False,           # headless is a tell for the CDP gate  [VERIFIED]
            block_webrtc=True,
            os_randomize=False,       # law #3: coherence > randomness within a session
            proxy=proxy,
            geoip=True,               # locale/timezone aligned to proxy exit (ES)
            network_idle=True,
        )
    if engine is Engine.NODRIVER:
        import nodriver as uc         # pure CDP; own async API (second code path, on purpose)
        return uc.start(
            browser_executable_path=None,   # real system Chrome (channel=chrome equiv)
            headless=False,
            browser_args=[f"--proxy-server={proxy}"] if proxy else [],
            lang="es-ES",
        )
    # Engine.CAMOUFOX -> cloverlabs-camoufox, Firefox-only fallback; pin the maintained fork.
    raise NotImplementedError("camoufox path: install cloverlabs-camoufox, not stock camoufox 0.4.11")
```

Doctrine reminders baked into the config (all from `02-SCRAPING-ENGINE.md`, unchanged):
- **Render once to unlock, then drain on Tier-0** — capture the page's own XHR to the internal
  API and replay with `curl_cffi` + the warmed `cf_clearance`/`datadome` cookie (§2 dashed arrow).
- **headed/xvfb mandatory** — headless is itself a signal for the CDP gate (SeleniumBase + nodriver
  both confirm). `[VERIFIED]`
- **Tier-1 never touches Akamai `_abck` / PerimeterX / hardened DataDome-sensor** — those are
  Tier-2 (Hyper Solutions sensor-mint + Decodo residential), spend-gated. Browser render there is
  BotBrowser, last resort only. (§2 Tier-2, §5 solver contract — unchanged.)

---

## 6. Is CARDEEP's current choice good enough? — final ruling

- **Wrapper (Scrapling): YES, keep.** Best-maintained tool in the audit; gives patchright +
  adaptive selectors + capture ergonomics in one dep. `[VERIFIED]`
- **Engine claim ("camoufox-driven"): NO, replace.** It is stale: Scrapling moved to patchright,
  and the camoufox pip wrapper is 16 months old with the maintainer on hiatus and a self-admitted
  perf regression. **Primary engine → patchright (via StealthyFetcher); add nodriver/zendriver as
  the named escalation; demote camoufox to the Firefox-only niche (cloverlabs fork).** `[VERIFIED]`
- **Tier-2 render (BotBrowser): YES, unchanged.** Audit confirms it. `[VERIFIED]`
- **rebrowser-patches: DROP.** Stale (13 months) and benchmark-equal to vanilla. `[VERIFIED]`

Net: CARDEEP was on the right *family* but pinned to a backend its own wrapper has already
abandoned. The two-engine CDP-first Tier-1 above is the bulletproof, recency-clean 2026 pick.

---

## 7. Sources (all fetched/verified 2026-06-12)

- Scrapling releases (v0.4.9, 2026-06-07) — github.com/D4Vinci/Scrapling/releases
- Scrapling StealthyFetcher backend = patchright since v0.3.13 — scrapling.readthedocs.io/en/latest/fetching/stealthy.html
- patchright (v1.60.0, 2026-06-03; Runtime.enable/Console.enable patches) — github.com/Kaliiiiiiiiii-Vinyzu/patchright
- nodriver (4.4k★, active, no tagged releases; pure-CDP successor to undetected-chromedriver) — github.com/ultrafunkamsterdam/nodriver
- zendriver (v0.15.3, 2026-03-12; nodriver fork) — github.com/stephanlensky/zendriver
- SeleniumBase (4.49.10, 2026-06-12; UC + CDP Mode) — pypi.org/project/seleniumbase · seleniumbase.io/examples/cdp_mode/ReadMe
- camoufox binary (v150.0.2, 2026-05-11) + hiatus notice + CloverLabs relocation — github.com/daijro/camoufox · camoufox.com/stealth
- camoufox pip stale (0.4.11, 2025-01-29) — pypi.org/project/camoufox
- BotBrowser (149.0.7827.59, 2026-06-09; CF/Akamai/Kasada/DataDome/PX/Imperva profiles) — github.com/MiddleSchoolStudent/BotBrowser
- rebrowser-patches (v1.0.19, 2025-05-09 — STALE) — github.com/rebrowser/rebrowser-patches
- Benchmark A (techinz: patchright 100 / nodriver 80 / camoufox 90 / zendriver 70) — github.com/techinz/browsers-benchmark
- Benchmark B (ianlpaterson 2026-05; nodriver 28/3/0 winner, 7 tools, 31 CF targets, 651 verdicts) — ianlpaterson.com/blog/anti-detect-browser-benchmark-patchright-nodriver-curl-cffi
- 2026 detection-layer model + DataDome 85k per-site ML models + residential-IP necessity — webscrapingapi.com/how-to-bypass-cloudflare · scrapfly.io/blog/posts/how-to-bypass-datadome-anti-scraping
```
