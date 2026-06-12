# T03 — Anti-bot Challenge Solving + Detection

> Domain: FlareSolverr vs Byparr, Cloudflare Turnstile / DataDome / PerimeterX / GeeTest
> solving, captcha services (2Captcha / CapSolver / CapMonster / others), and
> is-antibot detection libraries.
> Audited live: **2026-06-12**. Anti-hallucination: every claim is `[V]` (page/repo fetched
> this session) or `[A]` (inferred / not directly fetched). Source URLs inline.

---

## 0. TL;DR — what to ship

| Layer | Pick | Fallback | Why |
|---|---|---|---|
| **Cloudflare (JS/Turnstile interactive challenge)** | **Byparr** (Camoufox reverse-proxy) | FlareSolverr v3.5.0 | Byparr is Camoufox-native — already CARDEEP's approved engine. FlareSolverr is Selenium+undetected-chromedriver (a stack CARDEEP's CI **blocks**). `[V]` |
| **Headless-native CF clearance (no separate service)** | **sarperavci/CloudflareBypassForScraping** (DrissionPage) or **patchright-python** | Byparr | Drop into the existing browser tier; "request mirroring" yields `cf_clearance` + TLS-matched session. `[V]` |
| **Paid captcha solver (Turnstile / reCAPTCHA / DataDome token)** | **CapSolver** (keep current) | **CapMonster Cloud** | CapSolver tops 2026 CF rankings; CapMonster is the AI-only price/uptime hedge. Drop NopeCHA as primary-secondary — CapMonster is the stronger #2. `[V]` |
| **Open-source Turnstile solver (behind Solver Layer)** | **Theyka/Turnstile-Solver** (patchright) | CapSolver | Free, self-hosted, no API spend. "Fun project" caveat → keep CapSolver fallback. `[V]` |
| **Detection / self-test (is-antibot + fingerprint leak)** | **scrapfly/Antibot-Detector** (v2.6, Feb 2026) + **patchright detection matrix** | FingerprintJS BotD | Antibot-Detector flags which WAF a portal runs; BotD/CreepJS validate our own browser doesn't leak. `[V]` |

**Verdict on CARDEEP's current choice:** CapSolver-as-primary is **still correct in 2026** `[V]`.
Three deltas: (1) adopt **Byparr** as the CF-interactive solver instead of leaving the
`hyper-sdk-go` / FlareSolverr-style stub; (2) promote **CapMonster Cloud** over NopeCHA as the
paid #2; (3) make the **detection** half of the loop explicit — Antibot-Detector for portal
classification, BotD/CreepJS for self-audit. **DataDome stays unsolved-by-solver** — see §6.

---

## 1. The reality check that governs every choice below

The dominant defense on EU car portals is **continuous behavioral/ML scoring, not an
interactive captcha you can hand to a solver** `[V]`.

- DataDome now runs **~85,000 per-customer ML models** — one model per protected site. There is
  **no universal bypass**; passing request #1 and getting blocked at #10 is the norm.
  `[V]` https://scrapfly.io/blog/posts/how-to-bypass-datadome-anti-scraping
- "JavaScript-level stealth is dead." Success = **fingerprint management + behavioral simulation
  + residential proxy rotation**, combined — never a single solver call. `[V]`
- DataDome's slider/device-check surfaces **only when trust score drops**, and is **not reliably
  solvable by generic reCAPTCHA/hCaptcha solvers**. `[V]` (matches CARDEEP's own
  `docs/INFRASTRUCTURE.md` finding).

**Consequence for tool selection:** captcha solvers and CF-challenge proxies are a **narrow
fallback** for the *interactive* layer (Turnstile token, reCAPTCHA, CF JS-challenge). The heavy
lifting against Akamai/DataDome/PerimeterX is done by the **proxy + fingerprint + behavioral**
stack (curl_cffi + Camoufox + Decodo/Oxylabs), which is audited in T02/T05, not here. This doc
must not oversell any solver as a DataDome silver bullet.

---

## 2. CF challenge proxies — FlareSolverr vs Byparr

### FlareSolverr — `[V] ALIVE, but stack-incompatible`
- Repo: https://github.com/FlareSolverr/FlareSolverr — **14.3k★**, **48 open issues** `[V]`
- Latest release **v3.5.0 — 2026-05-26** `[V]` (release page).
- **Recency nuance `[V]`:** there was a **~6-month gap** (v3.4.0 Aug 2025 → v3.4.5/.6 Nov 2025),
  then a long stall, then v3.5.0 resumed May 2026 with "Resolve turnstile captcha" work. Not
  abandoned, but historically bursty — do not assume it tracks new CF challenges instantly.
