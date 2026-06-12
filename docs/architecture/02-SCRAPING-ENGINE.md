# CARDEEP — 02 · The Elite Scraping Engine

> Pillar document. The tiered fetch engine, per-defense routing, recipe system and
> self-healing that let Cardeep drain the inventory of 100% of Spain's car
> points-of-sale — from the open marketplace to the Akamai-walled OEM portal —
> without artisanal per-source work and without the engine ever falling.
>
> **Supersedes** the first-pass scrape doctrine in `docs/workflows/README.md §FASE 2`
> and replaces the `urllib`-based `fetch_page` currently living in
> `pipeline/sources/autoscout24.py`. Mark of this doc: every external claim is
> `[VERIFIED]` (read from source / fetched live) or `[ASSUMED]` (inferred, to be
> tested). No placeholders, no stubs.
>
> Anchor reality (read before designing): `docs/research/SOURCES_ES.md` (181-source
> census), `docs/ARCHITECTURE.md` (data layer), `pipeline/sources/*.py` (current code).

---

## 0. The embarrassment we are deleting

The current production fetch path is **plain `urllib`** with a hardcoded Chrome
User-Agent string (`pipeline/sources/autoscout24.py:19`, `:61-81`). `[VERIFIED]`
This is wrong on three axes and every one of them is a wall we will hit at scale:

1. **No TLS impersonation.** `urllib` over OpenSSL emits a Python-shaped ClientHello.
   Its JA3/JA4 does not match any browser. AutoScout24 already serves it today only
   because AS24 is *open* (no real WAF on `/lst`) — the census itself notes AS24
   "bloquea UA Anthropic; OK con UA Chrome" `[VERIFIED, SOURCES_ES.md §2.1]`, i.e. it
   gates on the UA *header* alone. The moment we point this client at Cloudflare
   (autocasion), Imperva (coches.com latent), DataDome, Akamai (spoticar, audi.es) or
   GeeTest (milanuncios), the TLS layer alone gets us a 403 before a byte of HTML.
2. **No post-quantum key share.** Current Chrome (≥131) sends an `X25519MLKEM768`
   key share in the ClientHello. `[VERIFIED]` Anti-bot vendors now treat the *absence*
   of that key share as a high-confidence bot signal — "the post-quantum key share is
   a new signal most scrapers don't send" and "JA4 now carries post-quantum key-share
   information." `[VERIFIED, scrapfly.io post-quantum-tls-bot-detection]` A 2024-era TLS
   profile fails even with a perfect UA.
3. **HTML pagination as the access strategy.** The code drains `/profesionales/{slug}?page=N`
   and even documents the hazard it creates: a non-stably-sorted live set "fabricates
   duplicates / drops across page boundaries" `[VERIFIED, autoscout24.py:62-63]`. Fighting
   HTML pagination is fighting the wrong surface. The data already lives in
   `__NEXT_DATA__` — a data-layer artifact — and most Tier-1 platforms expose an even
   cleaner internal JSON/GraphQL API (wallapop `api.wallapop.com/api/v3/cars/search`,
   coches.net `ms-mt--api-web.spain.advgo.net/search`) `[VERIFIED, SOURCES_ES.md §2.2]`.

The redesign inverts all three: **session-coherent current-Chrome TLS impersonation by
default, escalating browser stealth only when a JS/sensor challenge demands it, always
aimed at the data layer.**

---

## 1. Doctrine (the five laws, in priority order)

These govern every fetch decision. When they conflict, lower number wins.

1. **TARGET THE DATA LAYER, NEVER FIGHT HTML.** For every source, the recipe-hunt's
   first job is to find the internal API / GraphQL endpoint / `__NEXT_DATA__` /
   `application/ld+json` / XML sitemap that already carries the structured records.
   HTML scraping with CSS selectors is the *fallback of last resort*, used only when no
   data-layer surface exists. Rationale: data-layer surfaces are stabler (typed fields,
   no layout drift), cheaper (one JSON request vs N rendered pages), and often less
   defended than the human-facing HTML (an internal `/api/v3/cars/search` frequently
   answers a correct-fingerprint `curl_cffi` while the SRP HTML sits behind Turnstile).

2. **CHEAPEST TIER THAT WORKS.** Always attempt Tier-0 (`curl_cffi`) first. Escalate to
   Tier-1 (stealth browser) only on a *typed* failure signal (challenge fingerprint, JS
   gate, empty data-layer that requires render). Escalate to Tier-2 (paid proxies +
   sensors) only behind the owner's explicit spend gate. Cost is a first-class routing
   input: §6 of the orchestration doctrine — "lo masivo y barato → determinista/local;
   la inteligencia cara → solo para decidir." `[VERIFIED, ORQUESTACION.md]`

3. **SESSION-LEVEL FINGERPRINT COHERENCE.** Within one harvest session the TLS
   fingerprint, HTTP/2 SETTINGS + header order, User-Agent, `Accept-*` headers,
   `Sec-CH-UA*` client hints, and (Tier-2) exit IP must describe **one** consistent
   browser+device+network. A request that impersonates Chrome 131 TLS but sends a
   Chrome 120 UA, or rotates IP mid-session, is a self-inflicted bot signal. One session
   = one identity, start to finish.

