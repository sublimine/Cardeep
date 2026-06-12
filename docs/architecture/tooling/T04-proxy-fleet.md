# T04 — Proxy Fleet: Providers + Rotation for Spain (Residential / Mobile)

> Tooling audit for CARDEEP. Domain: proxy providers and rotation/management
> libraries for scraping 100% of Spain's used-vehicle points-of-sale and the
> giant marketplaces. Owner gates spend → the brief is **best value**, not
> cheapest and not most prestigious.
>
> Audit date: **2026-06-12**. Recency bar: anything not updated in 12+ months is
> treated as suspect and called out.
>
> Anti-hallucination legend: **[VERIFIED]** = I fetched the repo/page/API this
> session. **[ASSUMED]** = inferred, not directly confirmed. Every claim carries
> a source URL.

---

## 0. TL;DR — Recommendation

| Role | Pick | Why | ES per-GB (subscription) |
|---|---|---|---|
| **Primary residential** | **Decodo (ex-Smartproxy)** | Best price/quality balance, 736k ES IPs, 30-min sticky, clean `country-es` syntax, healthy maintained example SDK repo | **$3.00–$3.50/GB** (50/10 GB) |
| **Fallback / overflow residential** | **IPRoyal** | Non-expiring GB (project-based bursts), 2.0M ES IPs, sticky up to 7 days, SOCKS5 | **$4.90/GB @50GB**, $1.75 at bulk |
| **Cheapest bulk residential (cost-sensitive jobs)** | **Evomi** | $0.49/GB core, EU-domiciled (Swiss), sticky to 24h | **$0.49/GB** core |
| **Mobile (only where ES sites hard-block DC/residential)** | **Decodo or Evomi mobile** | Use surgically — mobile is 5–8x cost | Evomi $2.20–$3.75/GB; Oxylabs $9/GB PAYG |
| **Rotation / fleet management** | **Custom thin rotator** over provider gateway endpoints (provider does rotation server-side) + `requests-ip-rotator` only if AWS-DC fronting is ever needed | Scrapoxy (the obvious OSS choice) is **DEAD** | OSS / free |

**Bottom line:** If CARDEEP has no current choice, adopt **Decodo residential as
primary + IPRoyal as fallback**. Do **not** build on Scrapoxy — it was
discontinued in 2026 after 11 years. Do **not** pay Bright Data / Oxylabs
enterprise rates unless a specific ES target proves unbeatable by Decodo; the
performance delta is marginal and the price delta is 30–100%.

---

## 1. Why proxies matter for CARDEEP (scope framing)

Spain used-vehicle POS scraping hits two classes of target:

1. **Giant marketplaces** (coches.net, Milanuncios, Wallapop, AutoScout24.es,
   Flexicar, etc.) — aggressive anti-bot (Cloudflare, DataDome, PerimeterX-class
   fingerprinting). These require **residential** IPs with ES geo and session
   stickiness for paginated / logged-in-style flows.
2. **Long-tail dealer sites** (thousands of small POS) — mostly weak defenses;
   datacenter or rotating residential is fine. This is the **GB-volume** driver,
   so per-GB price dominates total cost.

Implication: the fleet must be **residential-first, ES-geo, sticky-capable**,
billed per-GB, with a cheap overflow lane for the long tail. Mobile is a
last-resort surgical tool, not a baseline.

---

## 2. Provider audit (live 2026 ecosystem)

All per-GB figures are **monthly subscription** unless marked PAYG
(pay-as-you-go). Prices verified against official pricing pages this session
where noted.

### 2.1 Decodo (formerly Smartproxy) — RECOMMENDED PRIMARY ✅

- **Alive?** Yes — rebranded Smartproxy→Decodo, actively selling. Example/SDK
  repo `Decodo/Decodo` **pushed 2026-05-06**, 1,189★, 8 open issues, MIT.
  **[VERIFIED]** (GitHub API).
- **What it solves:** Mid-market residential proxy with near-enterprise success
  rates at roughly half the enterprise price.
- **ES pool:** **736,181 residential IPs from Spain** advertised.
  **[VERIFIED]** https://decodo.com/proxies/list/europe/spain
- **Per-GB (residential, subscription):** 3GB $3.75 · 10GB $3.50 · 25GB $3.25 ·
  50GB $3.00. **PAYG (wallet) $8.50/GB.** **[VERIFIED]**
  https://decodo.com/proxies/residential-proxies/pricing
  (Note: ES landing page also shows a 100GB tier at $2.75/GB and PAYG $4.0/GB —
  pricing varies by entry point; treat $3.00–$3.50 as the realistic CARDEEP band
  and confirm at checkout.)