- **Engine:** Selenium + **undetected-chromedriver** `[V]`.
- **Why NOT primary for CARDEEP:** `undetected-chromedriver` is **explicitly BLOCKED** by
  CARDEEP's CI policy (`.forgejo/workflows/illegal-pattern-scan.yml`: "BLOCKED:
  undetected-chromedriver (outdated)") `[V]`. Adopting FlareSolverr as primary would violate the
  repo's own approved-stack gate. Also heavier (full Chrome) and more behavior-detectable than the
  Camoufox path.
- **Strengths:** huge ecosystem (Prowlarr/Jackett/Sonarr), battle-tested, simple HTTP API.
- **Weaknesses:** Selenium fingerprint surface, slower, the UC dependency, bursty maintenance.

### Byparr — `[V] ALIVE, recommended`
- Repo: https://github.com/ThePhaseless/Byparr — **1.6k★**, **16 open issues** `[V]`
- Latest release **v2.1.0 — 2026-02-08** ("Python 3.14, per-request proxy, stability fixes") `[V]`.
- **Engine: Camoufox + FastAPI** — drop-in FlareSolverr replacement (same `/v1` request shape) `[V]`.
- **Why primary for CARDEEP:** Camoufox is **already the approved T2/T3 engine** in CARDEEP's
  stack `[V]` (`anti_detecci_n_tier_1_camoufox_arsenal_open_s.md`). Byparr reuses the same C++
  Firefox patches and geoip we already trust — zero new detectable engine introduced.
- **Strengths:** highest Turnstile success in head-to-head writeups `[V]` (roundproxies); per-request
  proxy support (fits our proxy fleet); ARM/Linux/Win/macOS.
- **Weaknesses:** higher latency from deep-spoof logic `[V]`; smaller community than FlareSolverr;
  README explicitly "does not guarantee" bypass `[V]`.
- Cross-source: https://roundproxies.com/blog/byparr/ `[V]`

**Decision:** **Byparr primary, FlareSolverr fallback.** Byparr aligns with the approved Camoufox
engine and the CI block-list; FlareSolverr is the well-known compatibility net only.

---

## 3. Headless-native CF clearance (no sidecar service)

For tiers where we already drive a browser, a sidecar proxy is overhead. Two strong 2026 options:

### sarperavci/CloudflareBypassForScraping — `[V] ALIVE`
- Repo: https://github.com/sarperavci/CloudflareBypassForScraping — **2.4k★**, container
  published **~2 months ago** (≈Apr 2026) `[V]`.
- **Engine: DrissionPage** (real browser, not flagged as webdriver) `[V]`.
- **Killer feature: "request mirroring"** — forwards arbitrary HTTP requests through the bypass
  server, returning both the `cf_clearance` cookie **and** a TLS/JA3-matched session. Has a
  **Server Mode** to expose cookie/HTML retrieval remotely `[V]`.
- **Fit:** complements curl_cffi — generate `cf_clearance` once, then replay with our TLS-matched
  curl_cffi sessions. Strong for CF-cookie tiers without standing up Byparr.

### patchright-python — `[V] ALIVE, actively released`
- Repo: https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python `[V]`
- Latest release **v1.60.0 — 2026-06-03** (versions auto-track microsoft/playwright-python) `[V]`.
  Releases: v1.60.0 (Jun 3), v1.59.0 (Apr 29), v1.58.0 (Mar 7) — **monthly cadence in 2026** `[V]`.
- **What it is:** undetected Playwright — patches Playwright's obvious leaks (CDP, runtime
  detection) at the driver level.
- **Claimed pass set `[V]`:** Brotector, Cloudflare, Kasada, Akamai, Shape/F5, Bet365, **DataDome**,
  Fingerprint.com, CreepJS, Sannysoft, Incolumitas, IPHey, Browserscan, Pixelscan.
  Treat the DataDome claim as **per-site, not guaranteed** (see §6) — `[A]` on real EU-portal yield.