4. **BEAT PAGINATION WITH FACETS + STABLE SORT, NOT DEEPER PAGES.** Aggregators cap
   pagination (commonly ~1000–2000 results / ~20 pages). A dealer or a province with
   more stock than the cap is *un-drainable by paging alone*. The engine partitions the
   query space by orthogonal facets (price band, year band, make, fuel, postcode prefix)
   until every partition fits under the cap, and within each partition uses a **stable
   total sort** (deterministic tiebreak, e.g. `sort=price&desc=1` or an id sort) so page
   boundaries are reproducible and no record is duplicated or dropped. Union the
   partitions, dedup by stable id. (§7)

5. **CURRENT-CHROME FLOOR, ROTATE ON A CADENCE.** The impersonation target is *current
   stable Chrome*, never a pinned old version. JA3/JA4 profiles rot as Chrome ships
   (~6-week release train); a profile that was invisible last quarter becomes a flag.
   The engine carries a single `IMPERSONATE_TARGET` constant, health telemetry watches
   for a fingerprint-correlated rise in challenge rate, and the **X25519MLKEM768 key
   share is mandatory** (watch it specifically — it is the current highest-signal TLS
   discriminator `[VERIFIED]`). (§8)

---

## 2. The tiered fetch engine

```
                         ┌─────────────────────────────────────────────────┐
   source request  ──▶   │  ROUTER  (is-antibot fingerprint + recipe.tier)  │
                         └───────────────┬──────────────┬──────────────────┘
                                         │              │
       ┌─────────────────────────────────┘              └───────────────────────┐
       ▼                                                                          ▼
┌───────────────┐   typed challenge   ┌──────────────────────┐   sensor wall  ┌──────────────────┐
│ TIER-0  FETCH │ ─────signal──────▶  │ TIER-1  STEALTH BROWSER│ ───(spend)──▶ │ TIER-2  HEAVY    │
│ curl_cffi     │                     │ Scrapling Stealthy /   │               │ residential IP   │
│ TLS/JA3/JA4   │ ◀──promote/demote── │ camoufox               │               │ + sensor gen     │
│ HTTP/2+H3     │                     │ (CF/Turnstile/DataDome)│               │ (Akamai/PX/DD)   │
└───────┬───────┘                     └───────────┬────────────┘               └────────┬─────────┘
        │ raw bytes / JSON                         │ rendered DOM + captured XHR          │ tokens+cookies
        └──────────────────────────┬───────────────┴──────────────────────────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │  EXTRACTOR (recipe)  │  data-layer JSON path / JSON-LD / sitemap
                         │  + self-heal (§9)    │  → fallback adaptive CSS (Scrapling)
                         └──────────┬───────────┘
                                    ▼
                         normalized records → pipeline/ingest.py (delta engine, unchanged)
```

The three tiers are a **strict cost/capability ladder**. A source is pinned to its
*minimum sufficient* tier in its recipe; the router may escalate at runtime on a typed
signal and records the escalation back into the recipe (self-tuning, §9.4).

### Tier-0 — `curl_cffi` (the workhorse, ~90% of all requests)

- **Engine:** `curl_cffi` (lexiforest fork of curl-impersonate via cffi). `[VERIFIED,
  github.com/lexiforest/curl_cffi]` Impersonates browser TLS/JA3, HTTP/2 SETTINGS +
  pseudo-header order, supports HTTP/3, async with per-request proxy rotation, websockets.
  `[VERIFIED, websearch 2026-06]`
- **Impersonation target:** `impersonate="chrome"` (alias → latest supported Chrome, so
  we ride the version train automatically) `[VERIFIED]`, with an explicit pin
  (`chrome131`+) available for reproducibility audits. JA4 is covered because curl_cffi
  "impersonates the entire hello packet, and ja4 is just part of it." `[VERIFIED]`
- **Targets:** JSON/internal-API/GraphQL surfaces, `application/ld+json`, XML sitemaps,
  and open SSR HTML (`__NEXT_DATA__`). This is the surface for: every OEM JSON API (Kia,
  MG, BYD, Mercedes OneWeb…), the open platforms (AS24, autocasion, coches.com sitemap,
  motorflash), and the *internal APIs* of several Tier-1s (wallapop search API returns 200
  to a correct-fingerprint client; coches.net advgo search answers a POST). `[VERIFIED,
  SOURCES_ES.md §2]`
- **Why it suffices here:** these surfaces gate on TLS + headers + IP reputation, not on
  JS execution. A coherent current-Chrome fingerprint from a clean IP clears them at
  near-zero cost and full throughput.
- **Cost:** €0 (no proxy at Tier-0 unless IP-reputation-gated; then datacenter pool first).

### Tier-1 — Scrapling `StealthyFetcher` (JS render + soft challenges)