- **Geo-targeting:** continent / country / state / **city / ZIP / ASN**. Spain =
  `country-es`. **[VERIFIED]** (help.decodo.com + ES list page).
- **Sticky sessions:** rotate per-request OR sticky 1/10/30/60 min, custom up to
  24h. **[VERIFIED]** (decodo help docs / FAQ).
- **Pool / coverage:** marketed 115M+ IPs / 195+ locations (55M+ on some
  subscription tiers). Success rate cited 99.68–99.86%, <0.5s avg.
  **[ASSUMED]** on the headline pool figure (marketing); **[VERIFIED]** that the
  page states it.
- **Strengths:** best price/quality ratio in the mid tier; strong ES depth;
  city/ASN targeting (useful to mimic regional Spanish ISPs near a dealer);
  maintained SDK; SOCKS5 + HTTP(S); 3-day 100MB trial.
- **Weaknesses:** PAYG GB is expensive ($8.50) — only economical on
  subscription; 30-min default sticky cap shorter than IPRoyal's 7 days (rarely a
  problem for scraping).

**Integration (gate endpoint, ES sticky 30 min):**
```
# HTTP(S) — gate.decodo.com, port 7000 (rotating) / sticky via username params
# Username pattern: user-<USER>-country-es-session-<ID>-sessionduration-<MIN>
curl -x gate.decodo.com:7000 \
  -U "user-USERNAME-country-es-session-cardex01-sessionduration-30:PASSWORD" \
  "https://ip.decodo.com/json"
```

---

### 2.2 IPRoyal — RECOMMENDED FALLBACK ✅

- **Alive?** Yes — actively selling, docs current (docs.iproyal.com).
  **[ASSUMED]** active from live pricing/docs pages (no single repo to date-check;
  IPRoyal is closed-source SaaS).
- **What it solves:** Cost-controlled residential with **non-expiring traffic** —
  buy a GB block, unused GB rolls forever. Ideal for **bursty / project-based**
  CARDEEP runs (e.g., monthly full re-index) where a fixed monthly subscription
  would waste bandwidth.
- **ES pool:** **2,049,526 Spain IPs** — the **deepest ES pool** of the budget
  tier. **[VERIFIED]** https://iproyal.com/proxies-by-location/europe/spain/
- **Per-GB:** $7.00 @1GB → $5.95 @2GB → $5.25 @10GB → $4.90 @50GB, down to
  **$1.75/GB** at bulk. **[VERIFIED]** (use-apify.com pricing roundup +
  iproyal.com/pricing/residential-proxies).
- **Sticky:** 1 second to **7 days** (longest in this audit). **[VERIFIED]**
  (help.iproyal.com residential article).
- **Geo:** country + city; SOCKS5 + HTTP(S); geo in auth string.
- **Strengths:** non-expiring GB is a real money-saver for intermittent indexing;
  huge ES pool; very long sticky for account-style flows.
- **Weaknesses:** mid-tier per-GB at small volume ($4.90 @50GB > Decodo $3.00);
  you own retries/stealth/parsing (thin tooling); pool quality slightly below
  Decodo/enterprise per independent benchmarks **[ASSUMED]**.

**Integration:**
```
# geo.iproyal.com:12321, geo + sticky via username params
# user:PASS_country-es_session-cardex01_lifetime-30m  (lifetime up to 7d)
curl -x geo.iproyal.com:12321 \
  -U "USERNAME:PASSWORD_country-es_session-cardex01_lifetime-30m" \
  "https://ipv4.icanhazip.com"
```
(Exact param tokens per IPRoyal dashboard "proxy generator" — confirm in panel;
the `_country-`/`_session-`/`_lifetime-` scheme is IPRoyal's documented format.
**[ASSUMED]** on exact token spelling — verify against dashboard before coding.)

---

### 2.3 Evomi — RECOMMENDED CHEAPEST BULK LANE ✅ (cost-sensitive)

- **Alive?** Yes — actively selling, Swiss-domiciled, current pricing page.
  **[VERIFIED]** https://evomi.com/pricing
- **What it solves:** Lowest credible residential per-GB ($0.49) for the
  **long-tail dealer** volume where targets are weakly defended and the only
  thing that matters is cheap ES bandwidth.