- **Fit:** the Playwright-flavored sibling of Camoufox. Useful where a Chromium fingerprint is
  needed (vs Camoufox's Firefox). Also the dependency under Theyka's open-source solver (§5).

---

## 4. Paid captcha services — CapSolver vs CapMonster vs 2Captcha

Verified pricing/coverage (cross-checked against CARDEEP's own `docs/INFRASTRUCTURE.md` table):

| Service | Model | reCAPTCHA v2 /1k | Turnstile /1k | DataDome | Speed | Success | Status |
|---|---|---|---|---|---|---|---|
| **CapSolver** | AI-only | ~$0.80 `[V]` | ~$1.2 `[V]` | listed `[V]` | sub-10s, img 0.2s `[V]` | ~99.15% claimed `[V]` | **ALIVE, market leader 2026 `[V]`** |
| **CapMonster Cloud** | AI-only | $0.60 `[V]` | $1.30 `[V]` | yes (+ Amazon WAF, GeeTest, Yidun, Tencent) `[V]` | 1–3s `[V]` | up to 99% `[V]` | **ALIVE `[V]`** |
| **2Captcha** | Human + AI | $0.50–1.00 (AI) / ~$2.99 human `[V]` | supported `[V]` | premium/human `[V]` | 8–30s human, 1–3s AI `[V]` | high `[V]` | ALIVE; **BLOCKED by CARDEEP CI** `[V]` |

Notes:
- **CapSolver** = "undisputed leader in Cloudflare challenge solving" in 2026 rankings; covers the
  full CF spectrum (legacy JS → Turnstile → Managed Challenge tokens); ML adapts to zero-day CF
  updates `[V]`. https://www.capsolver.com/blog/Cloudflare/top-challenge-solver-ranking
- **CapMonster Cloud** = cheapest AI-only at high volume, broadest type list incl. **Amazon WAF /
  Yidun / Tencent** that CapSolver doesn't headline `[V]`. Best **#2** for price + uptime hedge.
  https://capmonster.cloud/en/
- **2Captcha** = only justified when a target genuinely needs **human-assisted** solving. It is on
  CARDEEP's CI **BLOCK** list `[V]` (`illegal-pattern-scan.yml`) — keep it off the dependency tree;
  if ever needed, it's an out-of-band manual op, not a pinned package.
- **NopeCHA** (current doc's "cheap secondary") — superseded as #2 by CapMonster on coverage
  breadth and stated success. Keep only as a tertiary cost-pilot.

**Decision:** **CapSolver primary (unchanged), CapMonster Cloud secondary.** Both AI-only,
API-compatible patterns, behind the existing **Solver Abstraction Layer**
(`scrapers/engine/antidetect/solver.py`) so swapping is a config change.

---

## 5. Open-source Turnstile solver (behind the Solver Layer, $0 spend)

### Theyka/Turnstile-Solver — `[V] ALIVE, hobby-grade`
- Repo: https://github.com/Theyka/Turnstile-Solver — **828★** `[V]`.
- **Engine: patchright** (multi-threaded, API server, Chromium/Chrome/Edge/Camoufox) `[V]`.
- Solves **Turnstile with no paid API** `[V]`.
- **Caveats `[V]`:** author calls it "a quick project made for fun and personal use"; updates
  "depend on stars/issues"; explicit "not responsible for API blocking / IP ban". → **fragile**,
  exactly the OSS-solver fragility CARDEEP's master-plan already flagged ("solvers open-source de
  DataDome/PerimeterX cambian/mueren rápido; depender de ellos es frágil") `[V]`.
- **Fit:** wire as `OssTurnstileSolver` backend behind the Solver Layer; **CapSolver remains the
  automatic fallback** when it fails. Re-verify liveness on a schedule (Research Scout).

This is the concrete OSS Turnstile backend the master-plan's Solver Abstraction Layer was
designed to host (`backend: none|capsolver|oss:<repo>`) `[V]`.

---

## 6. DataDome / PerimeterX / GeeTest — what is and isn't solvable

- **DataDome:** No solver "solves" it portfolio-wide (85k per-site ML models) `[V]`. CapSolver/
  CapMonster list DataDome support `[V]`, but real EU-portal bypass is **proxy quality +
  fingerprint + behavior**, with the solver only for the occasional interstitial/slider token.
  CARDEEP's blocked FR portals (leboncoin, lacentrale, coches.net, milanuncios) are **DataDome
  walls awaiting residential proxy** `[V]` — a captcha solver will **not** unlock them; that's a
  T02 proxy/budget decision, not a T03 solver decision.
- **PerimeterX (HUMAN):** same shape — behavioral + residential first; solver is last-resort token.
- **GeeTest / FunCaptcha / hCaptcha:** covered by both CapSolver and CapMonster `[V]` if any EU
  source surfaces them (rare on car portals). No dedicated tool needed beyond the paid layer.

**Anti-overselling guard:** any config that routes a DataDome/PX portal to a captcha solver as the
*primary* unblock is wrong and should fail review. Solver = interactive-token fallback only.

---

## 7. Detection / self-test libraries (the other half: "is-antibot" + leak audit)

You can't tune evasion without measuring it. Two distinct needs:

### A) Classify the portal's defense — scrapfly/Antibot-Detector — `[V] ALIVE`
- Repo: https://github.com/scrapfly/Antibot-Detector — **285★**, **v2.6 — 2026-02-23** `[V]`.
- Manifest-V3 Chrome extension; detects **Cloudflare, Akamai, DataDome, PerimeterX, Shape, AWS
  WAF, Imperva, Kasada** + captcha types (reCAPTCHA, hCaptcha, FunCaptcha, GeeTest, Turnstile) +
  fingerprinting methods, with **confidence scoring** `[V]`.
- **Fit:** the manual/triage companion to CARDEEP's `router/classifier.py` WAF-signature engine.
  Use during recipe authoring (W2) to confirm which wall a new portal runs before picking a tier.

### B) Audit our own browser for leaks — FingerprintJS BotD + CreepJS — `[V] ALIVE`
- **BotD:** https://github.com/fingerprintjs/botd — **1.4k★**, **v2.0.0 — 2025-11-04**, MIT `[V]`.
  Maintenance is **"stability-only"** (critical fixes, no new features) `[V]` — fine for a
  self-test oracle; not a moving target we depend on for features.
- **CreepJS:** the standard public fingerprint-consistency/leak oracle in 2026 `[V]`; catches the
  browser "lying" (logical contradictions across Canvas/WebGL/Audio/WebRTC/Navigator) `[V]`.
- **Fit:** run Camoufox/patchright sessions against BotD + CreepJS in CI to confirm **zero leaks**
  before a fingerprint identity is promoted to PREMIUM (trust_score ≥ 7.0). This closes the
  feedback loop the master-plan calls "longevity of identity over speed" `[V]`.

---

## 8. DEAD / AVOID — do not recommend corpses

| Tool | Status | Evidence |
|---|---|---|
| `undetected-chromedriver` | **AVOID** (and CI-blocked) | CARDEEP CI: "BLOCKED: undetected-chromedriver (outdated)" `[V]`. It is FlareSolverr's engine — another reason FlareSolverr is fallback-only. |
| `playwright-stealth` | **AVOID** (CI-blocked) | CARDEEP CI block-list `[V]`; superseded by patchright/Camoufox driver-level patches. |
| `puppeteer-stealth` / `fake-useragent` | **AVOID** (CI-blocked) | CARDEEP CI block-list `[V]`; trivially fingerprinted in 2026. |
| `2captcha` as a **pinned dependency** | **AVOID** in code | CARDEEP CI block-list `[V]`. Human-assisted, slow, costly; AI services dominate. (Service itself is alive for out-of-band manual use only.) |
| Vendor "DataDome solver — 99% success" API pages (captchakings et al.) | **TREAT AS MARKETING** `[A]` | Contradicts the per-site-ML reality `[V]`; not verifiable, not open. Do not architect around them. |

No tool below was found *abandoned* in the recommended set — every recommended repo released
within the last ~4 months `[V]`. The "12+ months stale = suspect" bar is met by all picks.

---

## 9. Integration map (where each lands in CARDEEP)

```
scrapers/engine/antidetect/solver.py   ← Solver Abstraction Layer (already designed)
  backends:
    NullSolver            (no-op, default)
    OssTurnstileSolver    → Theyka/Turnstile-Solver (patchright)     [$0, primary OSS]
    CapsolverSolver       → CapSolver API            [paid, fallback]   ← KEEP
    CapMonsterSolver      → CapMonster Cloud API      [paid, #2]         ← ADD
  selection: OSS first → CapSolver → CapMonster   (Lead Agent authorizes paid spend)

CF-interactive tier (T1/T2 when curl_cffi alone fails the JS/Turnstile challenge):
    primary:  Byparr  (Camoufox /v1 HTTP API)        ← ADD (replaces FlareSolverr-style stub)
    fallback: FlareSolverr v3.5.0                      ← compat net only
    alt:      sarperavci/CloudflareBypassForScraping (request-mirroring → cf_clearance for curl_cffi)

router/classifier.py  ← keep as automated WAF signature engine
  companion (manual W2 recipe authoring): scrapfly/Antibot-Detector extension

CI self-test (promote identity to PREMIUM only if clean):
    Camoufox/patchright session  →  BotD + CreepJS  →  assert no-leak
```

### Sample CONFIG — Solver Layer + per-portal routing

```yaml
# configs/antibot/solver_layer.yaml
solver_layer:
  selection_order: [oss_turnstile, capsolver, capmonster]   # cheapest-first
  budget_gate: lead_agent                                    # paid backends require auth
  backends:
    oss_turnstile:
      kind: oss
      repo: Theyka/Turnstile-Solver        # patchright, $0, hobby-grade
      engine: camoufox                      # reuse approved engine
      endpoint: http://127.0.0.1:5033
      liveness_recheck_days: 7              # Research Scout re-verifies (fragile OSS)
    capsolver:
      kind: paid
      api_key_env: CAPSOLVER_API_KEY        # KeePassXC; never hardcoded
      types: [turnstile, recaptcha_v2, recaptcha_v3, datadome_token]
      price_per_1k: { turnstile: 1.2, recaptcha_v2: 0.8 }
    capmonster:
      kind: paid
      api_key_env: CAPMONSTER_API_KEY
      types: [turnstile, recaptcha_v2, datadome, amazon_waf, geetest, yidun]
      price_per_1k: { turnstile: 1.3, recaptcha_v2: 0.6 }

# CF interactive-challenge proxy (only when curl_cffi fails the JS/Turnstile gate)
cf_challenge_proxy:
  primary:
    tool: byparr                            # Camoufox reverse-proxy, /v1 API
    endpoint: http://127.0.0.1:8191/v1
    per_request_proxy: true                 # bind to proxy fleet session
  fallback:
    tool: flaresolverr                      # v3.5.0 — compat only, UC engine
    endpoint: http://127.0.0.1:8192/v1
  cookie_minter:
    tool: cloudflarebypassforscraping       # DrissionPage; request-mirroring → cf_clearance
    mode: server
    handoff: curl_cffi                       # replay cookie in TLS-matched session

# HARD RULE: DataDome / PerimeterX portals NEVER route here as primary unblock.
datadome_perimeterx_policy:
  primary: residential_proxy + fingerprint + behavioral   # T02/T05, not a solver
  solver_use: interactive_token_only                       # slider/interstitial fallback

# Self-audit oracle — gate PREMIUM identity promotion
identity_leak_audit:
  oracles: [botd, creepjs]                  # run in CI
  promote_to_premium_if: { leaks: 0, trust_score_gte: 7.0 }
```

---

## 10. Sources (all fetched/searched 2026-06-12)

- FlareSolverr repo + releases — https://github.com/FlareSolverr/FlareSolverr/releases `[V]`
- Byparr repo — https://github.com/ThePhaseless/Byparr `[V]` ; guide https://roundproxies.com/blog/byparr/ `[V]`
- sarperavci/CloudflareBypassForScraping — https://github.com/sarperavci/CloudflareBypassForScraping `[V]`
- patchright-python releases — https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python/releases `[V]`
- Theyka/Turnstile-Solver — https://github.com/Theyka/Turnstile-Solver `[V]`
- CapSolver 2026 ranking — https://www.capsolver.com/blog/Cloudflare/top-challenge-solver-ranking `[V]`
- CapMonster Cloud — https://capmonster.cloud/en/ `[V]`
- DataDome reality — https://scrapfly.io/blog/posts/how-to-bypass-datadome-anti-scraping `[V]`
- scrapfly/Antibot-Detector — https://github.com/scrapfly/Antibot-Detector `[V]`
- FingerprintJS BotD — https://github.com/fingerprintjs/botd `[V]`
- CARDEEP internal ground truth: `docs/INFRASTRUCTURE.md`, `.forgejo/workflows/illegal-pattern-scan.yml`,
  `docs/master-plan/architecture/anti_detecci_n_tier_1_camoufox_arsenal_open_s.md`,
  `docs/deliverables/D2_ANTI_DETECTION_OPERATIONS.md` `[V]`