> **Stealth-engine reconciliation `[adversarial GAP-20 — MASTER_PLAN C-12 governs]`.** T02
> (the live-benchmarked tooling authority) supersedes this section's earlier "camoufox-driven"
> framing: Scrapling swapped its `StealthyFetcher` backend to **`patchright`** at v0.3.13, and the
> camoufox pip wrapper is ~16 months stale (maintainer on medical hiatus). **Canonical: the primary
> injector is `patchright` (the Scrapling default); camoufox is demoted to an OPTIONAL, pinned,
> vendored injector** used only where a probe proves patchright is fingerprintable on a specific
> target; **nodriver is allowed ONLY vendored at a pinned commit SHA** (never `@main` — a CI check
> forbids unpinned VCS deps). The engine is injector-agnostic behind `engine/fetch/tiers/`, so the
> swap is a one-file change. Any "camoufox-driven StealthyFetcher" phrasing below resolves to
> "patchright-driven StealthyFetcher".

- **Engine:** Scrapling `StealthyFetcher` (patchright backend ≥ Scrapling 0.3.13). `[VERIFIED,
  scrapling.readthedocs.io stealthy; T02]` It "bypasses all types of
  Cloudflare's Turnstile/Interstitial automatically, bypasses CDP runtime leaks and
  WebRTC leaks, isolates JS execution, removes Playwright fingerprints." `[VERIFIED,
  websearch 2026-06]` For Chromium-shaped needs, `DynamicFetcher` (Playwright, ~60%
  faster in current builds) `[VERIFIED]`; **camoufox (pinned/vendored)** is the Firefox-shaped
  fallback only when a target fingerprints Chromium specifically.
- **Targets:** JS-rendered SPAs with no usable data-layer surface, and soft anti-bot:
  **Cloudflare (managed challenge / Turnstile)**, **DataDome** (when it serves an
  interstitial, not a hard sensor wall), GeeTest slider (with solver, §5).
- **Doctrine inside Tier-1:** *still target the data layer.* The browser's job is to
  pass the challenge and obtain the clearance cookie / execute the bootstrap JS, **then
  capture the page's own XHR/fetch to the internal API** (via response interception) and
  replay that endpoint — ideally handing the warmed cookie jar + fingerprint back down to
  Tier-0 for the bulk drain. Render once to unlock, drain cheap. This is the
  "promote to unlock, demote to drain" pattern (§2 ladder, dashed arrow).
- **Cost:** CPU/RAM only (headed browser per session); no proxy spend unless IP-gated.

### Tier-2 — Heavy: residential proxies + sensor generation (spend-gated, hardest only)

- **Trigger:** reserved for defenses that **cannot** be cleared by fingerprint + render
  alone — primarily **Akamai Bot Manager** (`_abck` requires a valid `sensor_data`
  telemetry payload), **PerimeterX/HUMAN**, **Imperva/Incapsula** when hardened, and
  **DataDome** when it demands a fully-formed device-motion sensor payload. These also
  score **IP reputation** heavily, so datacenter IPs lose regardless of fingerprint.
- **Components (each behind the owner spend gate):**
  - **Residential / mobile proxies — Decodo (formerly Smartproxy).** 115M+ IPs, 195+
    locations, from ~$2/GB at volume (PAYG ~$8.50/GB, entry ~$3.75/GB). `[VERIFIED,
    decodo.com pricing]` Spanish-geo exit IPs are mandatory for geo-sensitive walls —
    the census notes milanuncios "fuera de ES dispara muro." `[VERIFIED, SOURCES_ES.md
    §2.2]` Decodo also offers a Site Unblocker / Web Scraping API (handles CAPTCHA + JS +
    rotation as one REST call) as an all-in-one escape hatch. `[VERIFIED]`
  - **Sensor generation — Hyper Solutions** (`hyper-sdk-py`). API/SDK that generates
    valid Akamai `sensor_data` → `_abck` cookies, plus Incapsula/Kasada/DataDome, *no
    browser required*, faster than browser automation. `[VERIFIED, github.com/Hyper-Solutions/hyper-sdk-py,
    hypersolutions.co]`
  - **CAPTCHA / token solvers — 2Captcha or CapSolver** for DataDome/GeeTest/Turnstile
    interactive challenges when render+solver is needed. `[VERIFIED, websearch 2026-06]`
  - **Patched browser — BotBrowser** (patched Chromium) as the render engine of last
    resort against CF/Akamai/Kasada/DataDome/PX/Imperva when camoufox is detected.
    `[VERIFIED, SOURCES_ES.md §4]`
- **Doctrine inside Tier-2:** sensor generation (Hyper) is preferred over full browser
  automation wherever the wall is *cookie-issuance* (Akamai `_abck`, Incapsula) because
  it is cheaper and faster and lets the bulk drain run on Tier-0 with the minted cookie.
  Full BotBrowser render is the fallback when the wall needs live DOM + behavior.
- **The mint-then-drain pattern is SCOPED, not universal `[adversarial GAP-19]`.** "Render once to
  unlock, capture the clearance cookie, hand it down to Tier-0 curl for the bulk drain" works for
  **cookie-ISSUANCE walls** (passive Cloudflare, Incapsula) where one cookie unlocks a session. It
  does **NOT** beat **full-sensor walls**. Web-verified: DataDome runs 85,000+ per-customer ML models
  scoring ~5T signals/day at the **request level** (TLS + IP + JS + behavior + motion), and Akamai's
  `_abck` is **invalidated the instant `sensor_data` stops matching the live request fingerprint** —
  so a clearance cookie replayed from a datacenter IP at curl-pace with zero mouse motion **re-scores
  as bot on the NEXT request**. Consequence: a 50k-listing Akamai drain (e.g. Spoticar) is **NOT one
  sensor mint then cheap — it is N sensor calls METERED PER PAGE.** Each source therefore carries a
  `wall_class ∈ {cookie-issuance, full-sensor}`: cookie-issuance uses mint-then-drain; full-sensor is
  **cost-modeled per request** (`pages × sensor_cost_per_call`, the authorization basis — MASTER_PLAN
  §5.1 G-A19), changing the Tier-2 cost estimate by orders of magnitude. The prior doc quoted Akamai's
  per-request `_abck` invalidation (00 §T1) but did not carry its consequence into the drain cost; it
  does now.
- **Hard rule:** **no Tier-2 component is invoked without the owner's explicit per-source
  spend authorization.** A source that requires Tier-2 and lacks authorization is parked
  in `state/tier1-blocked.json` with the *exact* wall (e.g. "Akamai `_abck`, sensor_data
  v3, Spanish residential IP required") — never silently retried, never faked. This is
  the `S-TIER1` "reporta método reproducible o el muro exacto que exige gasto." `[VERIFIED,
  ORQUESTACION.md WF-TIER1-HUNT]`

---

## 3. Per-source auto-routing (`is-antibot` + `browsers-benchmark`)

The router decides the tier *per source*, grounded in **data, not reputation**.

- **Fingerprinting:** `is-antibot` probes a source URL and classifies its defense
  (none / Cloudflare / DataDome / Akamai / PerimeterX / Imperva / GeeTest) from response
  headers, challenge bodies, set-cookie names (`_abck`=Akamai, `datadome`=DataDome,
  `cf_clearance`/`__cf_bm`=Cloudflare, `incap_ses`/`visid_incap`=Imperva,
  `_px*`=PerimeterX), status codes and challenge HTML signatures. `[VERIFIED, SOURCES_ES.md §4]`
- **Tool choice:** the classified defense maps to a winning tool+config via the table in
  §4, and the *cost-effectiveness* of each engine against each defense is grounded in
  `browsers-benchmark` empirical data — never on a tool's fame. `[VERIFIED, SOURCES_ES.md §4]`
- **Persistence:** the classification + chosen tier is written into the source's recipe
  (`defense:` + `tier:` fields, §9) and cached in `entity.website_waf` for entity-level
  scraping `[VERIFIED, ARCHITECTURE.md entity.website_waf]`. Re-classified on a cadence and
  on any challenge-rate spike.

Routing decision (pseudocode):

```python
def route(source) -> Tier:
    defense = is_antibot.classify(source.probe_url)         # data-driven label
    recipe  = load_recipe(source.key)                       # may already pin a tier
    tier    = max(recipe.min_tier, DEFENSE_FLOOR[defense])  # never below known floor
    if tier is Tier.HEAVY and not spend_gate.authorized(source.key):
        park(source, wall=defense, reason="spend gate"); return Tier.BLOCKED
    return tier

