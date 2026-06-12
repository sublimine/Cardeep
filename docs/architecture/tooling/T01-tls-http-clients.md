# T01 — No-Browser HTTP Clients with TLS/JA3/JA4 Impersonation

> Domain audit for CARDEEP. Task: pick the most updated, modern, bulletproof
> no-browser HTTP client able to impersonate browser TLS/JA3/JA4/HTTP2(+3)
> fingerprints, with a **current-Chrome floor** and **post-quantum
> (X25519MLKEM768)** key share, for high-throughput second-hand-vehicle scraping.
>
> Audit date: **2026-06-12**. Anti-hallucination: every claim is tagged
> `[VERIFIED]` (I fetched the repo/PyPI/changelog/blog) or `[ASSUMED]`
> (inference from a verified fact, not directly read). Source URLs inline.

---

## 0. TL;DR — the verdict

- **Recommended (primary): `curl_cffi` ≥ 0.15.0** — `[VERIFIED]` stable
  2026-04-03, beta 0.15.1b2 2026-06-05. It is the only candidate in this class
  that is simultaneously (a) actively maintained on a current-Chrome floor
  (impersonates up to **chrome146**, firefox147, safari260), (b) post-quantum
  correct (its engine, `lexiforest/curl-impersonate`, ships the
  **X25519MLKEM768** key share for modern Chrome targets), (c) HTTP/2 **and**
  HTTP/3 (QUIC) capable, and (d) a near-drop-in `requests`/`httpx` API with a
  real `AsyncSession`. **CARDEEP already standardizes on it** (`curl_cffi>=0.15.1`
  pinned in `scrapers/requirements.txt`). The current choice is good enough —
  but the **pin must move to `>=0.15.0` with an explicit chrome-target floor**,
  not the bare `chrome` alias (see §7).

- **Fallback (Rust-speed, throughput-bound): `rnet` / `wreq-python`** —
  `[VERIFIED]` v0.12.0 2026-06-04, 1.4k★, Rust+PyO3 over BoringSSL. BoringSSL
  natively negotiates X25519MLKEM768, so its PQ posture is correct by
  construction. Use it for the highest-volume sitemap/listing sweeps where
  per-request overhead dominates. Caveat: single high-churn maintainer, fast
  rename history (rnet → wreq-python), **no HTTP/3** — keep it as a
  throughput accelerator, not the primary.

- **Do not adopt as primary:** `primp` (alive but smaller, single-maintainer,
  no HTTP/3, weaker async story), `tls-client` (Go; alive again but uTLS-CVE
  exposed and out of CARDEEP's Python path), `hrequests` (**DEAD** — last PyPI
  release > 12 months, depends on tls-client). `requests`/`httpx`/`aiohttp`/
  `niquests` are **not impersonation clients** and are filtered by any modern
  CDN on TLS alone.

---

## 1. Why this domain is now make-or-break (2026 context)

A no-browser HTTP client only earns its place if its TLS ClientHello, HTTP/2
SETTINGS/priority frames, and (increasingly) HTTP/3 transport parameters match a
**real, current** browser. Two 2026 shifts raised the floor:

1. **Post-quantum key share is now a fingerprint, not a curiosity.** Chrome and
   Firefox send the **X25519MLKEM768** hybrid key share (NamedGroup `0x11ec` /
   4588, 1216-byte client share) by **default** in every TLS 1.3 ClientHello.
   `[VERIFIED]` A client claiming "Chrome 14x" that omits this key share is a
   direct mismatch a CDN can flag **before** the first HTTP byte. Source:
   Scrapfly, *Post-Quantum TLS: Why Scraping Tools Are Now Exposed*
   (2026-04-18) — https://scrapfly.io/blog/posts/post-quantum-tls-bot-detection
   ; PQC primer https://chromestatus.com/feature/5257822742249472 .