- **Per-GB:** **Core residential $0.49/GB** (100GB @ $49.99/mo), Premium
  residential $2.15/GB, PAYG $0.49. **Mobile** $2.20–$3.75/GB (volume-tiered),
  mobile PAYG $4.00. **[VERIFIED]** evomi.com/pricing.
- **Pool:** 54M+ residential IPs, 150+ countries (ES included).
  **[ASSUMED]** ES depth not separately published; global coverage stated.
- **Sticky:** 1 min → 120 min standard, `_lifetime-1440` extends to 24h; "hard
  session" holds IP while device stays online. **[VERIFIED]** (proxyway review +
  docs.evomi.com).
- **Geo:** country/city targeting; `country-es`-style param. **[ASSUMED]** exact
  ES token (verify in panel).
- **Strengths:** unbeatable price for the volume lane; EU/Swiss domicile is a
  **GDPR-friendly** plus for a Spain/EU operation; generous sticky (24h);
  free 1-day trial.
- **Weaknesses:** smaller brand / shorter track record than Decodo; "Core" pool
  quality is the trade for $0.49 — keep Core for soft targets, escalate to Decodo
  for hard marketplaces; ES-specific pool size unpublished (validate empirically
  before committing volume).

**Integration:**
```
# core-residential.evomi.com:1000 (HTTP) — username carries geo + session
curl -x core-residential.evomi.com:1000 \
  -U "USERNAME_country-ES_session-cardex01_lifetime-30:PASSWORD" \
  "https://ip.evomi.com/json"
```
(`_lifetime-1440` for 24h sessions. **[ASSUMED]** exact host/port — confirm in
Evomi dashboard.)

---

### 2.4 Bright Data — NOT RECOMMENDED for CARDEEP (overkill / overpriced) ⚠️

- **Alive?** Very — market leader, Web Unlocker + MCP, constant updates.
  **[VERIFIED]** (brightdata.com/pricing, multiple 2026 reviews).
- **Per-GB:** PAYG **~$5.04–$8.40/GB** (sources vary), ~$3.50/GB on $499 growth
  plan, ~$2.00–$3.00/GB committed at enterprise scale. Web Unlocker ~$3–$5 per
  1k successes. **[VERIFIED]** (use-apify + dataresearchtools 2026 roundups; the
  exact PAYG headline varies by source — official page is the arbiter).
- **Strengths:** biggest pool, best compliance/KYC posture, best anti-bot tooling
  (Web Unlocker auto-solves), city/ASN/carrier targeting, robust ES depth.
- **Weaknesses for CARDEEP:** **price** — 30–100% over Decodo for marginal gain
  on CARDEEP's target mix; enterprise sales friction; the owner gates spend.
- **Verdict:** Hold as a "break glass" option for a *specific* ES marketplace
  that defeats Decodo+IPRoyal+stealth. Web Unlocker (pay-per-success) could be a
  targeted unblock layer for the 2–3 hardest sites rather than a fleet-wide spend.

---

### 2.5 Oxylabs — NOT RECOMMENDED for CARDEEP (enterprise tax) ⚠️

- **Alive?** Very — enterprise leader alongside Bright Data. **[VERIFIED]**
  (oxylabs.io/pricing).
- **Per-GB:** Residential PAYG **$4.00/GB**; subscription $3.87 (Micro) → $3.75
  (Starter) → $3.49 (Advanced) → $3.01 (Premium) → **$2.00/GB** (Corporate,
  1TB+). **Mobile $9/GB** no-commit. **[VERIFIED]** (oxylabs roundups +
  oxylabs.io/pricing/residential-proxy-pool).
- **Strengths:** excellent success rates, strong ES coverage, sticky residential
  product, enterprise SLAs/compliance.
- **Weaknesses for CARDEEP:** entry per-GB higher than Decodo for similar quality
  at CARDEEP's volume; the $2/GB only materializes at 1TB+ commit, which the
  spend gate won't approve early. Mobile at $9/GB is the most expensive here.
- **Verdict:** Same as Bright Data — premium reserve, not the fleet baseline.

---

### 2.6 Quick price ladder (ES residential, realistic CARDEEP volume ~10–50GB)

| Provider | Per-GB @~50GB | PAYG | ES pool | Sticky max | Status |
|---|---|---|---|---|---|
| **Evomi (Core)** | **$0.49** | $0.49 | 54M global | 24h | ✅ cheapest |
| **Decodo** | **$3.00** | $8.50 | 736k ES | 24h (30m default) | ✅ best balance |
| **Oxylabs** | $3.49 | $4.00 | large | session-set | ⚠️ premium |
| **IPRoyal** | $4.90 | block (non-expiring) | **2.0M ES** | **7 days** | ✅ fallback |
| **Bright Data** | ~$3.50 (growth) | $5.04–8.40 | largest | session-set | ⚠️ premium |