DEFENSE_FLOOR = {
    "none":        Tier.T0,   # open SSR/JSON/sitemap → curl_cffi
    "cloudflare":  Tier.T1,   # try T0 first (often clears on TLS+UA); floor T1 on challenge
    "imperva":     Tier.T1,   # latent → T0; hardened → T1/T2
    "geetest":     Tier.T1,   # browser + slider solver
    "datadome":    Tier.T1,   # interstitial → T1; full sensor wall → T2
    "perimeterx":  Tier.T2,   # IP-rep + sensor
    "akamai":      Tier.T2,   # _abck sensor_data → Hyper + residential
}
```

> `cloudflare`/`imperva`/`datadome` floors are *optimistic*: the router still attempts
> Tier-0 once (a correct current-Chrome fingerprint clears Cloudflare's passive checks
> and Imperva-latent outright — census: autocasion "Cloudflare permisivo", coches.com
> "Imperva latente pero sirve sitemap+PDP a curl" `[VERIFIED]`) and only escalates on a
> *typed challenge response*. Optimism is free; escalation is on evidence.

---

## 4. Per-defense winning tool + config table

The operational heart. Each row: the classified defense → the cheapest engine that beats
it → the load-bearing config knobs. Tier is the *floor*; the router still tries cheaper
first where the floor is optimistic.

| Defense | Cookie/signal tells | Winning engine (floor tier) | Critical config | Cardeep sources |
|---|---|---|---|---|
| **None (open)** | no challenge; 200 to clean client | `curl_cffi` **T0** | `impersonate="chrome"`; HTTP/2; session-stable headers; X25519MLKEM768 present | AS24, autocasion (listings), coches.com sitemap, motorflash, all OEM JSON APIs, renew |
| **Cloudflare** | `cf_clearance`, `__cf_bm`; JS/managed challenge or Turnstile | T0 first → `curl_cffi`; on challenge **T1** Scrapling `StealthyFetcher` (camoufox) | curl_cffi clears passive CF often; StealthyFetcher auto-solves Turnstile/Interstitial `[VERIFIED]`; reuse `cf_clearance` cookie on T0 for bulk drain | autocasion, clicars, autohero |
| **DataDome** | `datadome` cookie; `/js/` interstitial or device-motion CAPTCHA | T1 `StealthyFetcher` (interstitial) → **T2** Hyper DataDome / CapSolver + Decodo residential (full sensor wall) | DataDome scores TLS+browser FP+**31 mouse-motion signals**+IP rep `[VERIFIED]`; need humanlike motion or generated sensor + residential IP | (platforms that harden; classify live before drain) |
| **Akamai Bot Manager** | `_abck`, `bm_sz`, `ak_bmsc`; 403 even on sitemap | **T2** Hyper Solutions `sensor_data`→`_abck` + Decodo residential; BotBrowser render fallback | `_abck` valid only if `sensor_data` telemetry matches the *observed request fingerprint* exactly — one mismatch invalidates instantly `[VERIFIED]`; sensor_data v3 deobfuscator is a trap (scoring shifts) `[VERIFIED]` → use maintained Hyper API, not a public deobf | spoticar (403 hard), audi.es, Das WeltAuto UA-gated, Spoticar VO |
| **PerimeterX / HUMAN** | `_px`, `_pxhd`, `_pxvid` | **T2** sensor gen + Decodo residential; BotBrowser fallback | IP reputation heavy → Spanish residential mandatory; often co-deployed with Turnstile/Akamai `[VERIFIED]` | (classify live) |
| **Imperva / Incapsula** | `incap_ses_*`, `visid_incap_*`; `___utmvc` JS | T0 first (latent) → **T1/T2** Hyper Incapsula on hardening | coches.com serves to curl while latent → **drain now before it hardens** (census directive `[VERIFIED]`); on hardening, Hyper Incapsula cookie | coches.com |
| **GeeTest** | gt/challenge params; slider/icon CAPTCHA | **T1** Scrapling/DynamicFetcher + 2Captcha/CapSolver GeeTest solver | geo-sensitive: ES residential reduces challenge frequency; solve slider trajectory `[VERIFIED]` | milanuncios (405 GeeTest to curl; "fuera de ES dispara muro") |

**Internal-API shortcut (applies across the table):** before deciding a tier from the
*HTML* defense, the recipe-hunt checks whether the platform's internal API is *less*
defended than its HTML. Empirically true for the Adevinta family: coches.net SRP HTML is
Lambda@Edge-walled (405) but `ms-mt--api-web.spain.advgo.net/search` answers a POST, and
wallapop's `api/v3/cars/search` returns 200 to a correct-fingerprint client with geo
headers `[VERIFIED, SOURCES_ES.md §2.2]`. Where the API is open, the source drops to **T0
regardless of its HTML defense label** — the single highest-leverage move in the engine.

---

## 5. Solver & sensor integration contract

All Tier-2 helpers sit behind one narrow interface so the engine never couples to a
vendor. Each call is metered (records cost) and gated (records authorization).

```python
class ChallengeSolver(Protocol):
    def akamai_sensor(self, page_url, abck, bm_sz, ua) -> str: ...      # Hyper → sensor_data
    def datadome(self, page_url, dd_cookie, ua, proxy) -> dict: ...     # Hyper/CapSolver
    def incapsula(self, page_url, script, ua) -> str: ...               # Hyper
    def geetest(self, gt, challenge, page_url) -> dict: ...             # 2Captcha/CapSolver
    def turnstile(self, sitekey, page_url) -> str: ...                  # solver fallback