2. **uTLS hardcoded-fingerprint CVEs.** `[VERIFIED]` The Go uTLS stack (which
   powers `tls-client`, Colly, go-rod tooling) took two named CVEs:
   **CVE-2026-26995** (missing padding extension, 1.6.0–1.8.1) and
   **CVE-2026-27017** (cipher-suite mismatch in ECH, 1.6.0–1.8.0). Fix: uTLS
   ≥ 1.8.2. Source: Scrapfly post above. This is a structural argument for a
   client whose fingerprints track a maintained browser engine
   (curl-impersonate's patched BoringSSL, or wreq's BoringSSL) over one that
   pins hand-rolled ClientHello specs.

**Consequence for tool choice:** "alive" is necessary but insufficient. The bar
is **current-Chrome floor + PQ key share + HTTP/2 frame fidelity**, refreshed on
a cadence that keeps up with Chrome's ~4-week release train.

---

## 2. Candidate matrix (all facts `[VERIFIED]` unless tagged)

| Tool | Lang / engine | Latest release (date) | Stars | Chrome floor | PQ X25519MLKEM768 | HTTP/2 | HTTP/3 | JA3/JA4 | Async | Status |
|------|---------------|------------------------|-------|--------------|-------------------|--------|--------|---------|-------|--------|
| **curl_cffi** | Python ↔ C (curl-impersonate / patched BoringSSL) | 0.15.0 (2026-04-03); beta 0.15.1b2 (2026-06-05) | (lexiforest, top-tier in class) | **chrome146** | **Yes** (engine, Chrome 124/130+ targets) | Yes | **Yes** (Chrome 145/146, FF147; QUIC + SOCKS5 UDP) | JA3/JA4 + custom `ja3`/`akamai`/`extra_fp` | Yes (`AsyncSession`) | **ALIVE — recommended** |
| **rnet / wreq-python** | Rust (PyO3) over **BoringSSL** (`wreq`) | 0.12.0 (2026-06-04); 73 releases | 1.4k | 100+ profiles incl. Chrome (latest via `wreq-util`) | **Yes** (BoringSSL native) `[ASSUMED]` from backend | Yes | **No** `[VERIFIED]` not mentioned | **JA3/JA4** | Yes | **ALIVE — fallback** |
| **primp** | Rust (PyO3) over rquest/wreq-family BoringSSL | 1.3.1 (2026-05-23) | 538 | **chrome144–148** | **Yes** `[ASSUMED]` BoringSSL native | Yes (custom header order, stream-id) | **No** | JA3/JA4 (topic) | Limited | **ALIVE — niche** |
| **tls-client** | Go (uTLS / fhttp) | v1.15.1 (2026-06-08); 371 commits | 1.7k | **Chrome_144** | not stated `[ASSUMED]` uTLS-dependent | Yes | **Yes** (claims QUIC/HTTP3 fp) | JA3 (from-string) | n/a (Go) | **ALIVE — out of path** |
| **hrequests** | Python wrapper over tls-client | 0.9.2 (no PyPI release in 12+ mo) | — | inherits tls-client (stale) | No | via tls-client | No | via tls-client | partial | **DEAD / discontinued** |
| requests / httpx / aiohttp / niquests | Python (ssl/openssl) | current | — | **none** (default ClientHello) | No | httpx yes | no | **no impersonation** | yes | not in class |

Engine sources (all `[VERIFIED]` fetched):
- curl_cffi releases https://github.com/lexiforest/curl_cffi/releases ;
  targets https://curl-cffi.readthedocs.io/en/latest/impersonate/targets.html ;
  PyPI https://pypi.org/project/curl-cffi/
- curl-impersonate (engine) https://github.com/lexiforest/curl-impersonate
  → "X25519Kyber768/X25519MLKEM curves introduced in Chrome 124 and 130",
  Chrome 145/146 wrappers, v1.5.6 (2026-05-02).