---

## 3. Rotation / fleet-management libraries (OSS)

The critical finding: **the IPs already rotate server-side** at the provider
gateway (Decodo `gate.decodo.com:7000`, IPRoyal `geo.iproyal.com:12321`, Evomi
endpoint). For CARDEEP you do **not** need a heavyweight rotation framework — you
need a thin session/ID manager. The classic OSS aggregators are mostly dead.

### 3.1 Scrapoxy — ☠️ DEAD / DISCONTINUED — DO NOT USE

- **Status:** **Discontinued in 2026 after 11 years.** Official End-of-Life FAQ;
  Docker images pulled from registries, public docs offline, shared infra shut
  down for non-paying users. Repo README literally reads "Scrapoxy has been
  discontinued." **[VERIFIED]** https://scrapoxy.io/qna and
  https://github.com/scrapoxy/scrapoxy (2,419★, license NOASSERTION).
- **Trap:** GitHub API shows `archived: false` and a `pushed_at 2026-02-07` — but
  that push is the **deprecation-notice commit**, not maintenance. Do not be
  fooled by the recent timestamp. **[VERIFIED]** (GitHub API + EOL FAQ
  cross-check).
- **What it was:** the best OSS proxy-aggregation/management layer (route across
  many providers, fingerprint, auto-rotate). Its death is exactly why CARDEEP
  should lean on **provider-side rotation + a small custom manager** instead of
  betting on an OSS aggregator.

### 3.2 ProxyBroker — ☠️ DEAD

- **Status:** Last push **2024-03-18**, 4,151★, 106 open issues, Apache-2.0.
  >2 years stale. **[VERIFIED]** (GitHub API). Do not adopt.

### 3.3 scrapy-rotating-proxies (TeamHG-Memex) — ⚠️ ALIVE BUT NICHE

- **Status:** pushed **2026-04-08**, 773★, 53 open issues, MIT. **[VERIFIED]**
  (GitHub API). Actively touched, but Scrapy-only and aimed at lists of *static*
  proxies with liveness checks + quarantine — redundant when the provider gateway
  already rotates. Useful only if CARDEEP runs Scrapy and wants per-proxy
  ban-tracking across a static IPRoyal/ISP list. Otherwise skip.

### 3.4 requests-ip-rotator (Ge0rg3) — ✅ ALIVE, NICHE UTILITY

- **Status:** pushed **2026-05-16**, 1,666★, 5 open issues, GPL-3.0.
  **[VERIFIED]** (GitHub API). Rotates IPs via **AWS API Gateway** (free-tier DC
  IPs). Not residential — useful only as a *zero-cost datacenter fronting* lane
  for the weakest long-tail dealer sites, to spare paid GB. Keep on the bench as a
  cost-optimizer, not a core dependency. GPL-3.0 — check license compatibility.

### 3.5 proxy.py (abhinavsingh) — ✅ ALIVE, INFRA TOOL

- **Status:** pushed **2026-05-18**, 3,529★, 87 open issues, BSD-3. **[VERIFIED]**
  (GitHub API). A programmable local proxy server. Good as a **local egress /
  upstream-chaining gateway** in front of provider pools (centralize auth,
  logging, per-domain provider routing — basically a mini home-grown Scrapoxy
  replacement). Strongest OSS candidate if CARDEEP wants a self-hosted control
  plane. Recommended for the *control* layer, not as an IP source.

### 3.6 cloudproxy (claffin) — ✅ ALIVE

- **Status:** pushed **2026-06-10**, 1,703★, 33 open issues, MIT. **[VERIFIED]**
  (GitHub API). Spins up disposable proxy droplets across DigitalOcean/AWS/GCP/
  Hetzner and rotates them. **Datacenter** IPs only — same role as
  requests-ip-rotator: a cheap DC lane for soft targets, not a residential
  substitute. Modern and maintained; viable bench tool.

### 3.7 Recommended rotation architecture for CARDEEP