class ProxyPool(Protocol):
    def lease(self, geo="ES", kind="residential", sticky=True) -> ProxyLease: ...
```

- **Preferred path = mint-then-drain:** for cookie-issuance walls (Akamai, Incapsula),
  call the sensor API once to mint the clearance cookie, inject it into a Tier-0
  `curl_cffi` session pinned to the *same* proxy IP + UA, and drain the data layer cheap.
  Browser render is the fallback only when live DOM/behavior is unavoidable.
- **Cost ledger:** every solver/proxy call writes `{source_key, vendor, units, est_cost,
  ts}` to `state/spend-ledger.json`. The spend gate reads this; a per-source budget cap
  trips a `source_health` alert before overspend.

---

## 6. Session & fingerprint coherence (law #3, mechanized)

A **Session** is the unit of coherence and the unit of throttling. One session carries:

| Layer | Bound value | Tier-0 owner | Tier-1/2 owner |
|---|---|---|---|
| TLS / JA3 / JA4 | `impersonate="chrome"` profile incl. X25519MLKEM768 | curl_cffi | camoufox/BotBrowser native FP |
| HTTP/2 SETTINGS + header order | Chrome-shaped | curl_cffi | browser native |
| User-Agent + `Sec-CH-UA*` | matches the TLS Chrome major | browserforge | browser native |
| `Accept` / `Accept-Language` (`es-ES`) / `Accept-Encoding` | Spanish locale | browserforge | browser locale |
| Cookie jar | warmed clearance cookies | shared store | shared store |
| Exit IP | sticky per session | datacenter→none | Decodo sticky residential (ES) |

- **`browserforge`** generates the UA + client-hint headers *consistent with* the
  impersonated TLS major, so header-vs-TLS never contradict. `[VERIFIED, SOURCES_ES.md §4]`
- **Coherence invariant (asserted at session open, fail-closed):** TLS Chrome major ==
  UA Chrome major == `Sec-CH-UA` major. A mismatch raises before any request — a
  self-inflicted fingerprint contradiction is a bug, not a runtime condition.
- **Sticky IP per session:** at Tier-2 the residential exit is leased *sticky* for the
  session lifetime; rotating IP mid-drain is itself a bot signal (law #3).
- **Throttle is per-session and per-host:** token-bucket pacing with jitter, concurrency
  capped per host. The existing scale runs already proved over-concurrency triggers
  source throttling ("138 dealers cayeron por throttling de AS24 bajo carga 4×"
  `[VERIFIED, PROGRESO.md]`) → concurrency is a tuned per-source knob, not a global max.

---

## 7. Pagination defeat: facet-partition + stable sort (law #4, mechanized)

Aggregators cap result depth. The engine never tries to "page deeper"; it **shrinks every
partition below the cap** and unions.

**Algorithm (per dealer / per geo slice):**

1. Query the **declared count** for the slice (the source's own total — AS24
   `numberOfResults`, wallapop/advgo `total`). `[VERIFIED, autoscout24.py:286]`
2. If `declared ≤ PAGE_CAP` → drain directly with a **stable total sort** (deterministic
   tiebreak; `sort=price&desc=1` today, prefer an immutable id sort where available).
3. If `declared > PAGE_CAP` → **recursively bisect** the dominant facet until each leaf
   `≤ PAGE_CAP`. Facet order by selectivity: `price band → registration-year band →
   make → fuel → postcode prefix`. Each leaf is drained with its own stable sort.
4. **Union all leaves, dedup by stable id** (deep-link / listing id), not by row position.
   The dedup is what makes partition overlap harmless.
5. **Reconcile:** `Σ leaf-distinct == declared` (within live-counter drift tolerance) is
   the pagination VAM gate; otherwise the slice is `UNVERIFIED` and re-partitioned. This
   directly feeds the existing count-quorum verifier (`pipeline/verify.py`). `[VERIFIED]`

This replaces the fragile `while page <= max_pages` loop in `autoscout24.py:283-308` —
which silently stops at `max_pages` and cannot drain a dealer larger than the cap.

---

## 8. JA3/JA4 rotation & the post-quantum watch (law #5, mechanized)

- **Single source of truth:** one `IMPERSONATE_TARGET = "chrome"` constant (alias to
  latest supported Chrome) used everywhere; the explicit pin (`chrome131`+) is only for
  reproducibility snapshots. Upgrading the floor is a one-line change, repo-wide.
- **~6-week cadence:** Chrome's release train rots JA3/JA4. A scheduled job (re)confirms
  the current Chrome major and that `curl_cffi` supports it; if curl_cffi lags a Chrome
  release, that lag itself is a tracked risk (the fingerprint becomes *stale-but-real*,
  still better than Python-shaped, but flagged).
- **X25519MLKEM768 is no longer a boolean — it is a byte-exact shape + cross-session stability
  problem `[adversarial GAP-17, web-verified 2026]`.** Akamai made PQ the **default** for all
  client-to-Akamai connections (Jan-31-2026, full rollout Mar-2026), and **~57% of real browser
  ClientHellos now carry it** (adding 1,088 bytes). The discriminator has moved on:
  - **(a) The self-test is upgraded from presence to BYTE-EXACT diff.** "Is the key share present"
    is insufficient. The engine-start self-test now diffs the **actual emitted ClientHello byte-for-
    byte against a reference current-Chrome JA4** — the **key-share GROUP ORDER and the 1,088-byte
    ClientHello shape**, not merely the presence of a PQ group. Drift in order/shape/length → block
    start + alert.
  - **(b) Cross-session fingerprint STABILITY for walled sources.** Akamai Bot Manager v4+ scores
    fingerprint **consistency ACROSS sessions**, not just within one. CARDEEP law #3 enforces
    *within-session* coherence but said nothing about cross-session stability — and rotating a fresh
    browserforge identity per session (the prior design) is **itself a v4+ flag** ("accounts that
    switch profiles mid-flow"). Fix: a **stable per-target identity that persists across sessions**
    for behaviorally-scored/walled sources — the same target sees the same fingerprint over time
    (the human pattern), while OPEN sources may still rotate. The identity is keyed by target and
    pinned in `state/` so it survives restarts.
- **Adaptive demotion of the target:** if `source_health` shows a fingerprint-correlated
  rise in challenge rate for a source, the router bumps that source's floor tier and
  files an alert — the fingerprint aged out *for that defense* and we stop bleeding
  requests against it.

---

## 9. The recipe system (versioned per source, self-healing)

A **recipe** is the durable asset that lets Cardeep re-scrape a source *without the raw
crude* and survive the source's drift. It supersedes the thin `recipe.py` AS24 dict
(`pipeline/recipe.py`) with a full versioned spec. Stored as YAML under
`countries/ES/recipes/<key>.yaml` (long-tail) and `countries/ES/_tier1/<key>.yaml`
(Tier-1, **physically separated** — `ARCHITECTURE.md §Separación Tier-1` `[VERIFIED]`),
committed to git `main` (the mandate's "recetas guardadas").

### 9.1 Recipe schema

```yaml
version: 3                      # monotonic; bump on any selector/endpoint/tier change
source_key: autoscout24
tier1: false                    # hard separation flag → which tree it lives in
defense: none                   # is-antibot classification (cached, re-checked on cadence)
tier: 0                         # min sufficient fetch tier (router floor)
impersonate: chrome             # TLS target (alias to current Chrome)