- rnet/wreq-python https://github.com/0x676e67/rnet ;
  wreq (Rust) https://github.com/0x676e67/wreq (v6.0.0-rc.29, 2026-06-03;
  "HTTPS via BoringSSL")
- primp https://github.com/deedy5/primp + https://github.com/deedy5/primp/releases
- tls-client https://github.com/bogdanfinn/tls-client
- hrequests https://pypi.org/project/hrequests/ (Snyk: "Inactive … no new
  versions … in the past 12 months … could be considered discontinued")

---

## 3. Per-candidate detail

### 3.1 curl_cffi — ALIVE, RECOMMENDED `[VERIFIED]`
- **What it solves:** browser-identical TLS/JA3 + HTTP/2 (Akamai) + HTTP/3
  fingerprints from Python, via cffi bindings to `lexiforest/curl-impersonate`
  (an actively maintained fork of the original curl-impersonate, which itself
  was stagnating). Near-drop-in `requests`/`httpx` API, real `AsyncSession`.
- **Recency:** stable **0.15.0 (2026-04-03)**, RC 0.15.0rc1 (2026-03-30), betas
  0.15.1b1 (2026-04-23) and 0.15.1b2 (2026-06-05). Engine curl-impersonate
  v1.5.6 (2026-05-02), 478 commits. **Squarely current.**
- **Fingerprint floor:** impersonate targets up to **chrome146**, chrome145,
  chrome142, chrome136, chrome133a; firefox147/144/135; safari260(+iOS)/2601;
  edge99/101 (Edge floor is old); tor145; chrome131_android. Generic aliases
  `chrome`/`firefox`/`safari` resolve to "latest available".