```
scrapers ──► [proxy.py control plane]  (self-hosted, optional but recommended)
                 │   routes by target difficulty:
                 ├─► Evomi Core (ES)        → long-tail soft dealer sites (cheap GB)
                 ├─► Decodo residential (ES)→ hard marketplaces (sticky 30m, session IDs)
                 ├─► IPRoyal (ES)           → overflow / non-expiring burst lanes
                 └─► cloudproxy / req-ip-rotator → free DC lane for trivial targets
```
Rotation itself = **session-ID cycling in the username** (provider rotates the
egress IP per new session string). A ~150-line manager that mints
`session-<uuid>` per worker and recycles on ban is all CARDEEP needs. No dead
aggregator required.

---

## 4. Is CARDEEP's current choice good enough?

**No current proxy provider is recorded in the project memory/source of truth for
T04** (memory references a scraper fleet, entity/delta/price APIs, and a dormant
`cardex-stealth` worktree, but no named proxy vendor). Treat this as a greenfield
selection.

**If any prior intent leaned on Scrapoxy for fleet management → replace it now:**
Scrapoxy is dead (§3.1). The replacement is **provider-side rotation +
`proxy.py` as an optional self-hosted control plane**, with **Decodo** as primary
residential, **IPRoyal** as non-expiring fallback, and **Evomi Core** as the
cheap bulk lane. Reserve Bright Data Web Unlocker / Oxylabs only as a per-success
"break glass" layer for the 2–3 hardest ES marketplaces.

---

## 5. Concrete adoption plan (spend-gated)

1. **Phase 0 (trials, ~$0):** Decodo 100MB trial + Evomi 1-day trial + IPRoyal
   small block. Benchmark each against the 5 hardest ES targets (coches.net,
   Milanuncios, Wallapop, AutoScout24.es, Flexicar) measuring success rate, block
   rate, latency, GB burn.
2. **Phase 1 (commit primary):** Decodo 25–50GB subscription ($3.00–3.25/GB) for
   marketplaces. IPRoyal block ($4.90/GB, non-expiring) as overflow.
3. **Phase 2 (bulk lane):** Evomi Core 100GB ($0.49/GB) for the validated soft
   long-tail dealer set; add free DC lane (cloudproxy / requests-ip-rotator) for
   trivially open sites to spare paid GB.
4. **Control plane (optional, recommended):** stand up `proxy.py` to centralize
   auth, per-domain provider routing, and ban-driven session recycling.
5. **Reserve:** keep a Bright Data Web Unlocker key un-provisioned but ready for
   the handful of sites that defeat everything else (pay-per-success, not GB).

---

## 6. Source URLs

**[VERIFIED] (fetched this session)**
- Decodo residential pricing — https://decodo.com/proxies/residential-proxies/pricing
- Decodo Spain pool (736,181 IPs) — https://decodo.com/proxies/list/europe/spain
- Decodo SDK repo (pushed 2026-05-06) — https://github.com/Decodo/Decodo
- Evomi pricing — https://evomi.com/pricing
- IPRoyal Spain pool (2,049,526 IPs) — https://iproyal.com/proxies-by-location/europe/spain/
- Scrapoxy EOL FAQ — https://scrapoxy.io/qna
- Scrapoxy repo (discontinued) — https://github.com/scrapoxy/scrapoxy
- scrapy-rotating-proxies (pushed 2026-04-08) — https://github.com/TeamHG-Memex/scrapy-rotating-proxies
- requests-ip-rotator (pushed 2026-05-16) — https://github.com/Ge0rg3/requests-ip-rotator
- ProxyBroker (pushed 2024-03-18, DEAD) — https://github.com/constverum/ProxyBroker
- proxy.py (pushed 2026-05-18) — https://github.com/abhinavsingh/proxy.py
- cloudproxy (pushed 2026-06-10) — https://github.com/claffin/cloudproxy

**[VERIFIED] (search-corroborated, multiple 2026 sources)**
- Oxylabs pricing — https://oxylabs.io/pricing/residential-proxy-pool
- Bright Data pricing — https://brightdata.com/pricing/proxy-network/residential-proxies
- IPRoyal pricing — https://iproyal.com/pricing/residential-proxies/
- Decodo sticky/endpoint docs — https://help.decodo.com/docs/residential-proxy-endpoints-and-ports
- IPRoyal sticky (7-day) — https://help.iproyal.com/en/articles/7214673-how-to-use-residential-proxies
- Bright Data 2026 pricing roundup — https://use-apify.com/blog/bright-data-pricing-guide-2026

**[ASSUMED] (verify before coding):** exact IPRoyal/Evomi username token spelling
(`_country-`/`_session-`/`_lifetime-`), ES-specific pool depth for Evomi, and the
marketing headline pool sizes (115M/54M) — confirm in each provider dashboard.