access:                         # HOW to reach the data layer (law #1)
  surface: next_data            # next_data | json_api | graphql | jsonld | sitemap | html
  endpoint: "https://www.autoscout24.es/profesionales/{slug}"
  method: GET
  declared_count_path: "$..numberOfResults"   # for VAM + pagination (law #4)
  pagination:
    strategy: facet_partition   # facet_partition | sitemap_walk | cursor | none
    page_cap: 400               # observed depth cap
    stable_sort: "sort=price&desc=1"
    facets: [price_band, year_band, make, fuel, postcode_prefix]

field_map:                      # data-layer path → canonical field (typed)
  deep_link: "$.url"            # prefixed with host
  vin_ref:   "$.id"
  make:      "$.vehicle.make"
  model:     "$.vehicle.model"
  year:      "$.vehicle.firstRegistrationDate.raw[:4]"
  km:        "$.vehicle.mileageInKm.raw"     # unwrap {raw,formatted} (autoscout24.py bug §below)
  price:     "$.prices.public.priceRaw"
  fuel:      "$.vehicle.fuelCategory.raw"
  transmission: "$.vehicle.transmissionType.raw"
  photo_url: "$.images[0].href"
  dealer:    "$..dealerInfoPage"             # identity lives here, NOT in per-listing seller