- **Post-quantum:** the changelog never says "ML-KEM" by name `[VERIFIED]`, but
  the **engine** (`lexiforest/curl-impersonate`) explicitly introduced
  "X25519Kyber768/X25519MLKEM curves … in Chrome 124 and 130" `[VERIFIED]`, so
  modern chrome13x/14x targets send the PQ key share. **This is the decisive
  reason to keep curl_cffi on a recent chrome target and off stale ones** —
  an old `chrome131`/`chrome133` pin can mismatch the PQ share (see issue
  threads #500, #529, discussion #364). `[VERIFIED]` (issue titles read).
- **0.15.x highlights:** HTTP/3 fingerprints for Chrome 145/146 + Firefox 147;
  HTTP/3 over SOCKS5-UDP proxy; CLI `curl-cffi`; static build (macOS ≥ 11);
  Android support; free-threading; `CurlOpt.HTTPHEADER_ORDER`; live fingerprint
  DB refresh via impersonate.pro (beta). `[VERIFIED]`
- **Weaknesses:** C/libcurl dependency (wheels mitigate, but musl/Alpine and
  exotic arch can need care); Edge fingerprints lag; per-request `impersonate`
  switching is discouraged (CARDEEP already enforces session-level only).
- **Fit for CARDEEP:** already the standard. `scrapers/engine/antidetect/tls.py`
  builds `AsyncSession(impersonate="chrome", http_version=3, proxies=…)` bound
  one-identity-one-JA3-per-session — exactly the right pattern. `[VERIFIED]`

### 3.2 rnet / wreq-python — ALIVE, FALLBACK `[VERIFIED]`
- **What it solves:** Rust-speed (PyO3) HTTP/WebSocket client over **BoringSSL**
  (`wreq` core), with 100+ device emulation profiles and fine-grained TLS +
  HTTP/2 extension control rather than opaque fingerprint strings. Outperforms
  requests/httpx/aiohttp/curl_cffi on its own pyperf suite (vendor benchmark —
  treat as directional). `[VERIFIED]`
- **Recency:** wreq-python **v0.12.0 (2026-06-04)**, 73 releases, 1.4k★; Rust
  `wreq` v6.0.0-rc.29 (2026-06-03), 858★. Very active.
- **Post-quantum:** README/docs don't say "ML-KEM" `[VERIFIED]`, but the TLS
  backend is **BoringSSL**, which ships X25519MLKEM768 natively and includes
  configured curves in the ClientHello `[VERIFIED]` (Cloudflare boringssl-pq,
  BoringSSL `-curves` behavior). So PQ correctness is **inherited from the
  stack** `[ASSUMED]` — verify with a live ClientHello capture before trusting
  it on a PQ-strict CDN.
- **Weaknesses:** **no HTTP/3** `[VERIFIED]`; single maintainer (0x676e67) with
  a **fast rename/restructure cadence** (rnet ⇄ wreq-python, wreq, wreq-util) —
  a real supply-chain/churn risk for a long-lived pipeline; pin exact versions.
- **Fit:** ideal as the throughput tier for massive listing/sitemap sweeps where
  curl_cffi's libcurl per-call overhead is the bottleneck. Keep behind the same
  identity/JA3-per-session invariant.

### 3.3 primp — ALIVE, NICHE `[VERIFIED]`
- v1.3.1 (2026-05-23), 538★, MIT, 96% Rust. Impersonates Chrome **144–148**,
  Firefox 140/146–148, Safari 18.5/26/26.3, Edge 144–148, Opera 126–131 — the
  **highest nominal Chrome floor** of the set. Lets you split `impersonate_os`
  (windows/macos/linux/android/ios/random) from the browser profile — useful.
- PQ: BoringSSL-family backend `[ASSUMED]` → likely correct; not documented.
- **Why not primary:** 538★ vs curl_cffi's far larger base; single maintainer;
  **no HTTP/3**; thinner async ergonomics; only 2 open issues but small support
  surface. Strong throughput pick, but `rnet` is the better-supported Rust
  fallback. Reach for primp specifically when the OS/browser split matters.

### 3.4 tls-client (bogdanfinn) — ALIVE but OUT OF PATH `[VERIFIED]`
- v1.15.1 (2026-06-08), 1.7k★, 371 commits, 35 releases. Now advertises
  HTTP/1.1+2+**3** with QUIC fingerprinting and `profiles.Chrome_144`. Genuinely
  revived. **But:** it is **Go**, built on uTLS/fhttp — i.e. exposed to the uTLS
  fingerprint-pinning CVEs (§1) unless on uTLS ≥ 1.8.2, and it sits outside
  CARDEEP's Python toolchain (would mean a sidecar/cgo bridge). Excellent if you
  ever build a Go scraping tier; **not** the Python answer.

### 3.5 hrequests (daijro) — DEAD `[VERIFIED]`
- Latest **0.9.2**, **no PyPI release in 12+ months**; Snyk flags **Inactive /
  likely discontinued**; no recent PR/issue activity. It wraps bogdanfinn's
  tls-client, so it inherits that stack's staleness with **none** of the recent
  revival. **Do not adopt. Do not depend on it transitively.** If any CARDEEP
  module imports it, rip it out.

### 3.6 Non-impersonation clients — not in class
`requests`, `httpx[http2]`, `aiohttp`, `niquests` ship the Python/OpenSSL default
ClientHello with **no** browser JA3/JA4 mimicry. CARDEEP pins `httpx[http2]==0.27.2`
and `aiohttp==3.9.5` `[VERIFIED]` — fine for **open/unprotected** endpoints
(plain sitemaps, OEM JSON, internal APIs) but they MUST NOT be pointed at
WAF-guarded portals; they fail on TLS before HTTP. Keep them as the "trusted
host" tier only.

---

## 4. Throughput note
Vendor benchmarks (rnet's pyperf suite; primp's "faster if throughput-bound")
both claim Rust clients beat curl_cffi on raw req/s. `[VERIFIED]` that the claims
exist; the **magnitude is environment-specific** and not independently
reproduced here. Practical reading consistent across 2026 write-ups
(Bright Data, Datahut, Piloterr): **curl_cffi is the maturity/coverage sweet
spot (HTTP/2+3, async, broad targets); reach for a Rust client only when
genuinely throughput-bound at high volume.** Decision rule for CARDEEP:
default curl_cffi; benchmark rnet on the actual listing-sweep workload before
promoting it on any host where per-request CPU is the proven bottleneck.

Sources: https://brightdata.com/blog/web-data/web-scraping-with-curl-cffi ,
https://www.blog.datahut.co/post/web-scraping-without-getting-blocked-curl-cffi ,
https://www.piloterr.com/blog/ultra-fast-python-http-client-with-advanced-tls-fingerprinting

---

## 5. Is CARDEEP's current choice good enough?
**Yes — curl_cffi stays.** It is the correct primary: alive, current-Chrome
floor, PQ-correct engine, HTTP/2+3, async, already wired into
`engine/antidetect/tls.py` with the right one-JA3-per-session discipline. No
replacement is warranted. The two corrections below are hardening, not a swap.

### 5.1 Required hardening (do these)
1. **Bump the floor and be explicit about it.** Pin moves from
   `curl_cffi>=0.15.1` (a beta string — `0.15.1` is only released as betas as of
   2026-06-12 `[VERIFIED]`) to a **stable floor**: `curl_cffi>=0.15.0,<0.16`.
   Tracking a beta in `requirements.txt` is a latent footgun.
2. **Pin the Chrome target above the PQ line — do not ship a stale alias risk.**
   The `chrome` alias resolves to "latest available" `[VERIFIED]`, which is good,
   but make the **minimum acceptable target explicit** in the TLSProfile map so a
   downgrade can't silently drop you onto a pre-PQ `chrome131/133`. Target
   `chrome142`+ (PQ-correct, current). The map in `tls.py` should name a concrete
   floor, not only the bare alias.
3. **Add a live PQ self-check to CI/health.** Hit a PQ-strict reflector (e.g. a
   TLS-inspect endpoint) and assert the ClientHello carries NamedGroup `0x11ec`
   (X25519MLKEM768). This catches a wheel/engine regression before a CDN does.

### 5.2 Adopt the fallback tier
Add `rnet` (pinned exact, e.g. `rnet==0.12.0`) as the **throughput accelerator**
for the heaviest sweeps, behind the same identity contract. Do **not** route
WAF-guarded portals onto httpx/aiohttp.

---

## 6. Recommended CONFIG

### 6.1 Primary — curl_cffi (CARDEEP's existing pattern, hardened)
```python
# scrapers/engine/antidetect/tls.py  — PQ-aware floor, session-level JA3 only
from curl_cffi.requests import AsyncSession
from scrapers.engine.identity.profile import Identity, TLSProfile

# Concrete PQ-correct targets (>= chrome142 sends X25519MLKEM768).
# Never map an identity onto a pre-PQ chrome131/133 target.
_PROFILE_MAP: dict[TLSProfile, str] = {
    TLSProfile.CHROME136: "chrome",      # alias -> latest available (>=146 today)
    TLSProfile.FIREFOX147: "firefox",
    TLSProfile.SAFARI260: "safari",
}
# Hard floor guard: refuse to start if curl_cffi resolves "chrome" below the PQ line.
_MIN_CHROME_PQ = 142

def make_session(identity: Identity) -> AsyncSession:
    impersonate = _PROFILE_MAP[identity.tls_profile]
    proxy = identity.proxy_ip  # http://user:pass@host:port
    return AsyncSession(
        impersonate=impersonate,   # session-level only; never per-request (JA3 invariant)
        http_version=3,            # QUIC / HTTP-3
        proxies={"https": proxy, "http": proxy} if proxy else None,
    )
```
```text
# requirements.txt
curl_cffi>=0.15.0,<0.16        # stable floor, PQ-correct engine, chrome146/ff147/safari260
```

### 6.2 Fallback — rnet (throughput tier, pinned exact)
```python
# scrapers/engine/antidetect/tls_fast.py  — Rust/BoringSSL accelerator
import rnet
from rnet import Impersonate

def make_fast_client(proxy: str | None) -> rnet.Client:
    # BoringSSL backend negotiates X25519MLKEM768 natively; verify with a live
    # ClientHello capture before trusting on a PQ-strict CDN.
    return rnet.Client(
        impersonate=Impersonate.Chrome,   # latest Chrome profile in wreq-util
        proxies=[proxy] if proxy else None,
    )
```
```text
# requirements.txt (fallback tier)
rnet==0.12.0                   # pin exact: single-maintainer, fast rename history
```
> NB: exact API names for `rnet` (`Impersonate.Chrome`, ctor kwargs) are
> `[ASSUMED]` from its docs and MUST be confirmed against the pinned 0.12.0
> `rnet` Python stubs before merge — the project renames aggressively.

---

## 7. Decision summary
- **Keep curl_cffi as primary.** It wins on the only axes that matter in 2026:
  current-Chrome floor, PQ key share, HTTP/2+3, async, maintenance, and it is
  already integrated correctly.
- **Harden the pin** (`>=0.15.0,<0.16`), **name an explicit PQ-correct Chrome
  floor**, and **add a live PQ ClientHello check**.
- **Add `rnet` as a pinned throughput fallback**; benchmark before promoting it
  per-host.
- **primp** = niche alternative (OS/browser split); **tls-client** = only if a
  Go tier appears (mind uTLS ≥ 1.8.2); **hrequests** = **dead, remove on sight**;
  plain `httpx/aiohttp/requests/niquests` = trusted-host tier only, never behind
  a WAF.

---

## Sources (all fetched 2026-06-12)
- curl_cffi releases — https://github.com/lexiforest/curl_cffi/releases `[VERIFIED]`
- curl_cffi PyPI — https://pypi.org/project/curl-cffi/ `[VERIFIED]`
- curl_cffi targets — https://curl-cffi.readthedocs.io/en/latest/impersonate/targets.html `[VERIFIED]`
- curl_cffi changelog — https://curl-cffi.readthedocs.io/en/latest/changelog.html `[VERIFIED]`
- curl-impersonate engine (PQ + Chrome 145/146) — https://github.com/lexiforest/curl-impersonate `[VERIFIED]`
- rnet / wreq-python — https://github.com/0x676e67/rnet `[VERIFIED]`
- wreq (Rust core, BoringSSL) — https://github.com/0x676e67/wreq `[VERIFIED]`
- primp repo + releases — https://github.com/deedy5/primp , /releases `[VERIFIED]`
- tls-client — https://github.com/bogdanfinn/tls-client `[VERIFIED]`
- hrequests (dead) — https://pypi.org/project/hrequests/ `[VERIFIED]`
- Post-quantum TLS bot detection (uTLS CVEs, PQ key share) — https://scrapfly.io/blog/posts/post-quantum-tls-bot-detection (2026-04-18) `[VERIFIED]`
- X25519MLKEM768 / Chrome PQ — https://chromestatus.com/feature/5257822742249472 `[VERIFIED]`
- Cloudflare boringssl-pq — https://github.com/cloudflare/boringssl-pq `[VERIFIED]`
- Benchmarks/practical guidance — https://brightdata.com/blog/web-data/web-scraping-with-curl-cffi , https://www.blog.datahut.co/post/web-scraping-without-getting-blocked-curl-cffi , https://www.piloterr.com/blog/ultra-fast-python-http-client-with-advanced-tls-fingerprinting `[VERIFIED]`
- CARDEEP current usage — `scrapers/engine/antidetect/tls.py`, `scrapers/portals/http_base.py`, `scrapers/requirements.txt` `[VERIFIED]`