validation:                     # the recipe's own acceptance gate (law: 0 critical nulls)
  required: [deep_link, price]
  bounds: { km: [1, 5000000], year: [1900, 2100] }

heal:                           # self-healing config (§9.3)
  adaptive_selectors: true      # Scrapling similarity relocation (HTML fallback only)
  reference_sample: "fixtures/autoscout24/golden.json"
  drift_alert_threshold: 0.15   # >15% field-null rate vs golden → alert + re-derive

provenance:
  derived_by: recipe-hunt-fleet # agent fleet (Tier-1) or deterministic inference (long-tail)
  verified_live: 2026-06-12
  notes: "open SSR; dealer identity in pageProps.dealerInfoPage"
```

### 9.2 Recipe lifecycle

```
DISCOVER source → HUNT recipe (find data layer, §1 law 1) → MATERIALIZE yaml (version N)
   → VERIFY on blind sample (validation gate) → COMMIT to git main
   → RUN (extractor reads recipe) → MONITOR (heal §9.3) → on drift: re-hunt → version N+1
```

- **Long-tail recipes** are derived *deterministically* (regex / JSON-LD / sitemap
  inference + local-LLM field mapping) — cheap, per the cost doctrine. `[VERIFIED, ORQUESTACION.md]`
- **Tier-1 recipes** are *hunted by the agent fleet* (`WF-TIER1-HUNT`) — expensive
  intelligence, one agent per giant, output = reproducible recipe *or* the exact wall.
  `[VERIFIED, ORQUESTACION.md]`
- Recipes are **CMS/DMS-family-keyed** for the long-tail: dealers on the same CMS
  (Motorflash microsites, a common DMS) share one recipe template parameterized per
  dealer — the census's "clasificar webs por CMS/DMS → receta por familia." `[VERIFIED,
  SOURCES_ES.md §9]` One recipe drains thousands of dealer sites.

### 9.3 Self-healing (Scrapling adaptive selectors)

- **Data-layer surfaces self-heal by structure:** JSON-path field maps are resilient to
  layout change; they break only on *schema* change, caught by the `validation` gate
  (null-rate spike vs the golden sample) → alert + re-hunt, not a silent wrong number.
- **HTML-fallback surfaces self-heal by similarity:** Scrapling's adaptive selectors
  relocate an element by similarity when its original path fails after a layout shift
  `[VERIFIED, websearch + SOURCES_ES.md §4]`. Enabled only for `surface: html` recipes.
- **Drift detector:** every run compares field-null rates and record-count against the
  recipe's golden sample; exceeding `drift_alert_threshold` files a `source_health` +
  `alert` row with the **exact origin** (`source_key`, `field`, observed-vs-expected) —
  the mandate's "alerta con el origen exacto," wired to the existing `alert`/`source_health`
  tables. `[VERIFIED, ARCHITECTURE.md migrations/0004]`

### 9.4 Self-tuning tier

When the router escalates a source at runtime (Tier-0 challenged → Tier-1 cleared), it
writes the *observed* working tier + defense back into the recipe (version bump) so the
next run starts at the right floor. The engine learns each source's true defense from
evidence and stops paying the escalation cost twice.

---

## 10. Concrete fixes this design forces on existing code

Grounded, not abstract — the redesign is also a bug-fix list against `pipeline/sources/autoscout24.py`:

1. **Replace `urllib` with `curl_cffi`** at every fetch (`fetch_page`, `collect_dealer_slugs`)
   → current-Chrome TLS + X25519MLKEM768. `[VERIFIED bug: urllib at :14-15, :69, :255]`
2. **Replace `while page <= max_pages`** with facet-partition + stable-sort drain (§7) →
   drains dealers larger than the page cap, which the current loop *cannot*. `[VERIFIED,
   :283-308]`
3. **Externalize the field map into the recipe** (§9.1) instead of hardcoded `parse_*`
   functions → versioned, self-healing, family-shareable. (The `{raw,formatted}` unwrap
   bug that doubled km digits — `autoscout24.py:144-148`, already patched — becomes a
   typed `field_map` path with a `bounds` gate, so the class of bug is structurally
   prevented.) `[VERIFIED, PROGRESO.md F3 causa raíz #2]`
4. **Route by `is-antibot`, not by a hardcoded `_UA`** (`:19`) → per-source tier from
   evidence (§3).
5. **Per-session coherence object** replaces the bare UA header dict (`:69`) → TLS+UA+
   headers+IP move as one identity (§6).

These ship as the new `pipeline/fetch/` engine (`session.py`, `router.py`, `tiers/`,
`solvers.py`) with `sources/*.py` reduced to thin recipe-bound adapters. Implementation is
out of scope for this doc (architecture only); the contracts above are the spec.

---

## 11. Dependencies (to pin when each front comes online)

Extends the commented block in `requirements.txt` `[VERIFIED]`. Versions are the current
verified line (2026-06); `impersonate="chrome"` keeps the TLS target self-updating.

```
# Tier-0 — workhorse
curl_cffi>=0.15.1            # TLS/JA3/JA4 + HTTP/2/3 browser impersonation  [VERIFIED]
browserforge                 # consistent UA + Sec-CH-UA client hints         [VERIFIED]
# Tier-1 — stealth browser / render
scrapling>=0.4.9             # StealthyFetcher (camoufox) + DynamicFetcher + adaptive selectors [VERIFIED]
camoufox[geoip]              # patched-Firefox stealth engine                 [VERIFIED]
# (optional Chromium-stealth alternates) patchright / nodriver / zendriver    [VERIFIED]
# Routing
is-antibot                   # defense classification per source              [VERIFIED]
# Tier-2 — spend-gated (install only when authorized)
hyper-sdk                    # Akamai/Incapsula/Kasada/DataDome sensor+cookie  [VERIFIED]
# 2captcha-python / capsolver — interactive challenge solvers                 [VERIFIED]
# Decodo (Smartproxy) residential — via proxy URL, no SDK pin required        [VERIFIED]
# BotBrowser — patched-Chromium render of last resort (binary, not pip)       [VERIFIED]
```

---

## 12. Sources (web-verified 2026-06-12)

- curl_cffi targets / JA4 / "chrome" alias / HTTP/3 — github.com/lexiforest/curl_cffi ·
  curl-cffi.readthedocs.io/en/latest/impersonate/targets.html · …/ja4.html
- X25519MLKEM768 as the new TLS bot signal; "post-quantum key share most scrapers don't
  send"; JA4 carries PQ key-share — scrapfly.io/blog/posts/post-quantum-tls-bot-detection ·
  scrapfly.io/web-scraping-tools/ja3-fingerprint/supported-group/x25519mlkem768
- Scrapling StealthyFetcher (camoufox, Turnstile/Interstitial auto-bypass), DynamicFetcher,
  adaptive selectors, v0.4.x — scrapling.readthedocs.io/en/latest/fetching/stealthy.html ·
  github.com/D4Vinci/Scrapling
- DataDome ML scoring (TLS+FP+31 motion signals+IP), solver/proxy approach —
  scrapfly.io/blog/posts/how-to-bypass-datadome-anti-scraping · zenrows.com/blog/datadome-bypass
- Akamai `_abck`/`sensor_data`, Hyper Solutions sensor API, "v3 deobfuscator is a trap" —
  github.com/Hyper-Solutions/hyper-sdk-py · hypersolutions.co · dev.to/xkiian (2026-05)
- Decodo (Smartproxy) residential pricing/scale + Site Unblocker — decodo.com/proxies/residential-proxies/pricing
- Internal `[VERIFIED]` facts (source endpoints, defenses, counts) — `docs/research/SOURCES_ES.md`,
  `docs/research/SOURCES_ES_raw.json`, `pipeline/sources/autoscout24.py`, `PROGRESO.md`.
```
